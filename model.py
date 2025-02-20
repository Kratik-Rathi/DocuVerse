from langchain_groq import ChatGroq
import streamlit as st


def initialize_model():
    """Initialize the Groq-based model."""
    st.session_state.model = ChatGroq(
        model="gemma2-9b-it",  # Update with the desired Groq-supported model
        temperature=0.3
    )


def get_model():
    """Get the initialized model."""
    return st.session_state.model
