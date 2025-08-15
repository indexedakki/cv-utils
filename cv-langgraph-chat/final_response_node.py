from state_types import MyState 
from typing import TypedDict, Literal, List,Optional, Tuple
import json
from prompt import final_response_prompt
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger
LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)
# logger.info("Starting FastAPI application...")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4", temperature=0)




def final_response_node(state: MyState) -> MyState:
    query = state["query"]
    reranked = state.get("reranked_results", [])

    reranked_json = json.dumps(reranked, indent=2)

    prompt = final_response_prompt.format(
        query=query,
        reranked_json=reranked_json
    )

    # print("\n📤 Final prompt sent to LLM:\n", prompt)

    response = llm.invoke(prompt)
    final_reply = response.content.strip()
    # Append query and response to messages
    updated_messages = state.get("messages", []) + [query, final_reply]
     
    # Update chat history
    chat_history = state.get("chat_history", [])
    chat_history.append((query, final_reply))
    print(f"Bot Response---->:",final_reply)
    logger.info(f"Bot Response---->:{final_reply}")

    

    return {
        **state,
        "final_response": final_reply,
        "messages": updated_messages,
        "chat_history": chat_history
    }

