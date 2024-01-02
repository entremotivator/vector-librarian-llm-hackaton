import weaviate
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from hamilton.function_modifiers import extract_fields
from hamilton.htypes import Collect, Parallelizable
from backend.ingestion import _get_embeddings__openai

def chatbot_backend(rag_query, all_chunks, prompt_to_reduce_summaries, summarize_model_name):
    # Backend processing goes here
    pass
