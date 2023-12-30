import json
import pandas as pd
import streamlit as st
import requests

def fetch_journal_data(api_key: str, search_query: str = "") -> dict:
    base_url = "https://medical-articles-live.p.rapidapi.com/journals"
    url = f"{base_url}?search={search_query}"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "medical-articles-live.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Request failed with status code: {response.status_code}")
        return {}

def retrieval_form_container(api_key) -> None:
    st.title("🏥 Medical Journals Explorer")

    left, right = st.columns(2)
    with left:
        form = st.form(key="journal_search_query")
        search_query = form.text_input("Enter search query for medical journals:", "")

    with right:
        st.write("Search Parameters")
        search_button = form.form_submit_button("Search")

    if search_button:
        with st.spinner("Searching..."):
            journal_data = fetch_journal_data(api_key, search_query)
            st.session_state["journal_data"] = journal_data

def display_journal_data(journal_data):
    if journal_data:
        st.write("Information about Medical Journals:")
        st.json(journal_data)
    else:
        st.warning("No data available. Please try another search.")

def app() -> None:
    st.set_page_config(
        page_title="🏥 Medical Journals Explorer",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    st.title("🏥 Medical Journals Explorer")

    # Replace 'your_api_key' with your actual RapidAPI key
    api_key = "c1ea464588msh41b2e1ac29e0f2ep1cd0ffjsn08a7ad695581"

    retrieval_form_container(api_key)

    journal_data = st.session_state.get("journal_data", {})
    display_journal_data(journal_data)

if __name__ == "__main__":
    app()
