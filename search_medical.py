
import numpy as np

from vector_store import get_embedding_model


def search_medical(index, chunks, question, top_k=5):
    if not question.strip() or index.ntotal == 0:
        return []

    model = get_embedding_model()

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    question_embedding = np.asarray(
        question_embedding,
        dtype="float32",
    )

    number_to_search = min(top_k, index.ntotal)
    scores, indices = index.search(
        question_embedding,
        number_to_search,
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        results.append({
            "page": chunks[idx]["page"],
            "text": chunks[idx]["text"],
            "similarity": float(score),
        })

    return results
