import json
import pandas as pd
import streamlit as st
import client
from authentication import openai_connection_status, weaviate_connection_status

def main():
    st.set_page_config(
        page_title="📤 Retrieval Chatbot",
        page_icon="🤖",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    st.title("📤 Retrieval Chatbot")

    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()

    st.write("Hello! I'm your Retrieval Chatbot. How can I assist you today?")

    openai_status = st.session_state.get("OPENAI_STATUS")
    if openai_status != ("success", None):
        st.warning("You need to provide an OpenAI API key. Visit `Information` to connect.")
        return

    dr = client.instantiate_driver()

    # User Input
    st.header("Ask me Anything:")
    rag_query = st.text_area("Your question:", value="What are the main challenges of deploying ML models?")
    retrieve_top_k = st.number_input("Top K results", value=3, help="Specify the number of results to retrieve")
    hybrid_search_alpha = st.slider("Search mode", min_value=0.0, max_value=1.0, value=0.75,
                                    help="[Weaviate docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)")

    # Chatbot Processing
    if st.button("Search"):
        with st.spinner("Searching..."):
            response = client.rag_summary(
                dr=dr,
                weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
                rag_query=rag_query,
                hybrid_search_alpha=hybrid_search_alpha,
                retrieve_top_k=int(retrieve_top_k),
            )
        st.session_state["history"].append(dict(query=rag_query, response=response))

        # Display Results
        st.header("Chatbot Response:")
        st.write(response["rag_summary"])

        # Display Detailed Results
        st.subheader("Detailed Results:")
        display_results(response)

        # Download Q&A History
        download_history(st.session_state.get("history"))

def display_results(response):
    # Display detailed results here
    pass

def download_history(history):
    st.download_button(
        "Download Q&A History",
        data=json.dumps(history),
        file_name="chatbot_history.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()
