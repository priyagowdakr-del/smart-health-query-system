# Smart Health Query System

An AI-powered application that helps users understand medical information contained in PDF reports using natural language questions.

## Features
- Upload medical PDF documents.
- Extract readable text from PDFs.
- Validate documents using predefined medical keywords.
- Retrieve relevant passages using semantic search.
- Generate educational answers using the Groq API.
- Display source page numbers, retrieved passages, similarity scores, response time, and token usage.

## Technologies Used
- Python
- Streamlit
- FastAPI
- Groq API
- Sentence Transformers
- FAISS
- PyMuPDF
- NumPy
- REST API

## Project Workflow
1. Upload a medical PDF through the Streamlit interface.
2. FastAPI receives and processes the document.
3. PyMuPDF extracts text from the PDF.
4. The medical validator checks for relevant medical keywords.
5. Text is split into chunks and converted into embeddings.
6. FAISS retrieves passages relevant to the user's question.
7. The Groq language model generates an educational answer from the retrieved passages.
8. The answer and source information are displayed in the interface.

## Installation

Clone the repository:

```bash
git clone https://github.com/priyagowdakr-del/smart-health-query-system.git
cd smart-health-query-system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a local `.env` file and add your Groq API key:

```text
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the placeholder with your own key. **Never upload your actual `.env` file or API key to GitHub.**

## Run the Application

Start the FastAPI backend:

```bash
uvicorn fast_api:app --reload
```

Open a second terminal and start the Streamlit frontend:

```bash
streamlit run app.py
```

## Disclaimer
This project is for educational and informational purposes only. It does not replace professional medical advice, diagnosis, or treatment.