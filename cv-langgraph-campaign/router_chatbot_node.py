import os
import smtplib
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from schema import CampaignState, ChatbotResponse
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def router_chatbot(state: CampaignState) -> CampaignState:
    """
    Use the LLM to decide what to do next based on the user query.
    """
    messages = [
        SystemMessage(content="You are a decision-making chatbot for recruitment campaigns."),
        HumanMessage(
            content=(
                "Given the user query, decide what to do next. "
                "You can choose from the following actions: "
                "generic: Send a response directly to user, "
                "generate_campaign: Start with generating a campaign email, "
                f"user query: {state['raw_text']}"
            )
        ),
    ]
    llm_struc = llm.with_structured_output(ChatbotResponse)
    response = llm_struc.invoke(messages)
    logger.info(f"Decided next action: {response}")
    state["action"] = str(response.action)
    # state['messages'] = add_messages(state['messages'], [AIMessage(content=str(response))])
    return state