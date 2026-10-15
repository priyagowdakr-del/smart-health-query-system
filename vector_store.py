
import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer
from pdf_reader import extract_pdf_text


# 1. Configuration
PDF_PATH = "MedicalGuide.pdf"
INDEX_PATH = "medical_index.faiss"
CHUNKS_PATH = "medical_chunks.pkl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# 2. Load the embedding model
print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)


# 3. Split extracted PDF text into chunks
def create_chunks(documents, chunk_size=500, overlap=50):
    chunks = []

    for document in documents:
        text = document["text"]
        page_number = document["page"]

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page": page_number,
                    "text": chunk_text
                })

            # Move forward while retaining some overlap
            start += chunk_size - overlap

    return chunks


# 4. Convert chunks into embeddings
def create_embeddings(chunks):
    if not chunks:
        return np.empty((0, 384), dtype="float32")

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return np.asarray(embeddings, dtype="float32")


# 5. Create and save the FAISS index
def create_faiss_index(embeddings):
    if len(embeddings) == 0:
        raise ValueError(
            "No embeddings were generated. Check your PDF."
        )

    dimension = embeddings.shape[1]

    # Inner product on normalized vectors gives cosine similarity
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    return index


# 6. Save text chunks and their page numbers
def save_chunks(chunks):
    with open(CHUNKS_PATH, "wb") as file:
        pickle.dump(chunks, file)

    print(f"Chunks saved to {CHUNKS_PATH}")


# 7. Main execution
def main():
    print("\nExtracting text from PDF...")

    documents = extract_pdf_text(PDF_PATH)

    if not documents:
        print("No readable text found in the PDF.")
        return

    print("Pages containing text:", len(documents))

    print("\nCreating text chunks...")

    chunks = create_chunks(documents)

    if not chunks:
        print("No text chunks were created.")
        return

    print("Total chunks:", len(chunks))

    print("\nGenerating embeddings...")

    embeddings = create_embeddings(chunks)

    print("Embedding shape:", embeddings.shape)

    print("\nCreating FAISS index...")

    index = create_faiss_index(embeddings)

    save_chunks(chunks)

    print("\nProcessing completed successfully!")
    print("Vectors stored in FAISS:", index.ntotal)
    print("FAISS index:", INDEX_PATH)
    print("Chunk data:", CHUNKS_PATH)


if __name__ == "__main__":
    main()
