import os
import json
import pandas as pd
import streamlit as st
from openai import OpenAI
import weaviate
from tenacity import retry, stop_after_attempt, wait_random_exponential
from trulens_eval import Tru, Feedback, Select
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as fOpenAI
import numpy as np
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import chromadb
from trulens_eval.tru_custom_app import TruCustomApp, instrument
from hamilton.function_modifiers import extract_fields
from hamilton.htypes import Collect, Parallelizable

# University information
university_info = """
The University of Washington, founded in 1861 in Seattle, is a public research university
with over 45,000 students across three campuses in Seattle, Tacoma, and Bothell.
As the flagship institution of the six public universities in Washington state,
UW encompasses over 500 buildings and 20 million square feet of space,
including one of the largest library systems in the world.
"""

# OpenAI client setup
oai_client = OpenAI()

# Create OpenAI embeddings for university information
oai_client.embeddings.create(
    model="text-embedding-ada-002",
    input=university_info
)

# OpenAIEmbeddingFunction setup with st.secrets
embedding_function = OpenAIEmbeddingFunction(
    api_key=st.secrets["openai"]["api_key"],
    model_name="text-embedding-ada-002"
)

# ChromaDB setup
chroma_client = chromadb.Client()
vector_store = chroma_client.get_or_create_collection(name="Universities",
                                                      embedding_function=embedding_function)

vector_store.add("uni_info", documents=university_info)

# Trulens setup
tru = Tru()

# RAG from scratch class
class RAG_from_scratch:
    @instrument
    def retrieve(self, query: str) -> list:
        results = vector_store.query(
            query_texts=query,
            n_results=2
        )
        return results['documents'][0]

    @instrument
    def generate_completion(self, query: str, context_str: list) -> str:
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

# Trulens feedback setup
fopenai = fOpenAI()

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

# Trulens custom app setup
tru_rag = TruCustomApp(rag,
                       app_id='RAG v1',
                       feedbacks=[f_groundedness, f_qa_relevance, f_context_relevance])

# Streamlit app
def app() -> None:
    st.set_page_config(
        page_title="📤 retrieval",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    with st.sidebar:
        # Add any sidebar elements or connections you need
        pass

    st.title("📤 Retrieval")

    # Your existing Streamlit code for retrieval_form_container
    # ...

    # Trulens recording
    with tru_rag as recording:
        rag.query("When was the University of Washington founded?")

    # Your existing Streamlit code for history_display_container
    # ...


if __name__ == "__main__":
    app()
