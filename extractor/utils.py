import re
import fitz

def clean_text(text):
    """
    Robust cleaning of text: normalizes whitespace, removes common line-starting
    bullet/list indicators (like '•', 'o', '§', '●'), and standardizes common OCR ligatures.
    """
    cleaned = re.sub(r'\s+', ' ', text).strip()
    cleaned = re.sub(r"^[•oO§●]\s*", "", cleaned) # Remove common leading bullet/list symbols
    cleaned = cleaned.replace("ﬁ", "fi").replace("ﬀ", "ff").replace("ﬂ", "fl") # Handle common OCR ligatures
    return cleaned

def get_block_attributes(block):
    """Extracts cleaned text, dominant font size, and bold status from a fitz text block."""
    full_text_parts = []
    dominant_size = 0.0
    is_bold = False

    if block.get('type') == 0 and block.get('lines'): # Only process actual text blocks with lines
        try:
            # Get info from the first span of the first line (common for block-level style)
            first_span = block['lines'][0]['spans'][0]
            dominant_size = first_span.get('size', 0.0)
            if first_span.get('font', '').lower() and ('bold' in first_span['font'].lower()):
                is_bold = True
            
            # Aggregate text from all spans in the block
            for line in block['lines']:
                for span in line['spans']:
                    full_text_parts.append(span.get('text', ''))
        except (KeyError, IndexError):
            # Fallback if block structure is not as expected, default attributes
            pass
        
        cleaned_text = clean_text("".join(full_text_parts))
        return cleaned_text, dominant_size, is_bold
        
    return None, 0.0, False # Return None text if block isn't a text block or has no text


def is_potential_section_heading(text_content, text_size, is_bold_font, body_text_baseline_size):
    """
    Generic heuristic to identify if a block's text is likely a major section heading.
    Applies stricter rules to minimize false positives ("Overview", "side.", list items).
    """
    if not text_content: # Must have content
        return False
        
    # Rule 1: Text length heuristics for conciseness
    words = text_content.split()
    if len(words) == 0: return False # Should be caught by not text_content, but double check
    if len(words) > 8: # Most headings are short. 8-word max, adjust based on observed PDFs.
        return False

    # Rule 2: Punctuation (headings rarely end in full stops, unless it's "Table of Contents.")
    if text_content.endswith('.') and len(words) > 3: # "Introduction." vs "Page." vs "Summary."
        return False
    if text_content.endswith(':') or text_content.endswith(';'): # Often sub-headings (e.g., "Ingredients:")
        return False

    # Rule 3: Common list item or internal heading exclusion
    lower_text = text_content.lower()
    if any(keyword in lower_text for keyword in [
        "ingredients", "instructions", "prepare", "cook", "serve", "conclusion",
        "introduction", "overview", "note", "summary", "references", "table of contents",
        "author", "abstract", "contents", "index", "disclaimer", "page",
        "description", "steps", "preparation" # Added more exclusions relevant to recipes/docs
    ]):
        return False
    
    # Rule 4: Prominence (font size and bold status are key)
    # This dynamically adapts based on the *average body text size* of the page.
    # Significant size jump or a combination of bold and moderate size jump is critical.
    
    # A substantial font size jump often signifies a new heading.
    if text_size > body_text_baseline_size + 3.0: # 3+ points larger is significant
        return True
    
    # Or, if it's bold and slightly larger than the baseline (catching bold subtitles/sections)
    if is_bold_font and text_size > body_text_baseline_size + 1.0: # Bold and 1+ pt larger
        return True
        
    # For very short titles (1-2 words), sometimes boldness is enough, even if not huge size jump,
    # as long as it's not a bullet and stands alone visually.
    if is_bold_font and len(words) <= 3 and text_size >= (body_text_baseline_size - 1.0):
        # A single bold word that's not significantly smaller than body text
        return True

    return False


def chunk_page_text(page):
    """
    Parses a PDF page to extract (section title, content) chunks.
    This parser:
    1.  Determines a dynamic 'body text' baseline font size for better heading detection.
    2.  Statefully collects content under a determined heading.
    3.  Filters out empty/junk blocks aggressively.
    """
    blocks = page.get_text("dict")["blocks"] # Use basic dict output for max compatibility
    
    results = []
    current_content_segments = []
    current_section_title = "Document Introduction/Misc." # Neutral, generic default for start of document
    
    # Dynamically determine body_text_baseline_size for this specific page.
    # We collect sizes from blocks that are likely NOT titles (e.g., medium font range, >1 line).
    font_size_candidates = []
    for block in blocks:
        if block.get('type') == 0 and block.get('lines'):
            lines_in_block = block.get('lines', [])
            if len(lines_in_block) > 1: # Consider blocks with multiple lines for body text size
                try:
                    first_span_size = lines_in_block[0]['spans'][0].get('size')
                    if 8.0 <= first_span_size <= 13.0: # Typical body text range
                        font_size_candidates.append(first_span_size)
                except (KeyError, IndexError):
                    pass
    
    # Baseline for body text size: the median or mode of likely body text sizes.
    body_text_baseline = 10.0 # Default fallback if no clear body text detected
    if font_size_candidates:
        # A robust way to get a baseline size, often mode is best but median works for small lists
        from collections import Counter
        most_common_sizes = Counter(font_size_candidates).most_common(1)
        if most_common_sizes:
            body_text_baseline = most_common_sizes[0][0]
        else: # Fallback to mean if no mode
            body_text_baseline = sum(font_size_candidates) / len(font_size_candidates)

    last_block_font_size_processed = body_text_baseline # Start comparison from the baseline

    def commit_section():
        """Helper to finalize and add the current section to results."""
        if current_content_segments: # Only commit if there's text accumulated
            final_content = " ".join(current_content_segments).strip()
            if final_content: # Ensure content is not empty after joining/cleaning
                results.append((current_section_title, final_content))
            current_content_segments.clear() # Reset for next section

    for block_num, block in enumerate(blocks):
        # Safely extract text, size, and bold status for the current block
        text_content, size_of_block, bold_status = get_block_attributes(block)
        
        # Skip blocks with no extractable or meaningful text
        if text_content is None or not text_content.strip():
            continue

        # Determine if this block is a new heading based on robust heuristics
        is_heading_block = is_potential_section_heading(text_content, size_of_block, bold_status, body_text_baseline)
        
        # Additional checks to prevent splitting within an instruction list (e.g., ingredient 1, 2, 3...)
        # This checks if the current block looks like a list item following a prior content block
        if not is_heading_block and re.match(r"^(\d+\.|[•oO])\s", text_content.strip()) and current_content_segments:
            # If it's a list item-looking text and not identified as a heading, and follows content,
            # it likely belongs to the current content section.
            pass # Keep it as content, don't trigger new section
        elif is_heading_block:
            # Found a new heading: commit the previous section and start a new one.
            commit_section()
            current_section_title = text_content # New heading is the new title
        
        # Always append current block's content (if not a heading or if it's the *first* block heading after commit)
        # Handle cases where heading is also content in our logic, as get_block_attributes handles joining.
        current_content_segments.append(text_content)
        
        # Update baseline if a clear body text size is observed, or track general block size flow.
        if 8.0 <= size_of_block <= 13.0 and not bold_status and is_heading_block is False: # It's typical content, update baseline
             body_text_baseline = size_of_block # Use actual content size for better dynamic adjustment

    # After iterating all blocks, commit the final section.
    commit_section()
    
    # Post-processing: If only one section exists and it's generic, try to find a better title if the document starts with one.
    if len(results) == 1 and results[0][0] == "Document Introduction/Misc." and blocks:
        for i, block in enumerate(blocks):
            if block.get('type') == 0 and block.get('lines'):
                text, size, bold = get_block_attributes(block)
                # Try a broader heading detection for the *very first* actual title, allowing for banners/overall titles.
                if text and size > 15.0 and len(text.split()) < 15: # Broad heuristic for first page major title
                    results[0] = (text, results[0][1]) # Replace the generic title
                    break
    
    return results