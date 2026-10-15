
import streamlit as st
import requests


# 1. Page configuration
st.set_page_config(
    page_title="Smart Patient Health Query System",
    page_icon="🩺",
    layout="centered"
)


# 2. FastAPI backend URL
API_URL = "http://127.0.0.1:8000/ask"


# 3. Page heading
st.title("🩺 Smart Patient Health Query System")

st.write(
    "Ask questions about the medical information "
    "stored in our PDF document."
)

st.info(
    "This application provides educational information "
    "from the supplied document. It does not replace "
    "professional medical advice."
)


# 4. Question input
question = st.text_area(
    "Enter your question",
    placeholder="Example: What does the document say about insomnia?",
    height=100
)


# 5. Submit question
if st.button("Get Answer", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Searching the document and generating an answer..."):

                response = requests.post(
                    API_URL,
                    json={"question": question.strip()},
                    timeout=120
                )

                response.raise_for_status()
                data = response.json()

            # 6. Display answer
            st.subheader("Answer")
            st.write(data["answer"])

            # 7. Display source page
            if data.get("source"):
                st.caption(f"Source: {data['source']}")

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the backend. "
                "Please start FastAPI first."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The request took too long. "
                "Please try again."
            )

        except requests.exceptions.HTTPError:
            st.error(
                "The backend returned an error. "
                "Check the FastAPI terminal for details."
            )

        except (ValueError, KeyError):
            st.error(
                "The backend returned an unexpected response."
            )
