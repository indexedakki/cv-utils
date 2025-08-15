from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # or AzureChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_community.embeddings import OpenAIEmbeddings
from typing import TypedDict, Annotated
import json
import os
from dotenv import load_dotenv
import asyncio
import pyodbc
from datetime import datetime


from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

# Define input and output schema
class SummaryInput(TypedDict):
    json_data: dict
    summary: Annotated[str, "Structured resume summary"]

# Setup LLM
load_dotenv()
# Get values from environment
model_name = os.getenv("MODEL")
openai_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4")

def insert_to_mysql(summary: str, data: dict):
    """Insert the summary and JSON data into Azure MySQL database."""
    try:
        name = data["Personal_Details"]["Name"]
        email = data["Personal_Details"]["Email"]
        phone = data["Personal_Details"]["Phone"][0]
        linkedin = data["Personal_Details"]["LinkedIn"]
        location = data["Personal_Details"]["location"]
        role = data["Personal_Details"]["Role"]
        experience_year = data["Experience_year"]
        skills = str(data["skillset"]["top_10_skills"])
        achievements =  str(data["Achievements"])
        career_gap =  str(data["career_gap"])
        present_employer = data["Professional_Experience"][0]["employer_name"]
        resume_metadata = data["Personal_Details"]["candidate_unique_id"]
        created_at = datetime.now()
        
        # response = openai.embeddings.create(
        #         model="text-embedding-ada-002",
        #         input=summary)
        # embedding = response.data[0].embedding
        # embedding_json = json.dumps(embedding)
        
        emb = OpenAIEmbeddings(model="text-embedding-ada-002")
        summary_embedding = emb.embed_query(summary)
        vector_json = json.dumps(summary_embedding)

        server   = os.getenv('AZURE_SQL_SERVER')
        database = os.getenv('AZURE_SQL_DATABASE')
        username = os.getenv('AZURE_SQL_USERNAME')
        password = os.getenv('AZURE_SQL_PASSWORD')
        driver   = 'ODBC Driver 17 for SQL Server'

        conn_str = (
            f"Driver={driver};"
            f"Server=tcp:{server},1433;"
            f"Database={database};"
            f"Uid={username}@cv-chatbot-server;"
            f"Pwd={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # then same INSERT, e.g.:
        cursor.execute("""
        INSERT INTO dbo.candidates 
            (name, email, phone, linkedin, location, role, experience_years, skills, present_employer, resume_metadata, created_at, achievements, career_gap, embeddings, summary)
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, email, phone, linkedin, location, role, experience_year, skills, present_employer, resume_metadata, created_at, achievements, career_gap, vector_json, summary
        ))
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"""Inserted into db
                Name: {name},  
                Email: {email},  
                Phone: {phone},  
                LinkedIn: {linkedin}, 
                Location: {location}, 
                Role: {role},
                Experience Year: {experience_year},
                Skills: {skills},
                Achievements: {achievements},
                Career Gap: {career_gap},
                Present Employer: {present_employer},
                Resume Metadata: {resume_metadata},
                Created At: {created_at}""")
    except Exception as e:
        logger.error(f"Error inserting into DB for {name}: {e}")


async def summarize_resume(file_path: str):
    """Summarizes a candidate's resume from a JSON file."""

    # Open and load the JSON data
    with open(file_path, 'r', encoding='utf-8') as file:
        input_json = json.load(file)

    template = """
    You are a smart assistant that summarizes a candidate's resume into a well-structured professional summary.

    Based on the following JSON input, generate a structured summary with the following sections:

    1. Name: (extract the candidate's name)
    2. Role: (extract the candidate's role)
    3. Location: (extract the candidate's location, default to "unspecified location" if not available)
    4. Top 10 Skills: (pick the most relevant technical and soft skills)
    5. Total Experience: (mention total years, if available)
    6. Work Experience: (List each job with the format: Company (Role: Duration): Responsibility summary)
    7. Projects: (List each project with the format: Project Name (Client, Duration): Brief description)
    8. Certifications: (List all certifications as a comma-separated list)

    Ensure:
    - The formatting is professional.
    - Line breaks separate each section.
    - Use concise but informative descriptions.

    Candidate JSON:
    {input_json}

    Generate the structured summary below:
    """
    prompt = PromptTemplate.from_template(template)

    # Node for summarizing
    def summarize_with_prompt(state: SummaryInput) -> SummaryInput:
        input_json = json.dumps(state["json_data"], indent=2)
        prompt_text = prompt.format(input_json=input_json)
        response = llm.invoke(prompt_text)
        return {"json_data": state["json_data"], "summary": response.content}

    # Build LangGraph
    graph_builder = StateGraph(SummaryInput)
    graph_builder.add_node("summarize", RunnableLambda(summarize_with_prompt))
    graph_builder.set_entry_point("summarize")
    graph_builder.add_edge("summarize", END)
    graph = graph_builder.compile()

    result = graph.invoke({"json_data": input_json})

    logger.info(f"Summary: {result['summary']}")

    filename = os.path.basename(file_path)            # → "resume1.json"
    name_only, _ext = os.path.splitext(filename)       # → ("resume1", ".json")

    out_path = os.path.join("cv_parse_runnables","summaries",f"{name_only}.txt")

    # Save the summary to a summaries folder
    with open(out_path, 'w', encoding='utf-8') as summary_file:
        summary_file.write(result["summary"])
    
    insert_to_mysql(result['summary'], input_json)
    

def _sync_summarize(file_path: str):
    """Sync wrapper that runs the async summarize_resume."""
    asyncio.run(summarize_resume(file_path))

async def summarize():
    SUMMARY_DIR = "cv_parse_runnables/summaries"
    os.makedirs(SUMMARY_DIR, exist_ok=True)

    async with asyncio.TaskGroup() as tg:
        for filename in os.listdir("cv_parse_runnables/separate_jsons"):
            file_path = os.path.join("cv_parse_runnables/separate_jsons", filename)
            # schedule the blocking wrapper in a thread
            tg.create_task(
                asyncio.to_thread(_sync_summarize, file_path)
            )

# asyncio.run(summarize())
