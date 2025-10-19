import uuid
from typing import Optional

import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Web RAG Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #424242;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-pending {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
    }
    .status-completed {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
    }
    .status-failed {
        background-color: #FFEBEE;
        border-left: 4px solid #F44336;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def ingest_url(url: str) -> Optional[dict]:
    """Submit URL for ingestion"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest-url", json={"url": url}, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error ingesting URL: {str(e)}")
        return None


def query_documents(
    query: str, session_id: Optional[str] = None, top_k: int = 5
) -> Optional[dict]:
    """Query the RAG system with optional session for conversation history"""
    try:
        payload = {"query": query, "top_k": top_k}
        if session_id:
            payload["session_id"] = session_id

        response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying documents: {str(e)}")
        return None


def main():
    # Initialize session state for session_id (persistent across reruns)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        print(f"🆔 New session created: {st.session_state.session_id}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Header
    st.markdown(
        '<div class="main-header">🔍 Web RAG Engine</div>', unsafe_allow_html=True
    )
    st.markdown("---")

    # Sidebar for URL Ingestion
    with st.sidebar:
        st.markdown("### 📥 Add Document")
        st.markdown("Enter a URL to add to your knowledge base")

        url_input = st.text_input(
            "URL",
            placeholder="https://example.com/article",
            label_visibility="collapsed",
        )

        ingest_button = st.button(
            "🚀 Add to Knowledge Base", type="primary", use_container_width=True
        )

        if ingest_button and url_input:
            with st.spinner("Processing URL..."):
                result = ingest_url(url_input)

                if result:
                    st.success("✅ URL submitted for processing!")
                    st.info(
                        "💡 The URL is being processed in the background. You can start querying once processing is complete."
                    )

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info(
            "This RAG system allows you to query documents from URLs using semantic search and AI-powered responses."
        )

        st.markdown("---")
        st.markdown("### 💬 Chat Controls")
        if st.button(
            "🔄 New Chat", help="Start a new conversation", use_container_width=True
        ):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

    # Main Chat Interface
    st.markdown("## 💬 Chat with Your Documents")

    # Default top_k value
    top_k = 5

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_documents(
                    prompt, session_id=st.session_state.session_id, top_k=top_k
                )

                if response:
                    answer = response.get(
                        "answer", "Sorry, I couldn't generate an answer."
                    )

                    # Display answer
                    st.markdown(answer)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                else:
                    error_msg = "Sorry, I encountered an error processing your query."
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
