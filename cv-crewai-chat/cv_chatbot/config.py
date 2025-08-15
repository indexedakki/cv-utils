# Create a RAG tool with custom configuration
RAG_CONFIG = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o",
            "number_documents": 15,  # Use 5 documents as context for the LLM

        },

    },
    "embedding_model": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-ada-002",
        }
    },
    "vectordb": {
        "provider": "chroma",
        "config": {
            "collection_name": "cv_chatbot",
            "dir": "./chroma_cv_db",
        }
    },
    "chunker": {
        "chunk_size": 1000,
        "chunk_overlap": 50,
        "length_function": "len",
        "min_chunk_size": 500
    }
}

CHAT_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "chatbot_memory",
            "path": "./chroma_chat_db",
        },
    },
}
