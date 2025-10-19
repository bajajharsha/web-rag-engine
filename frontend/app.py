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
    .source-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #1E88E5;
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


def query_documents(query: str, top_k: int = 5) -> Optional[dict]:
    """Query the RAG system"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query", json={"query": query, "top_k": top_k}, timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying documents: {str(e)}")
        return None


def main():
    # Header
    st.markdown(
        '<div class="main-header">🔍 Web RAG Engine</div>', unsafe_allow_html=True
    )
    st.markdown("---")

    # Sidebar for URL Ingestion
    with st.sidebar:
        st.markdown("### 📥 URL Ingestion")
        st.markdown("Add documents to your knowledge base")

        url_input = st.text_input(
            "Enter URL",
            placeholder="https://example.com/article",
            help="Enter a valid URL to scrape and add to the knowledge base",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            ingest_button = st.button(
                "🚀 Ingest", type="primary", use_container_width=True
            )
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)

        if ingest_button and url_input:
            with st.spinner("Processing URL..."):
                result = ingest_url(url_input)

                if result:
                    st.success("✅ URL submitted for processing!")
                    with st.container():
                        st.markdown(f"**Job ID:** `{result.get('job_id', 'N/A')}`")
                        st.markdown(f"**Status:** {result.get('status', 'N/A')}")
                        st.info(
                            "💡 The URL is being processed in the background. You can start querying once processing is complete."
                        )

        if clear_button:
            st.rerun()

        # Job Status Section
        st.markdown("---")
        st.markdown("### 📊 Job Status")
        st.info("Background worker processes your URLs automatically")

        # Show recent ingestions if stored in session state
        if "ingestion_history" not in st.session_state:
            st.session_state.ingestion_history = []

        if st.session_state.ingestion_history:
            st.markdown("**Recent Ingestions:**")
            for idx, job in enumerate(st.session_state.ingestion_history[-5:]):
                with st.expander(f"Job {idx + 1}: {job.get('url', 'N/A')[:30]}..."):
                    st.markdown(f"**Job ID:** `{job.get('job_id', 'N/A')}`")
                    st.markdown(f"**Status:** {job.get('status', 'N/A')}")

    # Main Chat Interface
    st.markdown("## 💬 Chat with Your Documents")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Settings
    with st.expander("⚙️ Query Settings"):
        top_k = st.slider(
            "Number of sources to retrieve",
            min_value=1,
            max_value=10,
            value=5,
            help="How many relevant chunks to retrieve from the vector database",
        )

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display sources if available
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    st.markdown("---")
                    st.markdown("### 📚 Sources")
                    for idx, source in enumerate(message["sources"], 1):
                        with st.expander(
                            f"Source {idx}: {source.get('url', 'Unknown')[:50]}..."
                        ):
                            st.markdown(
                                f"**URL:** [{source.get('url', 'N/A')}]({source.get('url', '#')})"
                            )
                            st.markdown(
                                f"**Relevance Score:** {source.get('score', 0):.4f}"
                            )
                            st.markdown("**Content:**")
                            st.text(source.get("content", "No content available"))

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
                response = query_documents(prompt, top_k)

                if response:
                    answer = response.get(
                        "answer", "Sorry, I couldn't generate an answer."
                    )
                    sources = response.get("sources", [])

                    # Display answer
                    st.markdown(answer)

                    # Display sources
                    if sources:
                        st.markdown("---")
                        st.markdown("### 📚 Sources")
                        for idx, source in enumerate(sources, 1):
                            with st.expander(
                                f"Source {idx}: {source.get('url', 'Unknown')[:50]}..."
                            ):
                                st.markdown(
                                    f"**URL:** [{source.get('url', 'N/A')}]({source.get('url', '#')})"
                                )
                                st.markdown(
                                    f"**Relevance Score:** {source.get('score', 0):.4f}"
                                )
                                st.markdown("**Content:**")
                                st.text(source.get("content", "No content available"))

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                else:
                    error_msg = "Sorry, I encountered an error processing your query."
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg, "sources": []}
                    )

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
