import json
import pandas as pd
import streamlit as st
from trulens import Trulens

import client
from authentication import openai_connection_status, weaviate_connection_status

# Constants
DEFAULT_RAG_QUERY = "What are the main challenges of deploying ML models?"
DEFAULT_TOP_K = 3
DEFAULT_ALPHA = 0.75

def add_trulens_to_sidebar():
    st.sidebar.title("🔍 Trulens")
    trulens_expander = st.sidebar.expander("Trulens Configuration")

    with trulens_expander:
        st.write("Configure Trulens settings here.")

def get_rag_query_form():
    form = st.form(key="retrieval_query")
    rag_query = form.text_area("Retrieval Query", value=DEFAULT_RAG_QUERY)
    return form, rag_query

def get_hybrid_search_parameters():
    st.write("Hybrid Search Parameters")
    retrieve_top_k = st.number_input("top K", value=DEFAULT_TOP_K, help="The number of chunks to consider for response")
    hybrid_search_alpha = st.slider(
        "alpha",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_ALPHA,
        help="0: Keyword. 1: Vector.\n[Weaviate docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)",
    )
    return int(retrieve_top_k), hybrid_search_alpha

def run_search(dr, rag_query, retrieve_top_k, hybrid_search_alpha):
    with st.status("Running"):
        response = client.rag_summary(
            dr=dr,
            weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
            rag_query=rag_query,
            hybrid_search_alpha=hybrid_search_alpha,
            retrieve_top_k=retrieve_top_k,
        )
    st.session_state["history"].append(dict(query=rag_query, response=response))

def display_history(history):
    if len(history) > 1:
        st.header("History")
        max_idx = len(history) - 1
        history_idx = st.slider("History", 0, max_idx, value=max_idx, label_visibility="collapsed")
        entry = history[history_idx]
    else:
        entry = history[0]

    st.download_button(
        "Download Q&A History",
        data=json.dumps(history),
        file_name="vector-librarian.json",
        mime="application/json"
    )

    st.subheader("Query")
    st.write(entry["query"])

    st.subheader("Response")
    st.write(entry["response"]["rag_summary"])

    df = pd.DataFrame(entry["response"]["all_chunks"])
    df = df.set_index("chunk_id")
    df = df.rename(columns=dict(
        score="Relevance",
        chunk_index="Chunk Index",
        document_file_name="File name",
        content="Content",
        summary="Summary"
    ))

    st.info("Double-click cell to read full content")
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_order=("Relevance", "Chunk Index", "File name", "Content", "Summary"),
        column_config={col: st.column_config.Column(width="small") 
                       for col in ("Relevance", "Chunk Index", "File name", "Content", "Summary")
                      }
    )

def app() -> None:
    st.set_page_config(
        page_title="📤 retrieval",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()
        add_trulens_to_sidebar()

    st.title("📤 Retrieval")

    if st.session_state.get("OPENAI_STATUS") != ("success", None):
        st.warning("""
            You need to provide an OpenAI API key.
            Visit `Information` to connect.    
        """)
        return
    
    dr = client.instantiate_driver()

    form, rag_query = get_rag_query_form()
    retrieve_top_k, hybrid_search_alpha = get_hybrid_search_parameters()

    if form.form_submit_button("Search"):
        run_search(dr, rag_query, retrieve_top_k, hybrid_search_alpha)

    history = st.session_state.get("history", [])
    display_history(history)

if __name__ == "__main__":
    app()
