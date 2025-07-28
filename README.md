# Round-1B-PersonaExtractor

# Adobe Hackathon 2025 – Round 1B: Persona-Driven Document Intelligence

## 🧠 Problem Statement
Build an intelligent document analyzer that extracts and ranks the most relevant sections from a collection of PDF documents based on a provided persona and their job-to-be-done.

---

## 📁 Folder Structure
```
Round-1B-PersonaExtractor/
├── extractor/
│   ├── processor.py         # Parses PDFs and prepares candidate sections
│   ├── reranker.py          # Uses sentence-transformers to rank sections
│   ├── utils.py             # Utility functions for parsing and cleaning
├── input/
│   ├── challenge1b_input.json
│   └── docs/                # PDF files go here
├── output/
│   └── challenge1b_output.json
├── main.py
├── requirements.txt
├── Dockerfile
├── approach_explanation.md
└── README.md
```

---

## 🚀 How to Run Locally

### 1. Create Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Prepare Inputs
- Place all PDFs into `input/docs/`
- Provide metadata in `input/challenge1b_input.json`

### 4. Run
```bash
python main.py
```

### 5. Output
- Results saved in: `output/challenge1b_output.json`

---

## 🧪 Sample Input (challenge1b_input.json)
```json
{
  "documents": [
    {"filename": "South of France - Cuisine.pdf", "title": "..."},
    {"filename": "South of France - Cities.pdf", "title": "..."}
  ],
  "persona": {"role": "Travel Planner"},
  "job_to_be_done": {"task": "Plan a trip of 4 days for a group of 10 college friends."}
}
```

---

## 🧾 Output Format (challenge1b_output.json)
```json
{
  "metadata": {
    "input_documents": ["..."],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [
    {"document": "...", "section_title": "...", "importance_rank": 1, "page_number": 2}
  ],
  "subsection_analysis": [
    {"document": "...", "refined_text": "...", "page_number": 2}
  ]
}
```

---

## 🐳 Run with Docker
```bash
docker build -t persona-extractor .
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  persona-extractor
```

> On Windows PowerShell, use `^` instead of `\` for line continuation.

---

## ✅ Constraints Met
- Offline capable (no internet needed after model load)
- CPU only
- Model size < 1GB
- Runtime < 60s for 5–7 PDFs

---

## 🧩 Model Used
- `all-MiniLM-L6-v2` (~80MB): Fast semantic embedding model via `sentence-transformers`

---

## 📞 Contact
For questions, reach out via hackathon submission portal or contact your team lead.
