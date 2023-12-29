import streamlit as st

import client
from authentication import (
    default_auth_weaviate,
    user_auth_weaviate,
    user_auth_openai,
    openai_connection_status,
    weaviate_connection_status,
)


def app() -> None:
    st.set_page_config(
        page_title="Vector Librarian",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    st.title("📚 AI VA HM")

    dr = client.instantiate_driver()

    st.markdown("""
    🚀 Introducing AI VA HM: Your Ultimate Medical Data Companion! 🚑

AI VA HM is not just a medical data application; it's a cutting-edge Retrieval Augmented Generative (RAG) marvel crafted with precision using Python, Weaviate, OpenAI, and the powerful Hamilton technology.

✨ Key Features:

Smart Data Verification 🤖🔍:
Ensure the utmost accuracy and reliability of your medical data with our intelligent verification system.

Instant Search Capability 🚀🔗:
Swiftly navigate through vast medical datasets using the power of RAG, delivering precise and relevant results instantly.

Dynamic Data Updates 🔄💡:
Keep your medical vector database up-to-date effortlessly. Our system allows seamless and efficient data updates.

Revolutionary Audio Interaction 🎙️👂:
Interact with your data like never before! Use voice commands for a hands-free, intuitive experience.

Effortless Note Management 🗒️📈:
Let AI assist you in creating and managing comprehensive notes and summaries effortlessly.

Decision-Making Made Fun 🤔🎉:
Generate insightful decisions using the power of both retrieval and generative models, making complex tasks enjoyable.

Emotive Emoji Enhancements 🌟🎭:
Express and understand information with a glance! Our application uses emojis to make data more engaging and user-friendly.

🌐 Why AI VA HM?

Unparalleled Accuracy: Trust our intelligent verification system for precise and reliable medical information.

Lightning-Fast Search: Experience instant results with our RAG-powered search capabilities.

Seamless Updates: Keep your database current effortlessly with our dynamic update features.

Intuitive Interaction: Enjoy a hands-free experience with our advanced audio interaction system.

Decision Fun: Make decisions a breeze with the perfect blend of retrieval and generative technologies.

Emotive Experience: Understand and convey information effortlessly with our expressive emoji-enhanced interface.

Join the future of medical data management with AI VA HM! 🚀🌍💙
    """)

    st.header("🔑Credentials")

    left, right = st.columns(2)

    with left:
        st.subheader("OpenAI")
        st.markdown("""
            This application uses OpenAI for text embeddings and generative answers.
            Enter your API key below.
                    
            [Get started with OpenAI](https://platform.openai.com/account/api-keys)
        """)
        st.warning("Your OpenAI account will be charged for your usage.")
        user_auth_openai()

    with right:
        st.subheader("Weaviate")
        st.markdown("""
            The demo connects to a default Weaviate instance.
            Enter your credentials to connect to your instance.
                    
            [Get started with Weaviate](https://console.weaviate.cloud/)
        """)
        default_auth_weaviate()
        user_auth_weaviate()

    
    with st.sidebar:
        openai_connection_status()
        weaviate_connection_status()

        if st.session_state.get("WEAVIATE_DEFAULT_INSTANCE") is False:
            client.initialize(
                dr=dr,
                weaviate_client=st.session_state.get("WEAVIATE_CLIENT")
            )


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()
