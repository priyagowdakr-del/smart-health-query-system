
import fitz

PDF_PATH = "MedicalGuide.pdf"


def extract_pdf_text(pdf_path):
    documents = []

    with fitz.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                documents.append({
                    "page": page_number,
                    "text": text
                })

    return documents


if __name__ == "__main__":
    documents = extract_pdf_text(PDF_PATH)

    print("Pages containing text:", len(documents))

    for document in documents:
        print(f"\nPage {document['page']}:")
        print(document["text"][:500])
