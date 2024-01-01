import os
import json
import pandas as pd
import streamlit as st
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from trulens_eval import Tru, Feedback, Select, Groundedness, TruCustomApp
from langchain.vectorstores.weaviate import Weaviate
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain
import weaviate
import numpy as np

# Import client and authentication modules
import client
from authentication import openai_connection_status, weaviate_connection_status, user_auth_openai, user_auth_weaviate, default_auth_weaviate
from openai_connection_status import OpenAI 

# Initialize OpenAI client
university_info = """
The University of Washington, founded in 1861 in Seattle, is a public research university
with over 45,000 students across three campuses in Seattle, Tacoma, and Bothell.
As the flagship institution of the six public universities in Washington state,
UW encompasses over 500 buildings and 20 million square feet of space,
including one of the largest library systems in the world.
"""
oai_client = openai_connection_status()
oai_client.embeddings.create(
    model="text-embedding-ada-002",
    input=university_info
)

# Initialize ChromaDB
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('openai_connection_status'),
                                             model_name="text-embedding-ada-002")

chroma_client = chromadb.Client()
vector_store = chroma_client.get_or_create_collection(name="Universities",
                                                      embedding_function=embedding_function)

vector_store.add("uni_info", documents=university_info)

# Initialize TruLens
tru = Tru()

class RAG_from_scratch:
    @instrument
    def retrieve(self, query: str) -> list:
        """
        Retrieve relevant text from vector store.
        """
        results = vector_store.query(
            query_texts=query,
            n_results=2
        )
        return results['documents'][0]

    @instrument
    def generate_completion(self, query: str, context_str: list) -> str:
        """
        Generate answer from context.
        """
        completion = oai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "user",
                 "content":
                     f"We have provided context information below. \n"
                     f"---------------------\n"
                     f"{context_str}"
                     f"\n---------------------\n"
                     f"Given this information, please answer the question: {query}"
                 }
            ]
        ).choices[0].message.content
        return completion

    @instrument
    def query(self, query: str) -> str:
        context_str = self.retrieve(query)
        completion = self.generate_completion(query, context_str)
        return completion

rag = RAG_from_scratch()

# Initialize TruLens Feedbacks
fopenai = Feedback.Provider.OpenAI(api_key=os.environ.get('openai_connection_status'))
grounded = Groundedness(groundedness_provider=fopenai)

f_groundedness = (
    Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness")
    .on(Select.RecordCalls.retrieve.rets.collect())
    .on_output()
    .aggregate(grounded.grounded_statements_aggregator)
)

f_qa_relevance = (
    Feedback(fopenai.relevance_with_cot_reasons, name="Answer Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on_output()
)

f_context_relevance = (
    Feedback(fopenai.qs_relevance_with_cot_reasons, name="Context Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on(Select.RecordCalls.retrieve.rets.collect())
    .aggregate(np.mean)
)

# Initialize TruLens Custom App
tru_rag = TruCustomApp(rag,
                       app_id='RAG v1',
                       feedbacks=[f_groundedness, f_qa_relevance, f_context_relevance])

# Streamlit App
def streamlit_app() -> None:
    st.set_page_config(
        page_title="📤 retrieval",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()
        user_auth_openai()
        user_auth_weaviate()
        default_auth_weaviate()

    st.title("📤 Retrieval")

    if st.session_state.get("OPENAI_STATUS") != ("success", None):
        st.warning("""
            You need to provide an OpenAI API key.
            Visit `Information` to connect.    
        """)
        return

    if st.session_state.get("WEAVIATE_STATUS") != ("success", None):
        st.warning("""
            You need to connect to Weaviate.
            Visit `Information` to connect.    
        """)
        return

    dr = client.instantiate_driver()

    retrieval_form_container(dr)

    if history := st.session_state.get("history"):
        history_display_container(history)
    else:
        st.session_state["history"] = list()

    # Example question
    user_question = st.text_input("Ask a question:")
    if st.button("Get Answer"):
        with tru_rag as recording:
            rag.query(user_question)

    # Display the TruLens Leaderboard
    leaderboard_button = st.button("Show Leaderboard")
    if leaderboard_button:
        tru.get_leaderboard(app_ids=["RAG v1"])

    # Display the TruLens Dashboard
    dashboard_button = st.button("Show Dashboard")
    if dashboard_button:
        tru.run_dashboard()

# New Page for Weaviate ChatVectorDBChain
def weaviate_chat_app() -> None:
    st.title("Weaviate ChatVectorDBChain Demo")
    st.write("Please enter a question or dialogue to get started!")

    client_weaviate = weaviate.Client("http://localhost:8080")
    vectorstore_weaviate = Weaviate(client_weaviate, "PodClip", "content")

    openai_weaviate = OpenAI(temperature=0.2, openai_api_key=os.environ.get('openai_connection_status'))
    qa_weaviate = ChatVectorDBChain.from_llm(openai_weaviate, vectorstore_weaviate)

    chat_history_weaviate = []

    while True:
        query_weaviate = st.text_input("Enter a question:")
        if st.button("Get Answer"):
            result_weaviate = qa_weaviate({"question": query_weaviate, "chat_history": chat_history_weaviate})
            st.write(f"Answer: {result_weaviate['answer']}")
            chat_history_weaviate = [(query_weaviate, result_weaviate['answer'])]

# Create the Streamlit app with multiple pages
app_pages = {
    "Retrieval": streamlit_app,
    "Weaviate Chat": weaviate_chat_app,
}

# Page selection
selected_page = st.sidebar.selectbox("Select a page", list(app_pages.keys()))

# Run the selected app page
app_pages[selected_page]()
