import streamlit as st
from pymed import PubMed

import client
from authentication import openai_connection_status, weaviate_connection_status

def pubmed_search_container() -> None:
    """Container to query PubMed using the pymed library"""
    form = st.form(key="pubmed_search_form")
    query = form.text_area(
        "PubMed Search Query",
        value="LLM in production",
        help="[See docs](https://github.com/gijswobben/pymed)",
    )

    with st.expander("PubMed Search Parameters"):
        max_results = st.number_input("Max results", value=5)

    if form.form_submit_button("Search"):
        st.session_state["pubmed_search"] = dict(
            query=query,
            max_results=max_results,
        )

def article_selection_container(dr, pubmed_form: dict) -> None:
    """Container to select PubMed search results and send /store_pubmed POST request"""
    pubmed = PubMed(tool="MyTool", email="my@email.com")
    results = pubmed.query(pubmed_form['query'], max_results=pubmed_form['max_results'])
    
    form = st.form(key="article_selection_form")
    selection = form.multiselect("Select articles to store", results, format_func=lambda r: r.title)
    
    if form.form_submit_button("Store"):
        pubmed_ids = [entry.pubmed_id for entry in selection]
        with st.status("Storing PubMed articles"):
            client.store_pubmed(
                dr=dr,
                weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
                pubmed_ids=pubmed_ids,
            )

def app() -> None:
    st.set_page_config(
        page_title="📥 ingestion",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )
    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()

    st.title("📥 Ingestion")

    if st.session_state.get("WEAVIATE_DEFAULT_INSTANCE"):
        st.warning("""
            Ingestion is disabled when using the Default Weaviate instance.
            Visit `Information` to connect to your own instance and ingest new documents.
        """)
        return
    
    if st.session_state.get("OPENAI_STATUS") !=  ("success", None):
        st.warning("""
            You need to provide an OpenAI API key.
            Visit `Information` to connect.    
        """)
        return
    
    dr = client.instantiate_driver()

    left, right = st.columns(2)

    with left:
        st.subheader("Download from PubMed")
        pubmed_search_container()
        if pubmed_form := st.session_state.get("pubmed_search"):
            article_selection_container(dr, pubmed_form)

    with right:
        st.subheader("Upload PDF files")
        pdf_upload_container(dr)

if __name__ == "__main__":
    app()
