import json
import pandas as pd
import streamlit as st

import chatbot_client
from authentication import openai_connection_status, weaviate_connection_status

def chatbot_form_container(dr) -> None:
    """Container to enter chatbot query and send /chatbot_summary GET request."""
    left, right = st.columns(2)
    with left:
        form = st.form(key="chatbot_query")
        chatbot_query = form.text_area(
            "Chatbot Query", value="What are the symptoms of a common cold?"
        )

    with right:
        st.write("Chatbot Search Parameters")
        retrieve_top_k = st.number_input(
            "top K", value=3, help="The number of responses to consider for the chatbot"
        )
        chatbot_search_alpha = st.slider(
            "alpha",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            help="0: Keyword. 1: Vector.\n[Weaviate docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)",
        )

    if form.form_submit_button("Chat"):
        with st.status("Running"):
            try:
                response = chatbot_client.chatbot_summary(
                    dr=dr,
                    weaviate_client=st.session_state.get("WEAVIATE_CLIENT"),
                    chatbot_query=chatbot_query,
                    chatbot_search_alpha=chatbot_search_alpha,
                    retrieve_top_k=int(retrieve_top_k),
                )
                st.session_state["chat_history"].append(dict(query=chatbot_query, response=response))
            except Exception as e:
                st.error(f"Error during chatbot interaction: {str(e)}")

def chat_history_display_container(chat_history):
    if len(chat_history) > 1:
        st.header("Chat History")
        max_idx = len(chat_history) - 1
        history_idx = st.slider("History", 0, max_idx, value=max_idx, label_visibility="collapsed")
        entry = chat_history[history_idx]
    else:
        entry = chat_history[0]

    st.download_button(
        "Download Chat History",
        data=json.dumps(chat_history),
        file_name="chat-history.json",
        mime="application/json"
    )

    st.subheader("Query")
    st.write(entry["query"])

    st.subheader("Response")
    st.write(entry["response"]["chatbot_summary"])

    df = pd.DataFrame(entry["response"]["all_responses"])
    df = df.set_index("response_id")
    df = df.rename(columns=dict(
        score="Relevance",
        response_index="Response Index",
        document_file_name="File name",
        content="Content",
        summary="Summary"
    ))

    st.info("Double-click cell to read full content")
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_order=("Relevance", "Response Index", "File name", "Content", "Summary"),
        column_config={col: st.column_config.Column(width="small") 
                       for col in ("Relevance", "Response Index", "File name", "Content", "Summary")
                      }
    )

def chatbot_app() -> None:
    st.set_page_config(
        page_title="💬 Chatbot",
        page_icon="💬",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()

    st.title("💬 Chatbot")

    if st.session_state.get("OPENAI_STATUS") != ("success", None):
        st.warning("""
            You need to provide an OpenAI API key.
            Visit `Information` to connect.    
        """)
        return
    
    dr = chatbot_client.instantiate_chatbot_driver()

    chatbot_form_container(dr)

    if chat_history := st.session_state.get("chat_history"):
        chat_history_display_container(chat_history)
    else:
        st.session_state["chat_history"] = list()

if __name__ == "__main__":
    chatbot_app()
