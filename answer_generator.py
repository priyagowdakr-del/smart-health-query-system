
import os

from dotenv import load_dotenv
from groq import Groq
from search_medical import search_medical


# 1. Load environment variables from .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Check your .env file."
    )


# 2. Create the Groq client
client = Groq(api_key=api_key)

MODEL_NAME = "openai/gpt-oss-20b"


# 3. Generate an answer using retrieved PDF evidence
def generate_answer(question):

    # Retrieve the closest passage from the PDF
    results = search_medical(question, top_k=1)

    if not results:
        return {
            "answer": (
                "The provided document does not contain "
                "sufficient information to answer this question."
            ),
            "page": None
        }

    result = results[0]

    # Avoid generating an answer from a weak match
    if result["similarity"] < 0.40:
        return {
            "answer": (
                "The provided document does not contain "
                "sufficient information to answer this question."
            ),
            "page": None
     }

    context = result["text"]
    page_number = result["page"]

    # Ask the LLM to answer using only the retrieved passage
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer questions using only the "
                    "provided medical document passage. "
                    "Do not use outside knowledge or invent "
                    "facts. If the passage does not contain "
                    "enough information, say that the provided "
                    "document does not contain sufficient "
                    "information to answer the question. "
                    "Provide educational information only, "
                    "not a diagnosis or personalized treatment."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Document passage:\n{context}\n\n"
                    "Give one clear, concise answer based "
                    "only on this passage."
                )
            }
        ],
        temperature=0.2,
        max_completion_tokens=300
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "page": page_number
    }


# 4. Test the answer generator
if __name__ == "__main__":

    print("\nSmart Patient Health Query System")
    print("Type 'exit' to stop.")

    while True:
        question = input("\nAsk a question: ").strip()

        if question.lower() == "exit":
            print("Program stopped.")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            result = generate_answer(question)

            print("\nAnswer:")
            print(result["answer"])

            if result["page"] is not None:
                print(f"\nSource: MedicalGuide.pdf, page "
                      f"{result['page']}")

        except Exception as error:
            print(f"An error occurred: {error}")
