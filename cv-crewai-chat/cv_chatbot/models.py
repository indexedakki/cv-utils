# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date

class ChatRequest(BaseModel):
    id: str
    user_input: str

class Message(BaseModel):
    id: str
    text: str
    sender: str

class ChatResponse(BaseModel):
    messages: List[Message]

class candidate(BaseModel):
    """Candidate data model."""
    candidate_name: str = Field(
        ..., description="Name of the candidate"
    )
    experience: str = Field(
        ..., description="Total years of experience along with current company and designation"
    )
    skills: str = Field(
        ..., description="Actual skills the candidate has worked on from professional experience"
    )
    contact_info: str = Field(
        ..., description="Contact information of the candidate"
    )
    linkedin_profile: Optional[str] = Field(
        None, description="LinkedIn profile URL of the candidate"
    )

class work_experience(BaseModel):
    """Work experience data model."""
    company: str = Field(
        ..., description="Company where the candidate has worked"
    )
    designation: str = Field(
        ..., description="Designation held by the candidate"
    )   
    duration: str = Field(
        ..., description="Duration of employment in the company"
    )
    key_responsibilities: str = Field(
        ..., description="Key responsibilities held by the candidate in the company"
    )
    skills_used: str = Field(
        ..., description="Skills used by the candidate in the role"
    )
    
class candidate_work_experience(BaseModel):
    """Combined model for work experience."""
    response_message: str = Field(
        ..., description="Response message for the work experience analysis"
    )
    work_experience: List[work_experience]

class candidate_finder(BaseModel):
    """Combined model for candidate details."""
    response_message: str = Field(
        ..., description="Response message for the candidate finder"
    )
    candidates: List[candidate]

class download_link(BaseModel):
    """Model for download link."""
    response_message: str = Field(
        ..., description="Response message for the download link generation"
    )
    download_link: str = Field(
        ..., description="Generated download link for the requested data"
    )

class CVParseResponse(BaseModel):
    """Response model for CV parsing."""
    response_message: str = Field(
        ..., description="Response message for Users queries"
    )
    candidate: candidate_finder
    work_experience: candidate_work_experience
    download_link: download_link