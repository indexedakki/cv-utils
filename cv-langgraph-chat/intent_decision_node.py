from state_types import MyState 
from typing import TypedDict, Literal, List,Optional, Tuple
from prompt import intent_prompt, genric_prompt
import openai
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)
logger.info("Starting FastAPI application...")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4", temperature=0)



def intent_decision_node(state: MyState) -> MyState:
    formatted_prompt = intent_prompt.format(messages="\n".join(state["messages"]), query=state["query"])
    response = llm.invoke(formatted_prompt).content.strip().lower()

    logger.info(f"User Query : {state['query']}")
    logger.info(f"LLM Intent Detected : {response}")

    print(f"User Query---->: {state['query']}")
    print(f"LLM Intent Detected---->: {response}")

    intent = response if response in ["new_question", "follow_up", "generic"] else "new_question"
    return {**state, "intent": intent}


def handle_new_question(state: MyState) -> MyState:
    # print("Handling new question")
    return state

def handle_follow_up(state: MyState) -> MyState:
    # print("Handling follow up  question")
    # Combine last few messages for better context
    history = state.get("chat_history", [])
    # context = "\n".join(state["messages"][-6:])  # last 3 Q-A pairs
    context = "\n".join([f"User: {q}\nBot: {a}" for q, a in history[-3:]])  # last 3 turns
    new_query = state["query"]
    updated_query = f"{context}\nFollow-up: {new_query}"
    return {**state, "query": updated_query}


def handle_generic_message(state: MyState) -> MyState:
    logger.info("Handling generic question")

    # print("Handling generic question")
    query = state["query"]
    prompt = genric_prompt.format(query=query)
    response = llm.invoke(prompt).content.strip()
    return {**state, "final_response": response}