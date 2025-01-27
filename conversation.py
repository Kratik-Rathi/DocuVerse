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
    # Determine if the user expects a list/points
    if any(keyword in user_question.lower() for keyword in ["points", "list", "bullets"]):
        prompt = f"Provide the answer in bullet points: {user_question}"
    else:
        prompt = user_question  # Keep the user's original question as-is

    # Query the conversation chain
    response = st.session_state.conversation({"question": prompt})
    st.session_state.chat_history = response["chat_history"]

    # Layout of input/response containers
    response_container = st.container()

    # Display chat history
    with response_container:
        for i, messages in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                # Display the user's question only (not the reformatted prompt)
                message(user_question, is_user=True, key=str(i))
            else:
                # Display the assistant's response
                message(messages.content, key=str(i))


def generate_summary(user_preference="paragraph", auto_generate=False):
    """Generate a detailed summary from the document."""
    # Ensure the conversation chain is available
    if not st.session_state.conversation:
        return "No data available to summarize."

    # If auto_generate is True, set user_preference to "paragraph"
    if auto_generate:
        user_preference = "paragraph"

    # Dynamically adjust the summary prompt
    if user_preference == "paragraph":
        prompt = "Provide a very detailed and comprehensive summary of the document in a paragraph format, including all key aspects and insights."
    elif user_preference == "points":
        prompt = "Provide a very detailed summary of the document in bullet points, including all major insights and important details."
    else:
        prompt = "Provide a very detailed summary of the document in a paragraph format, including all key aspects and insights."

    # Temporarily disable memory updates during summary generation
    original_memory = st.session_state.conversation.memory
    st.session_state.conversation.memory = None  # Disable memory

    try:
        # Query the conversational chain for the summary with an empty chat history
        response = st.session_state.conversation({"question": prompt, "chat_history": []})
        summary = response["answer"]
    finally:
        # Restore the memory after summary generation
        st.session_state.conversation.memory = original_memory

    # Format the summary based on user preference
    if user_preference == "paragraph":
        summary = enforce_paragraph_format(summary)
    return summary


def update_summary_format():
    user_preference = "points" if st.session_state.summary_format == "Points" else "paragraph"
    st.session_state.summary = generate_summary(user_preference=user_preference)
