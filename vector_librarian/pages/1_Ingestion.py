import arxiv
import streamlit as st

from vector_librarian import client
from vector_librarian.common import sidebar


def arxiv_search_container() -> None:
    """Container to query Arxiv using the Python `arxiv` library"""
    form = st.form(key="arxiv_search_form")
    query = form.text_area(
        "arXiv Search Query",
        value="LLM in production",
        help="[See docs](https://lukasschwab.me/arxiv.py/index.html#Search)",
    )

    with st.expander("arXiv Search Parameters"):
        max_results = st.number_input("Max results", value=5)
        sort_by = st.selectbox(
            "Sort by",
            [
                arxiv.SortCriterion.Relevance,
                arxiv.SortCriterion.LastUpdatedDate,
                arxiv.SortCriterion.SubmittedDate,
            ],
            format_func=lambda option: option.value[0].upper() + option.value[1:],
        )
        sort_order = st.selectbox(
            "Sort order",
            [arxiv.SortOrder.Ascending, arxiv.SortOrder.Descending],
            format_func=lambda option: option.value[0].upper() + option.value[1:],
        )

    if form.form_submit_button("Search"):
        st.session_state["arxiv_search"] = dict(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )


def article_selection_container(arxiv_form: dict) -> None:
    """Container to select arxiv search results and send /store_arxiv POST request"""
    results = list(arxiv.Search(**arxiv_form).results())
    form = st.form(key="article_selection_form")
    selection = form.multiselect("Select articles to store", results, format_func=lambda r: r.title)
    if form.form_submit_button("Store"):
        arxiv_ids = [entry.get_short_id() for entry in selection]
        with st.status("Storing arXiv articles"):
            client.store_arxiv(
                weaviate_url=st.session_state.get("WEAVIATE_URL"),
                weaviate_api_key=st.session_state.get("WEAVIATE_API_KEY"),
                arxiv_ids=arxiv_ids,
            )


def pdf_upload_container():
    """Container to uploader arbitrary PDF files and send /store_pdfs POST request"""
    uploaded_files = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=True)
    if st.button("Upload"):
        with st.status("Storing PDFs"):
            client.store_pdfs(
                weaviate_url=st.session_state.get("WEAVIATE_URL"),
                weaviate_api_key=st.session_state.get("WEAVIATE_API_KEY"),
                pdf_files=uploaded_files,
            )


def stored_documents_container():
    """Container showingstored PDF documents, results of /documents GET request"""
    response = client.all_documents(
        weaviate_url=st.session_state.get("WEAVIATE_URL"),
        weaviate_api_key=st.session_state.get("WEAVIATE_API_KEY"),
    )
    documents = response["all_documents_file_name"]
    st.table({"PDF file name": documents})


def app() -> None:
    """Streamlit entrypoint for PDF Summarize frontend"""
    # config
    st.set_page_config(
        page_title="📥 ingestion",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )
    sidebar()

    st.title("📥 Ingestion")

    left, right = st.columns(2)

    with left:
        st.subheader("Download from arXiv")
        arxiv_search_container()
        if arxiv_form := st.session_state.get("arxiv_search"):
            article_selection_container(arxiv_form)

    with right:
        st.subheader("Upload PDF files")
        pdf_upload_container()

    st.header("Documents stored in Weaviate")
    stored_documents_container()


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()