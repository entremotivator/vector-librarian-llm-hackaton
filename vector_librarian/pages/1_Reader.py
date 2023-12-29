import streamlit as st
import client
from authentication import openai_connection_status, weaviate_connection_status

def document_selector(dr):
    response = client.all_documents(
        dr=dr,
        weaviate_client=st.session_state.get("WEAVIATE_CLIENT")
    )
    documents = response["all_documents_file_name"]
    return st.selectbox("Select document", documents, format_func=lambda d: d["file_name"])

def document_reader(dr, document_id: str, document_type: str) -> None:
    response = client.get_document_by_id(
        dr=dr,
        weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
        document_id=document_id,
    )

    if document_type == "pdf":
        base64_content = response["get_document_by_id"]["pdf_blob"]
        content_type = "application/pdf"
    elif document_type == "txt":
        base64_content = response["get_document_by_id"]["text_blob"]
        content_type = "text/plain"
    else:
        st.error(f"Unsupported document type: {document_type}")
        return

    content_str = f'<embed src="data:{content_type};base64,{base64_content}" width=100% height=800 type="{content_type}">'
    st.markdown(content_str, unsafe_allow_html=True)

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

    st.title("🤓 Reader")
    st.markdown("Find below the documents indexed and stored in your Weaviate instance.")

    dr = client.instantiate_driver()
    document = document_selector(dr=dr)

    document_type = document["_additional"]["type"]  # Assuming there's a 'type' field in your document metadata
    print(document)
    document_reader(dr=dr, document_id=document["_additional"]["id"], document_type=document_type)

if __name__ == "__main__":
    app()
