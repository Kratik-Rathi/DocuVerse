from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import streamlit as st
from model import get_model
from streamlit_chat import message
from utils import enforce_paragraph_format


def get_conversation_chain(vectorstore):
    """Create a conversational retrieval chain using Groq."""
    model = get_model()  # Use the Groq model
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Create the conversation chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        verbose=True
    )
    return conversation_chain


def handle_user_input(user_question):
    """Handles user input and displays conversation history correctly."""

    if any(keyword in user_question.lower() for keyword in ["points", "list", "bullets"]):
        prompt = f"Give the answer in bullet points without missing any information: {user_question}"
    else:
        prompt = f"Provide a detailed answer in paragraph format without omitting details: {user_question}"

    if "conversation" not in st.session_state:
        st.error("Conversation chain is not initialized. Please upload a file first.")
        return

    response = st.session_state.conversation({"question": prompt})
    assistant_reply = response.get("answer", "Sorry, I couldn't generate a response.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({"user": user_question, "assistant": assistant_reply})
    for i, chat in enumerate(st.session_state.chat_history):
        message(chat["user"], is_user=True, key=f"user_{i}")
        message(chat["assistant"], key=f"assistant_{i}")


def generate_summary(user_preference="paragraph", auto_generate=False):
    """Generate a detailed summary from the document."""
    if not st.session_state.conversation:
        return "No data available to summarize."
    if auto_generate:
        user_preference = "paragraph"

    # Dynamically adjust the summary prompt
    if user_preference == "paragraph":
        prompt = "Provide a very detailed and comprehensive summary of the document in a single paragraph, including all key aspects and insights."
    elif user_preference == "points":
        prompt = "Provide a very detailed and comprehensive summary of the document in bullet points, including all major insights and important details."
    else:
        prompt = "Provide a very detailed and comprehensive summary of the document in a single paragraph, including all key aspects and insights."

    original_memory = st.session_state.conversation.memory
    st.session_state.conversation.memory = None

    try:
        response = st.session_state.conversation({"question": prompt, "chat_history": []})
        summary = response["answer"]
    finally:
        st.session_state.conversation.memory = original_memory

    if user_preference == "paragraph":
        summary = enforce_paragraph_format(summary)
    return summary


def update_summary_format():
    st.session_state.summary = None
    print(st.session_state.summary_format)
    user_preference = "points" if st.session_state.summary_format == "Points" else "Paragraph"
    st.session_state.summary = generate_summary(user_preference=user_preference)
