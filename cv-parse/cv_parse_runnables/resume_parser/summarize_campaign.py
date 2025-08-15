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
        email = data["Personal_Details"]["Email"]
    
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
        cursor.execute(f"""
            UPDATE dbo.candidates
            SET
                summary_campaign            = ?,
                summary_campaign_embeddings = ?
            WHERE
                email = ?;
            """, (
            summary ,vector_json, email
        ))
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"""Inserted summary campaign to db
                Summary = {summary} for user_id {email}""")
    except Exception as e:
        logger.error(f"Error inserting into DB for for summary campaign {email}: {e}")


async def summarize_resume(file_path: str):
    """Summarizes a candidate's resume from a JSON file."""

    # Open and load the JSON data
    with open(file_path, 'r', encoding='utf-8') as file:
        input_json = json.load(file)

    template = """
    You are a smart assistant that summarizes a candidate's resume into a well-structured professional summary.

    Based on the following JSON input, generate a structured summary with the following sections:
    
    Role: (extract the candidate's role)
    Location: (extract the candidate's location, default to "unspecified location" if not available)
    Top 10 Skills: (pick the most relevant technical and soft skills)
    Experience: (Total experience of candidate in years)

    Ensure:
    - The formatting is professional.
    - Line breaks separate each section.
    - Use concise but informative descriptions.
    - Only above sections should be there, nothing else
    
    Candidate JSON:
    {input_json}
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

    # logger.info(f"Summary: {result['summary']}")

    filename = os.path.basename(file_path)            # → "resume1.json"
    name_only, _ext = os.path.splitext(filename)       # → ("resume1", ".json")

    out_path = os.path.join("cv_parse_runnables","summaries_campaign",f"{name_only}.txt")

    # Save the summary to a summaries folder
    with open(out_path, 'w', encoding='utf-8') as summary_file:
        summary_file.write(result["summary"])
    
    insert_to_mysql(result['summary'], input_json)
    

def _sync_summarize(file_path: str):
    """Sync wrapper that runs the async summarize_resume."""
    asyncio.run(summarize_resume(file_path))

async def summarize_campaign():
    SUMMARY_DIR = "cv_parse_runnables/summaries_campaign"
    os.makedirs(SUMMARY_DIR, exist_ok=True)

    async with asyncio.TaskGroup() as tg:
        for filename in os.listdir("cv_parse_runnables/separate_jsons"):
            file_path = os.path.join("cv_parse_runnables/separate_jsons", filename)
            # schedule the blocking wrapper in a thread
            tg.create_task(
                asyncio.to_thread(_sync_summarize, file_path)
            )

# asyncio.run(summarize())
