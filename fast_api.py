
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from answer_generator import generate_answer


# 1. Create the FastAPI application
app = FastAPI(
    title="Smart Patient Health Query System",
    description="Ask questions using information from a medical PDF.",
    version="1.0.0"
)


# 2. Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 3. Define the request format
class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
        description="Question about the medical document"
    )


# 4. Welcome endpoint
@app.get("/")
def home():
    return {
        "message": "Smart Patient Health Query System API is running."
    }


# 5. Health-check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# 6. Question-answer endpoint
@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid question."
        )

    try:
        result = generate_answer(question)

        return {
            "question": question,
            "answer": result["answer"],
            "source": (
                f"MedicalGuide.pdf, page {result['page']}"
                if result["page"] is not None
                else None
            )
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer. "
                   "Check the backend terminal for details."
        ) from error
