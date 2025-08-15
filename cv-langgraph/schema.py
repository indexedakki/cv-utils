from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
# -----------------------------
# LangGraph State Definition
# -----------------------------
class CampaignState(TypedDict):
    # messages: Annotated[List[str], add_messages]
    raw_text: str             # initial user sentence
    role: str                 # job role
    experience_years: str     # minimum experience
    location: str
    skills: str               # required skills
    theme: str                # campaign theme
    candidates: List[str]
    email_draft: str            # chosen email content
    emails: List[str]
    action: str
    subject: str
    body: str
    similar_candidates: List[str]
    response: str
    email_feedback: str
    validate: bool = False
    current_field_question: str
    current_field: str
    previous_field: Optional[str] = None
    missing_fields: List[str]
    total_missing_field: int
    first_run: bool = False

class CampaignRequest(BaseModel):
    user_input: str
    session_id: str | None = None

class SendEmail(BaseModel):
    email_with_candidates: Dict[str, Any]

class ChatbotResponse(BaseModel):
    action: str = Field(description="""Action to take next: 
                        "generic": for direct response, 
                        "generate_campaign" for campaign email""")

class ExtractionResponse(BaseModel):
    role: str = Field(description="Role of candidate, **if given else leave it empty** **Example- Python Devloper, " \
    "Data Engineer, Solution Architect **")
    experience_years: int = Field(description="Years of experience mentioned **if given else -1**")
    skills: List[str] = Field(description="List of skills mentioned **if given else leave it empty**")
    location: str = Field(description="location mentioned **if given else leave it empty**")
    theme: str = Field(description="Theme of campaign **if given else leave it empty** **Example- AI for Future**")

class FilteredCandidate(BaseModel):
    name: List[str] = Field(description="Name of the candidate")
    email: List[str] = Field(description="Email of the candidate")
    location: List[str] = Field(description="Location of candidate")
    experience: List[str] = Field(description="Experience of candidate")

class EmailDraft(BaseModel):
    subject: str = Field(description="Subject of email")
    body: str = Field(description="Body of email")

class GenerateQuestion(BaseModel):
    question: str = Field(description="Asking user to provide missing fields or confirm if they want to skip them")