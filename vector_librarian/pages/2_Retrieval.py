import streamlit as st

from vector_librarian import client
from vector_librarian.common import sidebar


def retrieval_form_container() -> None:
    """Container to enter RAG query and sent /rag_summary GET request"""
    left, right = st.columns(2)
    with left:
        form = st.form(key="retrieval_query")
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
            response = client.rag_summary(
                weaviate_url=st.session_state.get("WEAVIATE_URL"),
                weaviate_api_key=st.session_state.get("WEAVIATE_API_KEY"),
                rag_query=rag_query,
                hybrid_search_alpha=hybrid_search_alpha,
                retrieve_top_k=int(retrieve_top_k),
            )
        st.session_state["history"].append(dict(query=rag_query, response=response))


def history_display_container(history):
    if len(history) > 1:
        st.header("History")
        max_idx = len(history) - 1
        history_idx = st.slider("History", 0, max_idx, value=max_idx, label_visibility="collapsed")
        entry = history[history_idx]
    else:
        entry = history[0]

    st.subheader("Query")
    st.write(entry["query"])

    st.subheader("Response")
    st.write(entry["response"]["rag_summary"])

    with st.expander("Sources"):
        st.write(entry["response"]["all_chunks"])


def app() -> None:
    """Streamlit entrypoint for PDF Summarize frontend"""
    # config
    st.set_page_config(
        page_title="📤 retrieval",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )
    sidebar()

    st.title("📤 Retrieval")

    retrieval_form_container()

    if history := st.session_state.get("history"):
        history_display_container(history)
    else:
        st.session_state["history"] = list()


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()