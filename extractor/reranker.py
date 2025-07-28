from sentence_transformers import SentenceTransformer, util

# Load a lightweight model (within 100MB)
model = SentenceTransformer("all-MiniLM-L6-v2")


def rank_sections(candidates, persona, job, top_n=5):
    query = persona + " - " + job
    query_embedding = model.encode(query, convert_to_tensor=True)

    scores = []
    for section in candidates:
        combined_text = section["title"] + ". " + section["content"]
        doc_embedding = model.encode(combined_text, convert_to_tensor=True)
        score = util.cos_sim(query_embedding, doc_embedding).item()
        scores.append((score, section))

    # Sort descending by similarity score
    scores.sort(reverse=True, key=lambda x: x[0])

    # Extract top_n sections
    top_sections = [entry[1] for entry in scores[:top_n]]
    return top_sections
