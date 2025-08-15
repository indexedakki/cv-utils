from typing import List, Any
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Personal_Details(BaseModel):
    Name: str = Field(
        description=""" Name of candidate in normal format """
        )
    Role: str = Field(
        description=""" Role of candidate as per work experience, like Python Developer, Data Engineer, React Developer, Data Scientist """
    )
    Email: str = Field(
        description=""" Email present in the resume of candidate else NA """
        )
    Phone: List[int] = Field(
        description=""" Phone number or contact number of candidate if not present put NA"""
        )
    Nationality: str = Field(
        description="""Nationality if present in the resume else NA"""
        )
    LinkedIn: str = Field(
        description="LinkedIn URL,if not present put NA"
        )
    url: str = Field(
        description="Any other URL as specified in the resume else NA"
        )
    location: str = Field(
        description="Candidate current location if present in resume if not put NA"
        )
    candidate_unique_id: str = Field(
        description="Unique identifier of the candidate as specified in the resume"
        )

class skillset(BaseModel):
    Key_Skills: List[str] = Field(
        description=""" Relevant skills and competencies """
        )
    Technical_Skills: List[str] = Field(
        description=""" technical proficiencies OR domain-specific skills  """
        )
    Optional_Skills: List[str] = Field(
        description=""" Irrelevant skills apart from Technical skills which are good to have if present in JD """
        )
    Soft_Skills: List[str] = Field(
        description=""" Soft skills if present in JD"""
                                   )
    top_10_skills: List[str] = Field(
        description=""" Top 10 skills based on all skills, which are most relevant to his work experience"""
        )

class ProfessionalDetail(BaseModel):
    """A single entry of the candidate's professional details."""
    employer_name: str = Field(description="Name of the employer")
    job_title: str = Field(description="Job title held")
    start_date: date = Field(description="Employment start date")
    end_date: Optional[date] = Field(None, description="Employment end date; optional if still employed")
    employer_country: str = Field(description="Country where the employer is located")
    employer_city: str = Field(description="City where the employer is located")
    job_function: str = Field(description="Job function or role description")
    key_responsibilities: List[str] = Field(description="Key responsibilities and achievements")
    skills: List[str] = Field(description="Skills learned during employment")

class resume(BaseModel):
    Personal_Details: Personal_Details
    skillset:skillset
    Experience_year: int = Field(
        description="""Total number of year of experience if not given leave it empty"""
        )
    Professional_Experience: List[ProfessionalDetail] = Field(
        description="""Companies, Job_titles, Duration_of_employment, Start_date, End_date, Key_responsibilities_and_achievements, skills :List of skills learned in duration of employment"""
        )
    Education:List[dict] = Field(
        description=""" Institutions attended, Degree, Department, Duration"""
        )
    Projects:List[dict] = Field(
        description="""Name : Project name , Objective: objective of the project, Role : role in project ,Outcome :outcome of project, skills: learned skills"""
        ) 
    Achievements:List[str] = Field(
        description=""" Notable accomplishments and recognitions """
        )
    Certification:List[str] = Field(
        description="""Relevant certifications and courses completed"""
        )
    Extra_Activities :List[str] = Field(
        description= """ Participation in relevant extracurricular activities or committees """
        )
    Professional_Summary:List[str] = Field(
        description="""Overview of expertise and career focus, Career goals and objectives as stated in the resume"""
        )

resume_template = """
You are an expert details extractor having experties in extracting Resume details for recruitment.
You are given with Resume, your task is to analyze Resume and extract all relevant information to facilitate matching with Job description.

Here is the Resume:
{resume}

Extract the details in below format, if any details/information is not present then left the field empty do not assume or make it anything by yourself.
{format_instructions}
"""
