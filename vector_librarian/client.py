
from hamilton import driver
from streamlit.runtime.uploaded_file_manager import UploadedFile

from backend import ingestion, retrieval, vector_db, arxiv_module


DRIVER_CONFIG = dict()

DRIVER = (
    driver.Builder()
    .enable_dynamic_execution(allow_experimental_mode=True)
    .with_config(DRIVER_CONFIG)
    .with_modules(arxiv_module, ingestion, retrieval, vector_db)
    .build()
)


def initialize(
    weaviate_url: str,
    weaviate_api_key: str,
) -> None:
    DRIVER.execute(
        ["initialize_weaviate_instance"],
        inputs=dict(
            weaviate_url=weaviate_url,
            weaviate_api_key=weaviate_api_key,
        )
    )


def store_arxiv(
    weaviate_url: str,
    weaviate_api_key: str,
    arxiv_ids: list[str],
) -> None:
    """Retrieve PDF files of arxiv articles for arxiv_ids\n
    Read the PDF as text, create chunks, and embed them using OpenAI API\n
    Store chunks with embeddings in Weaviate.
    """
    DRIVER.execute(
        ["store_documents"],
        inputs=dict(
            arxiv_ids=arxiv_ids,
            embedding_model_name="text-embedding-ada-002",
            data_dir="./data",
            weaviate_url=weaviate_url,
            weaviate_api_key=weaviate_api_key,
        ),
    )
    return


def store_pdfs(
    weaviate_url: str,
    weaviate_api_key: str,
    pdf_files: list[UploadedFile],
) -> None:
    """For each PDF file, read as text, create chunks, and embed them using OpenAI API\n
    Store chunks with embeddings in Weaviate.
    """
    DRIVER.execute(
        ["store_documents"],
        inputs=dict(
            arxiv_ids=[],
            embedding_model_name="text-embedding-ada-002",
            data_dir="",
            weaviate_url=weaviate_url,
            weaviate_api_key=weaviate_api_key,
        ),
        overrides=dict(
            local_pdfs=pdf_files,
        )
    )
    return


def rag_summary(
    weaviate_url: str,
    weaviate_api_key: str,
    rag_query: str,
    hybrid_search_alpha: float,
    retrieve_top_k: int,
):
    """Retrieve most relevant chunks stored in Weaviate using hybrid search\n
    Generate text summaries using ChatGPT for each chunk\n
    Concatenate all chunk summaries into a single query, and reduce into a
    final summary
    """
    results = DRIVER.execute(
        ["rag_summary", "all_chunks"],
        inputs=dict(
            rag_query=rag_query,
            hybrid_search_alpha=hybrid_search_alpha,
            retrieve_top_k=retrieve_top_k,
            embedding_model_name="text-embedding-ada-002",
            summarize_model_name="gpt-3.5-turbo-0613",
            weaviate_url=weaviate_url,
            weaviate_api_key=weaviate_api_key,
        ),
    )
    return results


def all_documents(weaviate_url: str, weaviate_api_key: str,):
    """Retrieve the file names of all stored PDFs in the Weaviate instance"""
    results = DRIVER.execute(
        ["all_documents_file_name"],
        inputs=dict(
            weaviate_url=weaviate_url,
            weaviate_api_key=weaviate_api_key,
        ),
    )
    return results