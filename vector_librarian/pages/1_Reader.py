import streamlit as st

import client
from authentication import openai_connection_status, weaviate_connection_status


def document_selector(dr):
    response = client.all_documents(
        dr=dr,
        weaviate_client=st.session_state.get("WEAVIATE_CLIENT")
    )
    documents = response["all_documents_file_name"]
    selected_documents = st.multiselect("Select documents", documents, format_func=lambda d: d["file_name"])
    return selected_documents


def pdf_reader(dr, document_ids: list) -> None:
    """Display the PDFs as embedded b64 strings in a markdown component"""
    for document_id in document_ids:
        response = client.get_document_by_id(
            dr=dr,
            weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
            document_id=document_id,
        )
        base64_pdf = response["get_document_by_id"]["pdf_blob"]
        pdf_str = f'<embed src="data:application/pdf;base64,{base64_pdf}" width=100% height=800 type="application/pdf">'
        st.markdown(pdf_str, unsafe_allow_html=True)


def app() -> None:
    st.set_page_config(
        page_title="Library",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()
        # stored_documents_container()

    st.title("🤓 Reader")
    st.markdown("Find below the PDF files indexed and stored in your Weaviate instance.")

    dr = client.instantiate_driver()

    selected_documents = document_selector(dr=dr)
    print(selected_documents)
    pdf_reader(dr=dr, document_ids=[doc["_additional"]["id"] for doc in selected_documents])


if __name__ == "__main__":
    app()
