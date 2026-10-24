
import base64
import time
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"
#user uploads the medical pdf or enters a question 
# == finally rerturns the answer,source pages, retrieved passages, and token usage for display
st.set_page_config(
    page_title="Smart Health Query System",
    page_icon="🩺",
    layout="centered",
)

st.markdown("""
<style>
.stApp {
    background: #f4f8fc;
}
.block-container {
    max-width: 900px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(135deg, #102a43, #087e8b);
    color: white;
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 20px;
}
.hero h1 {
    color: white;
}
.card {
    background: white;
    border: 1px solid #dce6f0;
    border-radius: 14px;
    padding: 20px;
    margin: 14px 0;
}
</style>
""", unsafe_allow_html=True)

if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "document_name" not in st.session_state:
    st.session_state.document_name = None
if "answer_data" not in st.session_state:
    st.session_state.answer_data = None

st.markdown("""
<div class="hero">
    <h1>🩺 Smart Health Query System</h1>
    <p>Upload a medical PDF, verify its content, and ask questions
    about the information in your report.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational information only. This application does not provide "
    "a medical diagnosis or replace professional medical advice."
)

# ---------------- UPLOAD ----------------
st.subheader("1. Upload your medical PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF medical report",
    type=["pdf"],
    help="Maximum size: 10 MB. Scanned image-only PDFs are not supported.",
)

if uploaded_file is not None:
    st.caption(
        f"Selected file: {uploaded_file.name} "
        f"({uploaded_file.size / 1024:.1f} KB)"
    )

    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("The PDF must be 10 MB or smaller.")

    elif st.button("Verify medical document", type="primary"):
        try:
            # Clear the previous document before replacing it.
            old_id = st.session_state.document_id
            if old_id:
                try:
                    requests.delete(
                        f"{API_URL}/documents/{old_id}",
                        timeout=10,
                    )
                except requests.RequestException:
                    pass

            st.session_state.document_id = None
            st.session_state.document_name = None
            st.session_state.answer_data = None

            pdf_bytes = uploaded_file.getvalue()
            encoded_pdf = base64.b64encode(pdf_bytes).decode("ascii")

            with st.spinner("Validating and processing your PDF..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    json={
                        "filename": uploaded_file.name,
                        "pdf_base64": encoded_pdf,
                    },
                    timeout=180,
                )

            if response.status_code != 200:
                try:
                    detail = response.json().get(
                        "detail", "Document validation failed."
                    )
                except ValueError:
                    detail = "Document validation failed."

                st.error(detail)

            else:
                result = response.json()

                st.session_state.document_id = result["document_id"]
                st.session_state.document_name = uploaded_file.name

                st.success(
                    "Medical document verified. "
                    "You can now ask questions about this report."
                )

                col1, col2 = st.columns(2)
                col1.metric("Pages extracted", result["pages_extracted"])
                col2.metric("Text chunks created", result["chunks_created"])

        except requests.RequestException as exc:
            st.error(
                "Could not connect to the backend. "
                "Make sure FastAPI is running."
            )
            st.caption(str(exc))

# ---------------- QUESTIONS ----------------
if st.session_state.document_id:
    st.divider()
    st.subheader("2. Ask about your report")

    st.caption(f"Current document: {st.session_state.document_name}")

    with st.form("question_form"):
        question = st.text_area(
            "Your question",
            placeholder="Example: What does this report say about haemoglobin?",
            max_chars=1000,
            height=100,
        )
        submitted = st.form_submit_button(
            "🔍 Get Answer",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        question = question.strip()

        if not question:
            st.warning("Please enter a question.")

        else:
            try:
                start = time.perf_counter()

                with st.spinner("Searching your report and generating an answer..."):
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={
                            "document_id": st.session_state.document_id,
                            "question": question,
                        },
                        timeout=120,
                    )

                elapsed = time.perf_counter() - start

                if response.status_code != 200:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text

                    st.error(f"Request failed: {detail}")

                else:
                    st.session_state.answer_data = response.json()
                    st.session_state.answer_data["_elapsed"] = elapsed

            except requests.RequestException as exc:
                st.error("Could not connect to FastAPI.")
                st.caption(str(exc))

    data = st.session_state.answer_data

    if data:
        st.divider()
        st.subheader("✨ Answer")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(data.get("answer", "No answer returned."))
        st.markdown("</div>", unsafe_allow_html=True)

        pages = data.get("source_pages", [])

        if pages:
            st.markdown(
                "**Source pages:** "
                + ", ".join(str(page) for page in pages)
            )
        else:
            st.caption("No supporting source pages were returned.")

        st.subheader("📊 AI performance")

        usage = data.get("usage") or {}
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Input tokens",
            usage.get("prompt_tokens")
            if usage.get("prompt_tokens") is not None else "N/A",
        )
        c2.metric(
            "Output tokens",
            usage.get("completion_tokens")
            if usage.get("completion_tokens") is not None else "N/A",
        )
        c3.metric(
            "Total tokens",
            usage.get("total_tokens")
            if usage.get("total_tokens") is not None else "N/A",
        )

        st.metric(
            "Response time",
            f"{data.get('_elapsed', 0):.2f} seconds",
        )

        st.subheader("🎯 Retrieved passages")

        passages = data.get("retrieved_passages", [])

        if passages:
            for number, passage in enumerate(passages, start=1):
                score = passage.get("similarity", 0.0)

                with st.expander(
                    f"Passage {number} · Page {passage['page']} · "
                    f"Similarity {score:.3f}"
                ):
                    st.progress(max(0.0, min(1.0, score)))
                    st.write(passage["text"])
        else:
            st.caption(
                "No sufficiently relevant passages were found in the report."
            )

        st.caption(
            "Similarity indicates text relevance, not medical accuracy. "
            "Check important results with a qualified healthcare professional."
        )

    # ---------------- CLEAR DOCUMENT ----------------
    st.divider()

    if st.button("🗑️ Clear uploaded document"):
        document_id = st.session_state.document_id

        try:
            requests.delete(
                f"{API_URL}/documents/{document_id}",
                timeout=10,
            )
        except requests.RequestException:
            st.warning(
                "The backend could not confirm cleanup. "
                "The document will expire from its in-memory registry "
                "after the configured timeout is checked."
            )

        st.session_state.document_id = None
        st.session_state.document_name = None
        st.session_state.answer_data = None
        st.rerun()

st.markdown("---")
st.caption(
    "Smart Patient Health Query System · Temporary document processing · "
    "For educational use only"
)
