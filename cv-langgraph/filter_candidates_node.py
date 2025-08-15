import os
import pyodbc
import openai
import json
import ast
import numpy as np
from schema import CampaignState
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

AZURE_SQL_SERVER   = os.getenv("AZURE_SQL_SERVER", "your_server.database.windows.net")
AZURE_SQL_DB       = os.getenv("AZURE_SQL_DB", "your_database")
AZURE_SQL_USER     = os.getenv("AZURE_SQL_USER", "your_user")
AZURE_SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD", "your_password")

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server=tcp:{AZURE_SQL_SERVER},1433;"
    f"Database={AZURE_SQL_DB};"
    f"Uid={AZURE_SQL_USER};"
    f"Pwd={AZURE_SQL_PASSWORD};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_embedding(text):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def fetch_all_embeddings():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = "SELECT * FROM [dbo].[candidates]"
    cursor.execute(query)

    results = []
    for row in cursor.fetchall():
        user_id, name, email, phone, location, role, experience_years, skills, present_employer, resume_metadata, created_at, linkedin, career_gap, achievements, embeddings, summary, vector_, summary_campaign, summary_campaign_embeddings = row
        embedding = np.array(ast.literal_eval(embeddings))
        results.append({
            "user_id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "location": location,
            "role": role,
            "experience_years": experience_years,
            "skills": skills,
            "present_employer": present_employer,
            "resume_metadata": resume_metadata,
            "created_at": created_at,
            "achievements": achievements,
            "career_gap": career_gap,
            "embeddings": embedding,
            "summary": summary,
            "summary_campaign": summary_campaign,
            "summary_campaign_embeddings": summary_campaign_embeddings
        })
    logger.info(f"Fetching SQL DB: {[results[i]['name'] for i in range(len(results))]}")
    return results

candidates = fetch_all_embeddings()

def filter_candidates(state: CampaignState) -> CampaignState:
    """
    Query Azure SQL for candidates matching role, experience, and skills.
    """
    semantic_search(state["raw_text"], state)
    # state['emails'] = top_candidates
    # sql = (
    #     "SELECT email FROM Candidates WHERE role = ? "
    #     "AND experience_years >= ?"
    # )
    # cursor.execute(sql, state["role"], state["experience_years"])
    # rows = cursor.fetchall()
    # state["candidates"] = [r.email for r in rows]
    # logger.info(f"Filtered {len(state['candidates'])} candidates for role: {state['role']}")
    
    return state

def semantic_search(user_query, state: CampaignState):
    query_vector = np.array(get_embedding(user_query))
    # candidates = fetch_all_embeddings()
    # Compute cosine similarity
    def parse_embedding(s):
        # s might be something like "[0.12, 0.34, ...]"
        return np.array(json.loads(s), dtype=float)

    def cosine_similarity(a, b):
        a = parse_embedding(a) if isinstance(a, str) else np.array(a, dtype=float)
        b = parse_embedding(b) if isinstance(b, str) else np.array(b, dtype=float)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    scored = []
    for person in candidates:
        sim = cosine_similarity(query_vector, person["summary_campaign_embeddings"])
        scored.append((sim, person))
    
    similar_candidates= []
    scored.sort(reverse=True, key=lambda x: x[0])
    for sim, person in scored:
        logger.info(f"Person: {person['name']}, Similarity: {sim}")
        similar_candidates.append("Name: " + person['name'] + " Role: " + person['role'] + " Email: " + person['email'] + " Skills: " + person['skills'] + 
                                " Experience: " + str(person['experience_years']) + " Location: " + person['location'])
    top_results = similar_candidates[:int(len(candidates) * 0.8)] # top 80%
    logger.info(f"Found {int(len(candidates) * 0.8)} similar candidates of total {len(candidates)} candidates")
    logger.info(f"Similar_candidates: {top_results}")
    state['similar_candidates'] = top_results
    
    return state