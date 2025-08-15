import os
import json
from typing import Dict
from redis.asyncio import Redis
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from schema import (CampaignState, CampaignRequest, SendEmail)
from filter_candidates_node import filter_candidates
from cohere_rerank_node import cohere_rerank
from generate_email_node import generate_email
from router_chatbot_node import router_chatbot
from parse_input_node import parse_input
from generate_response_node import generate_response
from generate_question_node import generate_question_chatbot
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)
logger.info("Starting FastAPI application...")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

memory = MemorySaver()
graph_builder = StateGraph(CampaignState)
graph_builder.add_node("router_chatbot", router_chatbot)
graph_builder.add_node("parse_input", parse_input)
graph_builder.add_node("generate_response", generate_response)

graph_builder.add_edge(START, "router_chatbot")
graph_builder.add_conditional_edges(
                            "router_chatbot",
                            lambda state: state["action"],
                            {
                                "generic" : "generate_response",
                                "generate_campaign" : "parse_input",
                            }
                        )

graph_builder.add_edge("generate_response", END)

graph = graph_builder.compile(checkpointer=memory)

graph_question_builder = StateGraph(CampaignState)
graph_question_builder.add_node("generate_question_chatbot", generate_question_chatbot)
graph_question_builder.add_edge(START, "generate_question_chatbot")
graph_question_builder.add_edge("generate_question_chatbot", END)
graph_question = graph_question_builder.compile(checkpointer=memory)


graph_email_builder = StateGraph(CampaignState)
graph_email_builder.add_node("filter_candidates", filter_candidates)
graph_email_builder.add_node("cohere_rerank", cohere_rerank)
graph_email_builder.add_node("generate_email", generate_email)

graph_email_builder.add_edge(START, "filter_candidates")
graph_email_builder.add_edge("filter_candidates", "cohere_rerank")
graph_email_builder.add_edge("cohere_rerank", "generate_email")
graph_email_builder.add_edge("generate_email", END)
graph_email = graph_email_builder.compile(checkpointer=memory)


# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# from IPython.display import Image, display
# display(Image(graph_question.get_graph().draw_mermaid_png()))

# from IPython.display import Image, display
# display(Image(graph_email.get_graph().draw_mermaid_png()))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
SESSION_TTL_SECONDS = 3600

redis: Redis  # global client

@app.on_event("startup")
async def startup_event():
    global redis
    # point to the correct host/port
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    try:
        pong = await redis.ping()
        if pong:
            print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        # fail fast so you know immediately
        print(f"❌ Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    await redis.close()

async def get_session(sid: str) -> dict:
    raw = await redis.get(sid)
    return json.loads(raw) if raw else {}

async def save_session(sid: str, data: dict):
    await redis.set(sid, json.dumps(data), ex=SESSION_TTL_SECONDS)

@app.post("/campaign")
async def run_campaign(req: CampaignRequest):
    sid = req.session_id or "default_session"
    state = await get_session(sid)

    logger.info(f"Session ID: {sid}")
    logger.info(f"Session data: {state}")

    initial_state: CampaignState = {
            "messages": [],
            "raw_text": req.user_input,
            "role": "",
            "experience_years": "",
            "location": "",
            "skills": "",
            "theme": "",
            "candidates": [],
            "email_draft": "",
            "emails": "",
            "action": "",
            "subject": "",
            "body": "",
            "similar_candidates": "",
            "response": "",
            "email_feedback": "",
            "validate": False,
            "missing_fields": [],
            "total_missing_field": "",
            "current_field_question": "",
            "current_field": "",
            "previous_field": "",
            "first_run": False
        }
    
    config = {"configurable": {"thread_id": sid}}

    # Create a state variable that starts with initial_state
    if state:
        logger.info(f"Current campaign state: {state!r}")
        state['raw_text'] = req.user_input
    else:
        state = initial_state
        logger.info(f"Initial campaign state: {initial_state!r}")
    logger.info(f"""Received user input---> "{req.user_input}" """)

    if state['first_run'] == False:
        state = graph.invoke(state, config=config)
        state = state
        if state['action'] == "generate_campaign":
            for field in ['role', 'experience_years', 'skills', 'location', 'theme']:
                if field == 'experience_years' and state['experience_years'] == -1:
                    state['missing_fields'].append(field)
                elif field == 'skills' and len(state['skills']) == 0:
                    state['missing_fields'].append(field)
                elif len(str(state[field])) == 0:
                    state['missing_fields'].append(field)
            state['total_missing_field'] = len(state['missing_fields'])
            state = state
            state['first_run'] = True
            await save_session(sid, state)
    if state['action'] == "generate_campaign":
        if state["validate"] == False:      
            if len(state['missing_fields']) == 0:
                logger.info("All fields are filled, proceeding to generate campaign.")
                state['validate'] = True
            logger.info(f"Missing fields: {state['missing_fields']}")
            for i in range(len(state['missing_fields'])+1):
                state['previous_field'] = state['current_field'] if len(str(state['current_field'])) > 0 else state['missing_fields'][0] if len(state['missing_fields']) > 0 else None
                field = state['missing_fields'].pop(0) if len(state['missing_fields']) > 0 else None      
                state['current_field'] = field
                if len(str(state['current_field_question'])) > 0:
                    logger.info(f"Answer for {state['previous_field']}: {state['raw_text']}")
                    state[state['previous_field']] = str(state['raw_text'])
                if state['total_missing_field'] > 0:
                    state['total_missing_field'] -= 1
                    state = graph_question.invoke(state, config={"configurable": {"thread_id": sid}})
                    state = state
                    await save_session(sid, state)
                    return {"message": state['current_field_question']}
        if state['validate'] == True:
            state['action'] = ""
            state = graph_email.invoke(state, config={"configurable": {"thread_id": sid}})
            state = state
            await save_session(sid, state)
            return {"email_draft": f"{state['email_draft']}"}

    else:
        state = graph.invoke(state, config=config)
        state = state
        if state['action'] == "generic":
            await save_session(sid, state)
            return {"message": f"{state['response']}"}

@app.get("/candidates")
async def candidate_list(session_id: str = Query(..., description="Your campaign session ID")):
    sid = session_id or "default_session"
    state = await get_session(sid)
    if not sid:
        logger.warning(f"No session found for ID '{sid}'")
        return{"message": f"No session found for ID '{sid}'"}
    
    current_state = state
    if not current_state:
        logger.warning(f"Campaign has not been initialized for session '{sid}'")
        return{"message": f"Campaign has not been initialized for session: '{sid}'"}
        
    return {
        "sid": sid,
        "candidates": current_state.get("candidates", []),
    }

@app.get("/email_draft")
async def email_draft(session_id: str = Query(..., description="Your campaign session ID")):
    sid = session_id or "default_session"
    state = await get_session(sid)
    if not sid:
        logger.warning(f"No session found for ID '{sid}'")
        return{"message": f"No session found for ID '{sid}'"}
    
    current_state = state
    if not current_state:
        logger.warning(f"Campaign has not been initialized for session '{sid}'")
        return{"message": f"Campaign has not been initialized for session: '{sid}'"}
        
    return {
        "sid": sid,
        "candidates": current_state.get("email_draft", []),
    }

@app.post("/send_email")
async def send_email(req: SendEmail, session_id: str = Query(..., description="Your campaign session ID")):
    sid = session_id or "default_session"
    state = await get_session(sid)
    if not sid:
        logger.warning(f"No session found for ID '{sid}'")
        return{"message": f"No session found for ID '{sid}'"}
    
    current_state = state
    if not current_state:
        logger.warning(f"Campaign has not been initialized for session '{sid}'")
        return{"message": f"Campaign has not been initialized for session: '{sid}'"}
        

    if "emails" in req.email_with_candidates:
        current_state['emails'] = req.email_with_candidates['emails']
    if "email_draft" in req.email_with_candidates:
        current_state['email_draft'] = req.email_with_candidates['email_draft']
    logger.info(f"Final Candidates: {current_state['emails']}")
    logger.info(f"Final Draft: {current_state['email_draft']}")
    return {"message": "Emails have been sent to concerned candidates"}