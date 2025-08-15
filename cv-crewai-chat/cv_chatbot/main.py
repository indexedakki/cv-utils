#!/usr/bin/env python
# pylint: disable=W0611, E1111
"""
Interactive CLI for CVChatbot with memory and logger setup.
"""
import sys
import os
import uuid
import time
import json
import warnings
from dotenv import load_dotenv
from fastapi import Header, File, UploadFile, APIRouter, Form, Depends, Query
from fastapi.responses import JSONResponse
from mem0 import Memory
from logger_setup import setup_logger
from cv_chatbot.crew import CvChatbot
from cv_chatbot.utils.json_to_text import json_to_text
from cv_chatbot.utils.download_blob import download_from_blob

from .models import ChatRequest, ChatResponse, Message

from crewai_tools import RagTool
from .utils.format_response import format_response, type_check
from .config import RAG_CONFIG, CHAT_CONFIG
# Suppress distracting syntax warnings from pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load environment variables
load_dotenv()

# Constants
LOG_PATH = "logs/app.log"


router = APIRouter(
    prefix='/cv_chatbot',
    tags=['cv_chatbot']
)

def initialize_memory(config: dict) -> Memory:
    """
    Initialize memory from the given configuration.

    Args:
        config (dict): Configuration for the vector store.

    Returns:
        Memory: An instance of Memory.
    """
    return Memory.from_config(config)


@router.get("/store_embeddings")
def store_embeddings():
    download_from_blob()
    rag_tool = RagTool(config=RAG_CONFIG)
    EMBEDDINGS_DIR = "summaries"
    for file in os.listdir(EMBEDDINGS_DIR):
        if file.endswith(".txt"):
            file_path = os.path.join(EMBEDDINGS_DIR, file)
            rag_tool.add(
                        data_type="text_file",
                        source=file_path,
                        metadata={
                            "source": file_path,
                            "category": "resume_data",
                        }
                    )
    return {"message": "Embeddings stored successfully."}     


@router.post("/chat")
def run(user_input: str = Query(..., description="Text from the user"),
         user_uuid: str         = Query(..., alias="id", description="UUID from the client")) -> None:
    """
    Launch the interactive chat session. Type 'exit', 'quit', or 'bye' to end.
    """
    memory = initialize_memory(CHAT_CONFIG)
    logger = setup_logger(__name__, LOG_PATH)

    while True:
        start_time = time.time()
        input = user_input
        if input.strip().lower() in {"exit", "quit", "bye"}:
            response = "Chatbot: Goodbye! It was nice talking to you."
            return response

        memory.add(f"User: {input}", user_id=user_uuid)
        relevant_info = memory.search(
            query=input,
            limit=3,
            user_id=user_uuid,
        )
        context = "\n".join(relevant_info)
        logger.info("Starting conversation with user: %s", user_uuid)
        logger.debug("User input: %s", input)

        inputs = {"user_message": input, "context": context}

        type_q = type_check(input)
        crew = CvChatbot().crew()
        response = crew.kickoff(
            inputs=inputs)
        logger.debug("Crew response: %s", response)
        final_response = format_response(response, type_q)

        usasge_metrics = crew.usage_metrics
        total_tokens = usasge_metrics.prompt_tokens
        completion_tokens = usasge_metrics.completion_tokens
        cached_prompt_tokens = usasge_metrics.cached_prompt_tokens
        end_time = time.time()
        duration = end_time - start_time
        logger.info("Response time: %.2f seconds", duration)
        logger.info("Total tokens: %d, Completion tokens: %d, Cached tokens: %d",
                    total_tokens, completion_tokens, cached_prompt_tokens)
        

        memory.add(f"Assistant: {final_response}", user_id=user_uuid)
        # print(f"Assistant: {response}")
        logger.debug("Assistant response: %s", final_response)

        return final_response


def train() -> None:
    """
    Train the CVChatbot crew for a given number of iterations.

    Args:
        iterations (int): Number of training iterations.
        filename (str): File name to save training logs or output.
    """
    memory = initialize_memory(CHAT_CONFIG)
    logger = setup_logger(__name__, LOG_PATH)
    
    iterations = 2
    filename = "trained_agents.pkl"
    while True:
        query = input("User: ")
        if query.strip().lower() in {"exit", "quit", "bye"}:
            response = "Chatbot: Goodbye! It was nice talking to you."
            return response

        memory.add(f"User: {query}", user_id="Lennex")
        relevant_info = memory.search(
            query=query,
            limit=3,
            user_id="Lennex",
        )
        context = "\n".join(relevant_info)

        logger.debug("User query: %s", query)

        inputs = {"user_message": query, "context": context}
        crew = CvChatbot().crew()
        response = crew.train(n_iterations=iterations, 
                        inputs=inputs, 
                        filename=filename
      )


        usasge_metrics = crew.usage_metrics
        total_tokens = usasge_metrics.prompt_tokens
        completion_tokens = usasge_metrics.completion_tokens
        cached_prompt_tokens = usasge_metrics.cached_prompt_tokens
        logger.info("Total tokens: %d, Completion tokens: %d, Cached tokens: %d",
                    total_tokens, completion_tokens, cached_prompt_tokens)
        

        memory.add(f"Assistant: {response}", user_id="Assistant")
        logger.debug("Assistant response: %s", response)

def run_cli() -> None:
    """
    Launch the interactive chat session. Type 'exit', 'quit', or 'bye' to end.
    """
    memory = initialize_memory(CHAT_CONFIG)
    logger = setup_logger(__name__, LOG_PATH)
    while True:
        query = input("User: ")
        if query.strip().lower() in {"exit", "quit", "bye"}:
            response = "Chatbot: Goodbye! It was nice talking to you."
            return response

        memory.add(f"User: {query}", user_id="Lennex22")
        relevant_info = memory.search(
            query=query,
            limit=3,
            user_id="Lennex22",
        )
        
        context = "\n".join(relevant_info)

        logger.debug("User query: %s", query)

        inputs = {"user_message": query, "context": context}
        crew = CvChatbot().crew()
        response = crew.kickoff(
            inputs=inputs)


        usasge_metrics = crew.usage_metrics
        total_tokens = usasge_metrics.prompt_tokens
        completion_tokens = usasge_metrics.completion_tokens
        cached_prompt_tokens = usasge_metrics.cached_prompt_tokens
        logger.info("Total tokens: %d, Completion tokens: %d, Cached tokens: %d",
                    total_tokens, completion_tokens, cached_prompt_tokens)
        

        memory.add(f"Assistant: {response}", user_id="Assistant")
        logger.debug("Assistant response: %s", response)

# train()
# run_cli()
# if __name__ == "__main__":
#     if len(sys.argv) == 1:
#         run()
#     elif len(sys.argv) == 3:
#         try:
#             iterations = int(sys.argv[1])
#         except ValueError:
#             print("Error: iterations must be an integer.")
#             sys.exit(1)
#         train(iterations, sys.argv[2])
#     else:
#         print("Usage: main.py [iterations filename]")
#         sys.exit(1)
