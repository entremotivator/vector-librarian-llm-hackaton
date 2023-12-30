import streamlit as st
import requests
from pathlib import Path

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

# Replace 'your_api_key' with your actual RapidAPI key
api_key = "678c90fecfmsh3ce9e4abad24c65p1f90f5jsn210c8c654b35"

# Streamlit app
st.title("Medical Journals Information")

# Search input
search_query = st.text_input("Enter a search query for medical journals:", "")

# Fetch journal data based on search query
journal_data = fetch_journal_data(api_key, search_query)

if journal_data:
    st.write("Information about Medical Journals:")
    st.json(journal_data)
else:
    st.warning("Failed to fetch journal data. Please check your API key and try again.")
