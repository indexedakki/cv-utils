import os
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from schema import CampaignState
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_response(state: CampaignState) -> CampaignState:
    """
    Use the LLM to generate a response based on the current state.
    """
    messages = [
        SystemMessage(content="You are a response generator."),
        HumanMessage(
            content=(
                f"""Generate a response based on the user query, you are not supposed to draft a mail if user tells you"
                **User Query:** {state['raw_text']}
                **If user query is about orgainizing campaign, then reply with emails have been sent to concerned candidates**"
                **Else if user query is generic, then reply as per user query**"""
            )
        ),
    ]
    response = llm.invoke(messages)
    # state['messages'] = add_messages(state['messages'], [AIMessage(content=response.content)])
    logger.info(f"Generated response: {response.content}")
    state['response'] = str(response.content)
    return state