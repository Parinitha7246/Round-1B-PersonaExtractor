import os
import fitz
from extractor.reranker import rank_sections
from extractor.utils import clean_text, chunk_page_text


def extract_relevant_sections(documents, doc_folder, persona, job):
    section_candidates = []

    for doc in documents:
        file_path = os.path.join(doc_folder, doc["filename"])
        if not os.path.exists(file_path):
            print(f"⚠️ Missing: {file_path}")
            continue

        pdf = fitz.open(file_path)

        for page_num, page in enumerate(pdf, start=1):
            blocks = chunk_page_text(page)
            for title, content in blocks:
                section_candidates.append({
                    "document": doc["filename"],
                    "page": page_num,
                    "title": title,
                    "content": content
                })

    # Rank all sections using semantic similarity
    top_sections = rank_sections(section_candidates, persona, job, top_n=5)

    # Extract top N sections with details
    extracted_sections = []
    subsection_analysis = []

    for rank, sec in enumerate(top_sections, start=1):
        extracted_sections.append({
            "document": sec["document"],
            "section_title": sec["title"],
            "importance_rank": rank,
            "page_number": sec["page"]
        })

        subsection_analysis.append({
            "document": sec["document"],
            "refined_text": sec["content"],
            "page_number": sec["page"]
        })

    return {
        "top_sections": extracted_sections,
        "subsections": subsection_analysis
    }
