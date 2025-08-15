import os
import smtplib
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from schema import CampaignState, EmailDraft 
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_email(state: CampaignState) -> CampaignState:
    """
    Use OpenAI to generate a recruitment email draft.
    """
    messages = [
        SystemMessage(content="You are a professional campaign email generator."),
        HumanMessage(
            content=(
                f"""
            Using the information below, draft a friendly yet professional email inviting the candidate to discuss a new opportunity.  
            - **Role Title:** {state['role']} 
            - **Location:** {state['location']}
            - **Minimum Experience:** {state['experience_years']} years  
            - **Key Skills (comma‑separated):** {state['skills']}  
            - **Theme:** {state['theme']}
            **Requirements for the email:**  
            1. **Subject line** that mentions the role and location along with theme.  
            2. **Personalized greeting**.  
            3. **Intro paragraph** referencing their Role and Skill expertise and minimum years of experience.  
            4. **Bullet list** summarizing:  
            - Role title  
            - Location (hybrid/remote/on‑site)  
            - Experience requirement  
            - Core skills  
            5. **Call to action** proposing 1–2 time slots to discuss, anytime next week.  
            6. **Polite closing** with your name, title, and company.

            **Output Format (markdown):**  
            Subject: <your subject line>

            Dear Candidate,

            <email body>

            Warm regards,  
            <Asoft Team>  
            <Human Resource>
        """
            )
        ),
    ]
    llm_struc = llm.with_structured_output(EmailDraft)
    response = llm_struc.invoke(messages)
    state['subject'] = response.subject
    state['body'] = response.body
    state['email_draft'] = str(response.body)
    logger.info(f"Generated email draft: {state['email_draft']}")
    # prev = state.get("messages", [])  # this must be a list of ChatMessages / dicts with role+content
    # combined = add_messages(prev, messages + [response])
    # store it back
    # state["messages"] = combined
    return state

def edit_email_draft(state: CampaignState) -> CampaignState:
    """
    Allow the user to edit the generated email draft.
    """
    messages = [
        SystemMessage(content="You are a professional campaign email editor."),
        HumanMessage(
            content=(
                f"""Here is the generated email draft:\n{state['email_draft']}\n"
                Please edit the draft based on the feedback: {state['email_feedback']}\n"""
            )
        ),
    ]
    llm_struc = llm.with_structured_output(EmailDraft)
    response = llm_struc.invoke(messages)
    state['subject'] = response.subject
    state['body'] = response.body
    state['email_draft'] = str(response.body)
    logger.info(f"Edited email draft: {state['email_draft']}")
    return state

def send_email(state: CampaignState) -> CampaignState:
    """
    Send the generated email draft via SMTP to all filtered candidates.
    """
    try:    
        # for dest in state['emails']:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(os.getenv('EMAIL_SENDER'), os.getenv('EMAIL_PASSWORD'))
            subject = f"{str(state['subject'])}"
            body    = f"{str(state['body'])}"
            message = f"Subject: {subject}\n\n{body}"
            s.sendmail(os.getenv('EMAIL_SENDER'), "akki.ss22x25@gmail.com", message)
    except Exception as e:
        logger.error(e)
    return state