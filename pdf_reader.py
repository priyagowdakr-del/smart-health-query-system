
import fitz

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PDF_PAGES = 500

#extracts readable text and page numbers from PDF bytes and raises errors for invalid or unsupported PDFs
def extract_pdf_text(pdf_bytes: bytes):
    """Extract readable text and page numbers from PDF bytes."""

    if not pdf_bytes:
        raise ValueError("The uploaded file is empty.")

    if len(pdf_bytes) > MAX_PDF_SIZE:
        raise ValueError("PDF must be 10 MB or smaller.")

    # Basic signature check; this is not sufficient by itself
    # to prove that a file is a valid or safe PDF.
    if not pdf_bytes.lstrip().startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    documents = []

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            if pdf.page_count == 0:
                raise ValueError("The PDF contains no pages.")

            if pdf.page_count > MAX_PDF_PAGES:
                raise ValueError("PDF must contain 100 pages or fewer.")

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                if text:
                    documents.append({
                        "page": page_number,
                        "text": text,
                    })

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "The PDF could not be opened. Please upload a readable PDF."
        ) from exc

    combined_text = "\n".join(
        document["text"] for document in documents
    )

    if len(combined_text) < 300:
        raise ValueError(
            "Not enough readable text was found. "
            "Please upload a text-readable medical PDF. "
            "Scanned image-only PDFs are not supported in this version."
        )

    return documents
