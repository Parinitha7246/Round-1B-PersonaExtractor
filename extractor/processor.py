import os
import fitz
from extractor.reranker import rank_sections
from extractor.utils import chunk_page_text


def extract_relevant_sections(documents, doc_folder, persona, job):
    document_champions = []

    # STAGE 1: Find the single best section (champion) within each document.
    for doc in documents:
        file_path = os.path.join(doc_folder, doc["filename"])
        if not os.path.exists(file_path):
            continue

        current_doc_candidates = []
        pdf = fitz.open(file_path)
        for page_num, page in enumerate(pdf, start=1):
            for title, content in chunk_page_text(page):
                current_doc_candidates.append({
                    "document": doc["filename"], "page": page_num,
                    "title": title, "content": content
                })

        if current_doc_candidates:
            doc_champion_list = rank_sections(current_doc_candidates, persona, job, top_n=1)
            if doc_champion_list:
                document_champions.append(doc_champion_list[0])

    # STAGE 2: Rank the champions against each other to get the final list.
    final_top_sections = rank_sections(document_champions, persona, job, top_n=5)

    # Build the final JSON output.
    extracted_sections, subsection_analysis = [], []
    for rank, sec in enumerate(final_top_sections, start=1):
        extracted_sections.append({
            "document": sec["document"], "section_title": sec["title"],
            "importance_rank": rank, "page_number": sec["page"]
        })
        subsection_analysis.append({
            "document": sec["document"], "refined_text": sec["content"],
            "page_number": sec["page"]
        })

    return {"top_sections": extracted_sections, "subsections": subsection_analysis}