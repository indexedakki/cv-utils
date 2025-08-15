import os
import smtplib
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from schema import CampaignState, ExtractionResponse
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def parse_input(state: CampaignState) -> CampaignState:
    """
    Use the LLM to extract role, experience_years, skills, and theme from a raw sentence.
    Returns JSON with fields.
    """
    messages = [
        SystemMessage(content="You are helpful assisstant to extract role, skills, experience, location and theme from user message"),
        HumanMessage(
            content=(
                "Extract the following fields from the user message:"
                "role, experience_years, skills, location, theme."
                f"\nMessage: {state['raw_text']}"
            )
        ),
    ]
    llm_struc = llm.with_structured_output(ExtractionResponse)
    response = llm_struc.invoke(messages)

    state['role'] = response.role
    state['experience_years'] = response.experience_years
    state['skills'] = response.skills
    state['location'] = response.location
    state['theme'] = response.theme
    ai_msg = AIMessage(content=response.json())

    # 3) Merge it into your existing history list
    #    note: add_messages(left: List[BaseMessage], right: List[BaseMessage]) -> List[BaseMessage]
    # state['messages'] = add_messages(state['messages'], [ai_msg])
    logger.info(f"Parsed input: {response}")
    return state