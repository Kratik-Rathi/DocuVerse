import streamlit as st
import hashlib
import os

from document_processor import get_files_text
from text_processor import get_vectorstore, get_text_chunks
from model import initialize_model
from conversation import (
    handle_user_input,
    generate_summary,
    update_summary_format,
    get_conversation_chain
)

# 🔹 Toggle Milvus (OFF for Streamlit)
USE_MILVUS = os.getenv("USE_MILVUS", "false").lower() == "true"


# -------------------------------
# 🔹 File Hash Helpers
# -------------------------------
def get_file_hashes(files):
    hashes = []
    for f in files:
        content = f.read()
        hashes.append(hashlib.md5(content).hexdigest())
        f.seek(0)
    return hashes


def files_changed(new_files, prev_hashes):
    if not new_files or not prev_hashes:
        return True
    return get_file_hashes(new_files) != prev_hashes


# -------------------------------
# 🔹 Main App
# -------------------------------
def main():
    st.set_page_config(page_title="Ask your Document", layout="wide")
    st.title("Ask Your Document")

    # -------------------------------
    # 🔹 Session State Init
    # -------------------------------
    defaults = {
        "conversation": None,
        "chat_history": [],
        "processComplete": False,
        "summary_format": "Paragraph",
        "summary_format_changed": False,
        "summary": None,
        "is_processing": False,
        "uploaded_files": None,
        "prev_file_hashes": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "model" not in st.session_state:
        initialize_model()

    # -------------------------------
    # 🔹 Upload UI
    # -------------------------------
    if not st.session_state.processComplete:
        st.write("## Upload your file")
        uploaded_files = st.file_uploader(
            "Upload PDF, DOCX, TXT, XLSX",
            type=["pdf", "docx", "txt", "xlsx"],
            accept_multiple_files=True,
        )
        process = st.button("Process")
    else:
        with st.sidebar:
            st.write("## Upload more files")
            uploaded_files = st.file_uploader(
                "Upload PDF, DOCX, TXT, XLSX",
                type=["pdf", "docx", "txt", "xlsx"],
                accept_multiple_files=True,
            )
            process = st.button("Process")

    # -------------------------------
    # 🔹 Process Files
    # -------------------------------
    if process:
        if uploaded_files:
            current_hashes = get_file_hashes(uploaded_files)

            if files_changed(uploaded_files, st.session_state.prev_file_hashes):
                st.session_state.prev_file_hashes = current_hashes
                st.session_state.chat_history = []
                st.session_state.conversation = None
                st.session_state.summary = None
                st.session_state.processComplete = False
                st.session_state.is_processing = True

                with st.spinner("Processing documents..."):
                    try:
                        # 🔥 No Milvus dependency here anymore
                        files_text = get_files_text(uploaded_files)
                        text_chunks = get_text_chunks(files_text)

                        # 👉 This already handles Milvus → FAISS fallback
                        vectorstore = get_vectorstore(text_chunks)

                        st.session_state.conversation = get_conversation_chain(vectorstore)

                        user_pref = (
                            "points"
                            if st.session_state.summary_format == "Points"
                            else "paragraph"
                        )

                        st.session_state.summary = generate_summary(user_preference=user_pref)
                        st.session_state.processComplete = True

                        st.success("✅ Document processed successfully!")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.session_state.processComplete = False

                    finally:
                        st.session_state.is_processing = False
            else:
                st.info("Same file uploaded. No reprocessing needed.")
        else:
            st.warning("Please upload at least one file.")

    # -------------------------------
    # 🔹 Display Summary + Chat
    # -------------------------------
    if st.session_state.processComplete:
        st.subheader("Summary")

        st.radio(
            "Select summary format:",
            ["Paragraph", "Points"],
            key="summary_format",
            on_change=update_summary_format
        )

        st.write(st.session_state.summary or "No summary available.")

        # Chat History
        for msg in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(msg["user"])
            with st.chat_message("assistant"):
                st.write(msg["assistant"])

        # User Input
        user_question = st.chat_input("Ask a question about your document")

        if user_question:
            with st.chat_message("user"):
                st.write(user_question)

            response = handle_user_input(user_question)
            answer = response.get("answer", "No answer found.")

            st.session_state.chat_history.append({
                "user": user_question,
                "assistant": answer
            })

            with st.chat_message("assistant"):
                st.write(answer)

    # -------------------------------
    # 🔹 Processing Indicator
    # -------------------------------
    if st.session_state.is_processing:
        st.info("Processing... Please wait.")


# -------------------------------
# 🔹 Run App
# -------------------------------
if __name__ == "__main__":
    main()