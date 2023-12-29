import json
import pandas as pd
import streamlit as st

import client
from authentication import openai_connection_status, weaviate_connection_status

def medical_search_prompt_container() -> None:
    """Container to select a pre-programmed medical search prompt."""
    st.subheader("Medical Search")
    medical_prompt_options = [
        "Diagnose a medical condition.",
        "Treatment options for a specific disease.",
        "Side effects of a medication.",
        # Add more medical prompts as needed
    ]
    medical_prompt = st.selectbox("Select a medical prompt", medical_prompt_options)
    return medical_prompt

def retrieval_form_container(dr, is_medical_query) -> None:
    """Container to enter RAG query and send /rag_summary GET request."""
    left, right = st.columns(2)
    with left:
        form = st.form(key="retrieval_query")
        if is_medical_query:
            rag_query = medical_search_prompt_container()
        else:
            rag_query = form.text_area(
                "Retrieval Query", value="What are the main challenges of deploying ML models?"
            )

    with right:
        st.write("Hybrid Search Parameters")
        retrieve_top_k = st.number_input(
            "top K", value=3, help="The number of chunks to consider for response"
        )
        hybrid_search_alpha = st.slider(
            "alpha",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            help="0: Keyword. 1: Vector.\n[Weaviate docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)",
        )

    if form.form_submit_button("Search"):
        with st.status("Running"):
            try:
                response = client.rag_summary(
                    dr=dr,
                    weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
                    rag_query=rag_query,
                    hybrid_search_alpha=hybrid_search_alpha,
                    retrieve_top_k=int(retrieve_top_k),
                )
                st.session_state["history"].append(dict(query=rag_query, response=response))
            except Exception as e:
                st.error(f"Error during retrieval: {str(e)}")

def history_display_container(history):
    if history:
        st.header("History")
        max_idx = len(history) - 1
        history_idx = st.slider("History", 0, max_idx, value=max_idx, label_visibility="collapsed")
        entry = history[history_idx]

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
    else:
        st.info("No history to display.")

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

    st.title("📤 Retrieval")

    if st.session_state.get("OPENAI_STATUS") != ("success", None):
        st.warning("""
            You need to provide an OpenAI API key.
            Visit `Information` to connect.    
        """)
        return
    
    dr = client.instantiate_driver()

    is_medical_query = st.checkbox("Medical Search", value=False)
    retrieval_form_container(dr, is_medical_query)

    if history := st.session_state.get("history"):
        history_display_container(history)
    else:
        st.session_state["history"] = list()

if __name__ == "__main__":
    app()
