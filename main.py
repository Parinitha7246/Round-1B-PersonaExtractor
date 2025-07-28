import os
import json
import datetime
from extractor.processor import extract_relevant_sections


def main():
    input_json_path = "input/challenge1b_input.json"
    output_json_path = "output/challenge1b_output.json"

    with open(input_json_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    documents = input_data["documents"]
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]

    doc_folder = "input/docs"
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
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print("✅ Processing complete. Output saved to", output_json_path)


if __name__ == "__main__":
    main()