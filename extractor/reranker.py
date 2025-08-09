from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def rank_sections(candidates, persona, job, top_n=5):
    """Ranks candidates using a generic, dynamic query that teaches intent."""
    query = f"""
    Analyze this request: A user with the role of a '{persona}' needs to complete the job: '{job}'.

    Your task is to find the most useful document sections to help them.
    A useful section will be a recipe or item that is highly relevant to the job.
    Evaluate each section based on how directly it helps the user achieve their goal.
    """

    if not candidates:
        return []

    query_embedding = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)

    for section in candidates:
        section['score'] = 0.0
        combined_text = section["title"] + ". " + section["content"]
        if combined_text.strip():
            doc_embedding = model.encode(combined_text, convert_to_tensor=True, normalize_embeddings=True)
            score = util.dot_score(query_embedding, doc_embedding).item()
            section['score'] = score

    candidates.sort(reverse=True, key=lambda x: x['score'])
    return candidates[:top_n]