
import re
#checks if the uploaded document is a medical document based on the presence of medical terms
#  in the text especuially for keyword related to users quesry as well as pdf text mainly medical keyword
MEDICAL_TERMS = {
    "laboratory": [
        "hemoglobin", "haemoglobin", "platelet",
        "blood test", "white blood cell", "red blood cell",
        "glucose", "creatinine", "cholesterol",
        "reference range", "laboratory report",
    ],
    "clinical": [
        "patient", "clinical history", "diagnosis",
        "symptoms", "medical history", "treatment",
        "clinical findings", "doctor", "physician",
    ],
    "hospital": [
        "discharge summary", "hospital", "admission",
        "prescription", "medication", "dosage",
        "radiology report", "impression",
        "medical report", "investigation report",
    ],
}


def validate_medical_document(documents):
    """
    Return a validation result based on medical terminology.

    This is a heuristic, not a medically reliable classifier.
    """

    text = " ".join(
        document["text"] for document in documents
    ).lower()

    matched_categories = []
    matched_terms = []

    for category, terms in MEDICAL_TERMS.items():
        category_matches = [
            term for term in terms
            if re.search(
                r"(?<!\w)" + re.escape(term) + r"(?!\w)",
                text,
            )
        ]

        if category_matches:
            matched_categories.append(category)
            matched_terms.extend(category_matches)

    # Require indicators from at least two different categories.
    # This reduces false acceptance but cannot eliminate it.
    is_medical = (
        len(matched_categories) >= 2
        and len(matched_terms) >= 3
    )

    if is_medical:
        message = (
            "Medical document verified. "
            "You can now ask questions about this report."
        )
    else:
        message = (
            "We could not verify this as a medical document. "
            "Please upload a readable medical report."
        )

    return {
        "is_medical": is_medical,
        "message": message,
        "matched_categories": matched_categories,
    }
