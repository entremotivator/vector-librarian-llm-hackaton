import json
import pandas as pd
import streamlit as st
import client
from authentication import openai_connection_status, weaviate_connection_status

def main():
    st.set_page_config(
        page_title="📤 retrieval",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    st.title("📤 Retrieval")

    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()

    st.write("Hello! I'm your retrieval chatbot. How can I assist you today?")

    openai_status = st.session_state.get("OPENAI_STATUS")
    if openai_status != ("success", None):
        st.warning("You need to provide an OpenAI API key. Visit `Information` to connect.")
        return

    dr = client.instantiate_driver()

    # User Input
    rag_query = st.text_area("Ask me something:", value="What are the main challenges of deploying ML models?")
    retrieve_top_k = st.number_input("Top K", value=3, help="The number of chunks to consider for response")
    hybrid_search_alpha = st.slider("Alpha", min_value=0.0, max_value=1.0, value=0.75,
                                    help="[Weaviate docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)")

    # Chatbot Processing
    if st.button("Search"):
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

if __name__ == "__main__":
    main()
