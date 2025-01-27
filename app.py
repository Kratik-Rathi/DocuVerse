import streamlit as st
from dotenv import load_dotenv
from document_processor import get_files_text
from text_processor import get_vectorstore, get_text_chunks
from model import initialize_model
from conversation import handle_user_input, generate_summary, update_summary_format, get_conversation_chain


def main():
    load_dotenv()
    st.set_page_config(page_title="Ask your Document", layout="wide")
    st.title("Ask Your Document")

    # Initialize session state variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = False
    if "summary_format" not in st.session_state:
        st.session_state.summary_format = "Paragraph"
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "model" not in st.session_state:
        initialize_model()
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    # Conditional layout for file uploader
    if not st.session_state.processComplete:
        st.write("## Upload your file")
        uploaded_files = st.file_uploader(
            "Upload your PDF or DOCX file", type=["pdf", "docx"], accept_multiple_files=True
        )
        process = st.button("Process")
        warning_placeholder = st.empty()  # Initialize the warning placeholder
    else:
        with st.sidebar:
            st.write("## Upload more files")
            uploaded_files = st.file_uploader(
                "Upload your PDF or DOCX file", type=["pdf", "docx"], accept_multiple_files=True
            )
            process = st.button("Process")
            warning_placeholder = st.empty()  # Initialize the warning placeholder

    # Process the uploaded files if the process button is clicked
    if process:
        if uploaded_files:
            st.session_state.conversation = None
            st.session_state.chat_history = None
            st.session_state.processComplete = False
            st.session_state.summary = None

            st.session_state.is_processing = True

            # Get text from uploaded files
            files_text = get_files_text(uploaded_files)
            text_chunks = get_text_chunks(files_text)

            vectorstore = get_vectorstore(text_chunks)
            st.session_state.conversation = get_conversation_chain(vectorstore)

            # Generate summary based on user preference
            user_preference = "points" if st.session_state.summary_format == "Points" else "paragraph"
            st.session_state.summary = generate_summary(user_preference=user_preference)

            # Mark process as complete
            st.session_state.processComplete = True
            st.session_state.is_processing = False
        else:
            # Use the warning_placeholder to show the warning message below the process button
            warning_placeholder.warning("Please upload at least one file.")

    # If the process is complete, show the summary and chat interface
    if st.session_state.processComplete:
        st.subheader("Summary")
        st.radio(
            "Select summary format:",
            options=["Paragraph", "Points"],
            index=0 if st.session_state.summary_format == "Paragraph" else 1,
            on_change=update_summary_format,
            key="summary_format",
        )

        if not st.session_state.summary:
            user_preference = "points" if st.session_state.summary_format == "Points" else "paragraph"
            st.session_state.summary = generate_summary(user_preference=user_preference)

        st.write(st.session_state.summary or "No summary available.")

        user_question = st.chat_input("Ask a question about your files.")
        if user_question:
            handle_user_input(user_question)
    else:
        if st.session_state.is_processing:
            st.info("Processing the uploaded document. Please wait...")


if __name__ == '__main__':
    main()
