# Framework supporting MLOps Apps
import streamlit as st 
# Large Language Model Library
from langchain.llms import OpenAI
import docx
import datetime
import time
import base64
import json

# Additional Imports
from authentication import openai_connection_status, weaviate_connection_status
import client

# App initialization
st.set_page_config(
    page_title="🤖 AIVABOT",
    page_icon="🩺",
    layout="centered",
    menu_items={"Get help": None, "Report a bug": None},
)

# Sidebar setup
with st.sidebar:
    openai_connection_status()
    weaviate_connection_status()

# Main app title
st.title("🤖 AIVABOT")

# Check if OpenAI API key is provided
if st.session_state.get("OPENAI_STATUS") != ("success", None):
    st.warning("You need to provide an OpenAI API key. Visit `Information` to connect.")
else:
    # OpenAI LLM initialization
    llm = OpenAI(temperature=0.3, openai_api_key=st.session_state.get("OPENAI_KEY"))

    # AIVABOT pages
    pages = ["Chatbot", "Medical Summary Report Generator", "Weaviate's Memory"]
    selected_page = st.sidebar.radio("Select Page", pages)

    # Page navigation
    if selected_page == "Chatbot":
        # Chatbot page
        # ... (previous chatbot code)
    elif selected_page == "Medical Summary Report Generator":
        # Medical Summary Report Generator page
        # ... (previous medical report code)
    elif selected_page == "Weaviate's Memory":
        # Weaviate's Memory page
        st.header("🧠 Weaviate's Memory")

        # Add Weaviate's memory functionalities here
        # ...

# Additional functionalities (e.g., history, etc.)
# ...
