import streamlit as st

from common import sidebar


def app() -> None:
    st.set_page_config(
        page_title="Vector Librarian",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    st.title("📚 Vector Librarian")
    st.header("Hello World")
     
    sidebar()


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()
