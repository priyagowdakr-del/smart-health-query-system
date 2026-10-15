# Smart Patient Health Query System

An AI-powered PDF question-answering application built with
Python, Sentence Transformers, FAISS, Groq, FastAPI, and Streamlit.

## Overview

The system answers questions using information retrieved from
a pre-provided medical PDF. It extracts PDF text, creates
embeddings, retrieves relevant passages using FAISS, and uses
a language model to generate a readable answer.

## Technologies

- Python
- PyMuPDF
- Sentence Transformers
- FAISS
- Groq API
- FastAPI
- REST API and JSON
- Streamlit
- NumPy

## Architecture

Medical PDF
→ Text Extraction
→ Chunking and Embeddings
→ FAISS Semantic Search
→ Groq LLM
→ FastAPI
→ Streamlit Interface

## Project Files

- `pdf_reader.py` - Extracts text and page numbers.
- `vector_store.py` - Creates chunks, embeddings, and the FAISS index.
- `search_medical.py` - Retrieves relevant passages.
- `answer_generator.py` - Generates answers using Groq.
- `fast_api.py` - Provides REST API endpoints.
- `app.py` - Provides the Streamlit frontend.

## Setup

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   `pip install -r requirements.txt`

4. Place your permitted medical PDF in the project folder
   and name it `MedicalGuide.pdf`.
5. Create a `.env` file and add:

   `GROQ_API_KEY=your_groq_api_key`

6. Build the vector index:

   `python vector_store.py`

7. Start FastAPI:

   `python -m uvicorn fast_api:app --reload`

8. In another terminal, start Streamlit:

   `python -m streamlit run app.py`

9. Open `http://localhost:8501`.

## Important Notes

- Keep your API key private.
- Do not upload confidential or copyrighted documents
  unless you have permission.
- This is an educational document assistant, not a
  medical diagnostic or treatment system.
- Verify generated answers against the source document.
