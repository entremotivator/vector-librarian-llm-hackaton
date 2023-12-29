# Framework supporting MLOps Apps
import streamlit as st 
# Additional Imports
from authentication import openai_connection_status, weaviate_connection_status
import client
# Large Language Model Library

import datetime
import time
import base64
import json

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

    # Chatbot page
    st.header("🤖 Chatbot")
    
    # User input field
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "🤖", "content": "Hey there! I'm your AIVABOT. How can I assist you today?"})
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            with st.spinner('Starting Bot ...'):
                st.markdown(message["content"])

    # Chatbot functionalities
    if (prompt := st.text_input("You:", key="chat_input")):
        # Display user message in chat message container
        with st.chat_message("🙂"):
            st.markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "🙂", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("🤖"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner('Wait for it...'):
                assistant_response = llm(prompt)

            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "🤖", "content": full_response})

# Additional functionalities (e.g., history, etc.)
# ...
