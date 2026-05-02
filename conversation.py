import streamlit as st

from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_classic.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)

from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from model import get_model
from utils import enforce_paragraph_format


# -------------------------------
# 🔹 Initialize Conversation Chain
# -------------------------------
def get_conversation_chain(vectorstore):
    """
    Creates a conversational RAG pipeline with memory.
    """

    llm = get_model()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )

    # Memory stores previous user/assistant messages
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # -------------------------------
    # Step 1: Rewrite follow-up question
    # -------------------------------
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Given the chat history and the latest user question, rewrite the latest question
as a standalone question.

Do not answer the question.
Only rewrite it if it depends on previous chat history.
If it is already standalone, return it as-is.
"""
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_q_prompt
    )

    # -------------------------------
    # Step 2: Main QA prompt
    # -------------------------------
    qa_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a helpful document-based assistant.

Use the provided context to answer the user's question in detail.

Context:
{context}

Rules:
- Answer only using the provided document context.
- If the answer is not available in the context, say:
  "The uploaded document does not contain enough information to answer this."
- Do not make up facts.
- Keep the answer clear, structured, and useful.
"""
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    question_answer_chain = create_stuff_documents_chain(
        llm,
        qa_prompt
    )

    # -------------------------------
    # Step 3: Full RAG pipeline
    # -------------------------------
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain
    )

    return {
        "chain": rag_chain,
        "memory": memory
    }


# -------------------------------
# 🔹 Handle User Query
# -------------------------------
def handle_user_input(user_question):
    """
    Handles user input and returns assistant response.
    """

    if "conversation" not in st.session_state:
        st.error("Conversation not initialized. Please upload documents first.")
        return {"answer": "Conversation not initialized. Please upload documents first."}

    chain = st.session_state.conversation["chain"]
    memory = st.session_state.conversation["memory"]

    # Format response style based on user request
    if any(
        keyword in user_question.lower()
        for keyword in ["points", "list", "bullets", "bullet points"]
    ):
        formatted_question = (
            "Answer in detailed bullet points without missing important information: "
            f"{user_question}"
        )
    else:
        formatted_question = (
            "Provide a detailed paragraph answer without omitting important information: "
            f"{user_question}"
        )

    # Get chat history from memory
    chat_history = memory.chat_memory.messages

    try:
        response = chain.invoke({
            "input": formatted_question,
            "chat_history": chat_history
        })

        answer = response.get(
            "answer",
            "Sorry, I couldn't generate a response."
        )

        # Save original user question and final answer to memory
        memory.chat_memory.add_user_message(user_question)
        memory.chat_memory.add_ai_message(answer)

        return {"answer": answer}

    except Exception as e:
        error_message = f"Error while generating response: {str(e)}"
        st.error(error_message)
        return {"answer": error_message}


# -------------------------------
# 🔹 Generate Summary
# -------------------------------
def generate_summary(user_preference="paragraph", auto_generate=False):
    """
    Generate a document summary.
    """

    if "conversation" not in st.session_state:
        return "No data available to summarize. Please upload documents first."

    chain = st.session_state.conversation["chain"]

    if auto_generate:
        user_preference = "paragraph"

    summary_prompts = {
        "paragraph": """
Provide a very detailed and comprehensive summary of the uploaded document
in a single well-written paragraph. Include all key insights, important points,
major arguments, conclusions, and relevant details from the document.
""",
        "points": """
Provide a very detailed and comprehensive summary of the uploaded document
in bullet points. Include all key insights, important points, major arguments,
conclusions, and relevant details from the document.
"""
    }

    prompt = summary_prompts.get(
        user_preference,
        "Provide a detailed summary of the uploaded document."
    )

    try:
        response = chain.invoke({
            "input": prompt,
            "chat_history": []
        })

        summary = response.get("answer", "No summary generated.")

        if user_preference == "paragraph":
            summary = enforce_paragraph_format(summary)

        return summary

    except Exception as e:
        return f"Error while generating summary: {str(e)}"


# -------------------------------
# 🔹 UI Callback
# -------------------------------
def update_summary_format():
    """
    Callback when user changes summary format.
    """

    st.session_state.summary = None

    user_preference = (
        "points"
        if st.session_state.summary_format == "Points"
        else "paragraph"
    )

    st.session_state.summary = generate_summary(
        user_preference=user_preference
    )