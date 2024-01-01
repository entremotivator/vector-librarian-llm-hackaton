import json
import pandas as pd
import streamlit as st
from authentication import openai_connection_status, weaviate_connection_status
from client import your_chatbot_function  # Replace with your actual chatbot function

# Function to send a message to the chatbot and get the response
def chatbot_interaction(message):
    response = your_chatbot_function(message)  # Replace with your actual chatbot function
    return response

# Streamlit app header
st.title("Streamlit Chatbot")

# Check connection status
openai_status = openai_connection_status()
weaviate_status = weaviate_connection_status()

st.subheader("Connection Status")
st.write(f"OpenAI Connection Status: {openai_status}")
st.write(f"Weaviate Connection Status: {weaviate_status}")

# Chatbot interface
st.subheader("Chat with the Bot")

# User input box
user_input = st.text_input("You:", "")

# Button to send message
if st.button("Send"):
    # Display user message
    st.text("You: " + user_input)

    # Get chatbot response
    bot_response = chatbot_interaction(user_input)

    # Display chatbot response
    st.text("Chatbot: " + bot_response)
