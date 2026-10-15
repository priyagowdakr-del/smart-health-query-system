
import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer


# 1. File paths
INDEX_PATH = "medical_index.faiss"
CHUNKS_PATH = "medical_chunks.pkl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# 2. Load the embedding model
print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)


# 3. Load the saved FAISS index
index = faiss.read_index(INDEX_PATH)


# 4. Load the saved text chunks
with open(CHUNKS_PATH, "rb") as file:
    chunks = pickle.load(file)


# 5. Search for relevant medical passages
def search_medical(question, top_k=5):
    if not question.strip():
        return []

    # Convert the question into an embedding
    question_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    question_embedding = np.asarray(
        question_embedding,
        dtype="float32"
    )

    # Retrieve the most similar chunks
    number_to_search = min(top_k, index.ntotal)

    scores, indices = index.search(
        question_embedding,
        number_to_search
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        results.append({
            "page": chunks[idx]["page"],
            "text": chunks[idx]["text"],
            "similarity": float(score)
        })

    return results


# 6. Test the search function
if __name__ == "__main__":
    while True:
        question = input(
            "\nAsk a question about the medical PDF "
            "(or type 'exit' to stop): "
        )

        if question.strip().lower() == "exit":
            print("Search stopped.")
            break

        results = search_medical(question)

        if not results:
            print("No matching passages were found.")
            continue

        print("\nRelevant passages:")

        for number, result in enumerate(results, start=1):
            print(f"\nResult {number}")
            print(f"Page: {result['page']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Text: {result['text']}")
