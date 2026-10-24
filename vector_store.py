
from functools import lru_cache

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

#splits the text into chunks and creates embeddings and a FAISS index of 500 words with an overlap of 50 words between chunks  

@lru_cache(maxsize=1)
def get_embedding_model():
    # Load the model once per Python process.
    return SentenceTransformer(MODEL_NAME)


def create_chunks(documents, chunk_size=500, overlap=50):
    chunks = []

    for document in documents:
        text = document["text"]
        page = document["page"]

        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page": page,
                    "text": chunk_text,
                })

            if end >= len(text):
                break

            start = end - overlap

    if not chunks:
        raise ValueError("No searchable text chunks were created.")

    return chunks


def create_document_index(chunks):
    model = get_embedding_model()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    # Return the index and chunks instead of saving them to disk.
    return index, chunks
