from langchain_groq import ChatGroq
import streamlit as st


def initialize_model():
    """Initialize the Groq-based model."""
    if "model" not in st.session_state:
        try:
            # Access the API key from Streamlit secrets
            groq_api_key = st.secrets["GROQ_API_KEY"]
            st.session_state.model = ChatGroq(
                model="gemma2-9b-it",  # Replace with the correct model name
                api_key=groq_api_key,
                temperature=0.3
            )
        except KeyError:
            st.error("GROQ_API_KEY is missing in the secrets file.")
        except Exception as e:
            st.error(f"Failed to initialize the model: {e}")
            print(f"Error initializing model: {e}")


def get_model():
    """Get the initialized model."""
    return st.session_state.model
