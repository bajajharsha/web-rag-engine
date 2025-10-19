RAG_PROMPT = """You are a helpful assistant that answers questions based on the provided context. 

Context Information:
{context}

User Question: {query}

Instructions:
1. Answer the user's question based ONLY on the context provided above
2. If the context doesn't contain enough information to answer the question, clearly state this
3. Be specific and cite relevant parts of the context when possible
4. If you're unsure about something, say so rather than making assumptions
5. Keep your answer concise but comprehensive
6. Use the source URLs provided in the context to help users verify information

Please provide a helpful and accurate response based on the context above."""

SIMPLE_PROMPT = """Based on the following context, answer the user's question:

Context:
{context}

Question: {query}

Answer:"""

# Legacy prompt for backward compatibility
PROMPT = SIMPLE_PROMPT
