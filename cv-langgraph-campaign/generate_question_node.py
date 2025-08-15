import os
import smtplib
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from schema import CampaignState, GenerateQuestion
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_question_chatbot(state: CampaignState) -> CampaignState:
    """
    Generate questions for missing fields from the user input.
    """
    messages = [
        SystemMessage(content="You are a helpful assistant that generates questions for missing fields."),
        HumanMessage(
            content=(
                f"Generate a question for the following field if missing: "
                f"Field: = {state['current_field']}\n"
                f"If any field is missing or invalid, ask user to provide it."
                f"If he doesn't want to provide it ask him to enter blank space"
            )
        ),
    ]
    llm_struc = llm.with_structured_output(GenerateQuestion)
    response = llm_struc.invoke(messages)

    state["current_field_question"] = str(response.question)
    logger.info(f"Generated question: {response}")

    return state