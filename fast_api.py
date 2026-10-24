
import base64
import binascii
import time
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from pdf_reader import extract_pdf_text, MAX_PDF_SIZE
from medical_validator import validate_medical_document
from vector_store import create_chunks, create_document_index
from search_medical import search_medical
from answer_generator import generate_answer

app = FastAPI(title="MediLens Medical Document API")

# Temporary, process-local memory only.
# Never write uploaded reports or their indexes to disk.
documents = {}

DOCUMENT_TTL_SECONDS = 30 * 60  # 30 minutes


class UploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    pdf_base64: str = Field(min_length=1, max_length=14_000_000)


class QuestionRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=1000)


def cleanup_expired_documents():
    now = time.time()
    expired = [
        doc_id
        for doc_id, record in documents.items()
        if now - record["created_at"] > DOCUMENT_TTL_SECONDS
    ]

    for doc_id in expired:
        documents.pop(doc_id, None)


@app.get("/")
def home():
    return {"message": "MediLens Medical Document API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
def upload_document(request: UploadRequest):
    cleanup_expired_documents()

    if not request.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted.",
        )

    try:
        pdf_bytes = base64.b64decode(
            request.pdf_base64,
            validate=True,
        )
    except (binascii.Error, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF data is invalid.",
        )

    if len(pdf_bytes) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 10 MB or smaller.",
        )

    try:
        page_documents = extract_pdf_text(pdf_bytes)
        validation = validate_medical_document(page_documents)

        if not validation["is_medical"]:
            raise HTTPException(
                status_code=422,
                detail=validation["message"],
            )

        chunks = create_chunks(page_documents)
        index, chunks = create_document_index(chunks)

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The document could not be processed.",
        )

    # The original PDF bytes are not stored in the registry.
    document_id = uuid.uuid4().hex

    documents[document_id] = {
        "index": index,
        "chunks": chunks,
        "created_at": time.time(),
        "matched_categories": validation["matched_categories"],
    }

    return {
        "document_id": document_id,
        "message": validation["message"],
        "pages_extracted": len(page_documents),
        "chunks_created": len(chunks),
        "expires_in_minutes": 30,
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    cleanup_expired_documents()

    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    record = documents.get(request.document_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="This document has expired or was cleared. Upload it again.",
        )

    try:
        passages = search_medical(
            record["index"],
            record["chunks"],
            question,
            top_k=5,
        )

        # Avoid sending clearly unrelated passages to the LLM.
        # This threshold is a heuristic and may need tuning.
        relevant_passages = [
            item for item in passages
            if item["similarity"] >= 0.30
        ]

        generated = generate_answer(
            question,
            relevant_passages,
        )

        pages = sorted({
            item["page"] for item in relevant_passages
        })

        return {
            "question": question,
            "answer": generated["answer"],
            "source_pages": pages,
            "retrieved_passages": relevant_passages,
            "usage": generated["usage"],
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Answer generation failed. Check the backend logs.",
        )


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    existed = documents.pop(document_id, None) is not None

    return {
        "deleted": existed,
        "message": (
            "Document cleared."
            if existed
            else "Document was already cleared or expired."
        ),
    }
