import openai
import streamlit as st

import client


def sidebar():
    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API key", 
            type="password",
            value=st.session_state.get("OPENAI_API_KEY", ""),
            help="[docs](https://platform.openai.com/docs/api-reference/introduction)",
        )
        st.session_state["OPENAI_API_KEY"] = openai_api_key

        weaviate_url = st.text_input(
            "Weaviate Cluster URL",
            value=st.session_state.get("WEAVIATE_URL", ""),
            help="[docs](https://weaviate.io/developers/wcs/quickstart)"
        )
        st.session_state["WEAVIATE_URL"] = weaviate_url

        weaviate_api_key = st.text_input(
            "Weaviate API key",
            type="password",
            value=st.session_state.get("WEAVIATE_API_KEY", ""),
            help="[docs](https://weaviate.io/developers/wcs/quickstart)"
        )
        st.session_state["WEAVIATE_API_KEY"] = weaviate_api_key

        if st.button("Initialize"):
            openai.api_key = st.session_state.get("OPENAI_API_KEY")
            client.initialize(
                weaviate_url=st.session_state.get("WEAVIATE_URL"),
                weaviate_api_key=st.session_state.get("WEAVIATE_API_KEY"),
            )
