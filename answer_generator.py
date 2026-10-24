
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

#sends the question and relevant passeges to the groq language model to generate an answer
MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b",
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing from your .env file."
    )

client = Groq(api_key=api_key)


def generate_answer(question, passages):
    if not passages:
        return {
            "answer": (
                "I could not find a sufficiently relevant passage "
                "in this document to answer the question."
            ),
            "usage": None,
        }

    context = "\n\n".join(
        f"PDF page {item['page']}:\n{item['text']}"
        for item in passages
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer questions about an uploaded medical "
                    "document for educational purposes. Use only the "
                    "supplied passages for document-specific claims. "
                    "Do not invent test results, diagnoses, or sources. "
                    "If the passages do not answer the question, say so. "
                    "Explain medical terms clearly, distinguish general "
                    "information from personal medical advice, and "
                    "recommend a qualified healthcare professional for "
                    "personal medical decisions. Never claim to diagnose."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Retrieved document passages:\n{context}"
                ),
            },
        ],
        temperature=0.2,
        max_completion_tokens=400,
    )

    usage_data = getattr(response, "usage", None)

    usage = None
    if usage_data is not None:
        usage = {
            "prompt_tokens": getattr(
                usage_data, "prompt_tokens", None
            ),
            "completion_tokens": getattr(
                usage_data, "completion_tokens", None
            ),
            "total_tokens": getattr(
                usage_data, "total_tokens", None
            ),
        }

    return {
        "answer": response.choices[0].message.content or "",
        "usage": usage,
    }
