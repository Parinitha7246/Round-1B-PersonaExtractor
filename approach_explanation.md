# Approach Explanation for Round 1B - Persona-Driven Document Intelligence

## Overview
This solution implements a lightweight, semantic-driven PDF analyzer that extracts and prioritizes relevant document sections based on a given persona and job-to-be-done. The system is optimized to run offline, within strict resource constraints, and generalizes across domains such as travel, research, education, and finance.

## Input Handling
The system accepts:
- A JSON file containing metadata (persona, job, list of documents)
- A folder containing 3–10 PDFs

The `main.py` orchestrates the execution pipeline by invoking the processing module with all inputs.

## Section Extraction Logic
1. **PDF Parsing (extractor/processor.py)**:
   - Each document is parsed using PyMuPDF.
   - Every page is analyzed for text blocks.
   - Blocks with bold fonts and large font sizes are treated as heading candidates.
   - These are grouped with the surrounding paragraph to form a candidate section.

2. **Section Representation**:
   - Each section includes: document name, page number, title (heading), and its associated content.

## Relevance Ranking
- Persona and job strings are concatenated into a single query.
- All sections and the query are embedded using the `all-MiniLM-L6-v2` SentenceTransformer model (~80MB).
- Cosine similarity is used to compute relevance between each section and the persona-job query.
- Top 5 sections are selected based on similarity score.

## Output Generation
The final JSON output contains:
- **Metadata**: timestamp, input docs, persona, and job
- **Extracted Sections**: top-5 ranked section titles with page number
- **Subsection Analysis**: associated refined body text of those sections

## Why This Works
- **Generalizable**: The semantic similarity method doesn’t rely on keywords or hardcoded rules, making it domain-agnostic.
- **Efficient**: Uses lightweight models under 100MB, ensuring fast inference (< 60s) and compatibility with <1GB constraints.
- **Modular**: Separation of concerns across `processor`, `reranker`, and `utils` allows easy extension and debugging.

## Constraints Handled
- ⚙️ CPU-only execution
- 🧠 Model size well under 1GB
- ⏱️ ~30 seconds runtime for 7 PDFs tested locally

## Possible Improvements
- Add fallback if heading structure is missing using sentence boundary detection.
- Incorporate extractive summarization using BART or T5 variants if model size permits.
- Add section deduplication or merging if documents are highly repetitive.

---
This approach ensures a robust and interpretable pipeline that adapts to any document-persona-job combination.
