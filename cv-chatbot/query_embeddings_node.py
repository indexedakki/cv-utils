from state_types import MyState 
from typing import TypedDict, Literal, List,Optional, Tuple
# from model import client
import os
import numpy as np
import json
import pyodbc
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger
LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


driver = '{ODBC Driver 17 for SQL Server}'
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
username = 'cvchatbot'
password = os.getenv("PASSWORD")

conn_str = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)


def query_embeddings(state: MyState) -> MyState:
    # print("Enter Query Embeddings")
    query = state["query"]
    embedding_model = client.embeddings.create(
        input= query,
        model="text-embedding-ada-002"
    )
    embedding = embedding_model.data[0].embedding  # Extracting the embedding from the response
    # print(f"the query from embeddings",query )
    # print(f"[Query Embedding] Created embedding of length {len(embedding)}")
    return {**state, "query_embedding": embedding}


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def semantic_search(state: MyState) -> MyState:
    query_embedding = np.array(state["query_embedding"])

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT  * FROM candidates")

    results = []
    for row in cursor.fetchall():
        try:
            candidate_embedding = np.array(json.loads(row.embeddings))  # parse JSON string
            score = cosine_similarity(query_embedding, candidate_embedding)
            results.append({
                "name": row.name,
                "email": row.email,
                "phone": row.phone,
                "location": row.location,
                "role": row.role,
                "experience_years": row.experience_years,
                "skills": row.skills,
                "present_employer": row.present_employer,
                "linkedin": row.linkedin,
                "career_gap":row.career_gap,
                "achievements": row.achievements,
                "summary": row.summary,
                "score": score
            })
            # print("Results in the function-->",results)
        except Exception as e:
            print(f"Skipping row due to error: {e}")

    # Sort by similarity score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Take top 5 matches
    top_results = results[:10]
    # print(f"[Semantic Search] Found {len(top_results)} top matches.")
    return {**state, "semantic_results": top_results}

#----------------------- Store the semantic chunks in LangGraph state
def store_chunks_results(state: MyState) -> MyState:
    print("Entering Store chunks results")
    logger.info("Entering Store chunks results")

    semantic_results = state.get("semantic_results", [])
    return {**state, "semantic_results": semantic_results}