import re
import fitz

def clean_text(text):
    """Remove extra whitespace and control characters."""
    return re.sub(r'\s+', ' ', text.strip())


def chunk_page_text(page):
    """
    Extract heading + paragraph text blocks from a PDF page.
    Returns a list of (title, content) pairs.
    """
    blocks = page.get_text("dict")["blocks"]
    results = []

    for block in blocks:
        if block['type'] != 0:
            continue

        lines = block.get("lines", [])
        if not lines:
            continue

        spans = [span for line in lines for span in line.get("spans", []) if span.get("text")]
        if not spans:
            continue

        title_candidate = spans[0]["text"]
        title_size = spans[0]["size"]
        bold_font = "bold" in spans[0]["font"].lower() or "black" in spans[0]["font"].lower()

        # Use heuristics: large, bold text as section title
        if title_size > 11 and bold_font and len(title_candidate.split()) < 12:
            title = clean_text(title_candidate)
            content = " ".join([clean_text(span["text"]) for span in spans[1:]])
            results.append((title, content))

    return results
