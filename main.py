import os
import json
import datetime
from extractor.processor import extract_relevant_sections

def main():
    print("🚀 Script started...")
    doc_folder = "input/docs"
    documents = [{"filename": f} for f in os.listdir(doc_folder) if f.endswith(".pdf")]

    persona = input("Enter the persona role (e.g., Travel Planner): ")
    job = input("Enter the job to be done (e.g., Plan a culinary tour): ")

    results = extract_relevant_sections(documents, doc_folder, persona, job)

    final_output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_sections": results["top_sections"],
        "subsection_analysis": results["subsections"]
    }

    os.makedirs("output", exist_ok=True)
    output_json_path = "output/challenge1b_output.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print(f"✅ Processing complete. Output saved to {output_json_path}")


if __name__ == "__main__":
    main()