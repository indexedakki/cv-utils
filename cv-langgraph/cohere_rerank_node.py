import os
import cohere
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from schema import CampaignState, FilteredCandidate 
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def cohere_rerank(state: CampaignState):
    co = cohere.ClientV2()
    similar_candidates = state['similar_candidates']
    response = co.rerank(
        model="rerank-v3.5",
        query=state["raw_text"],
        documents=similar_candidates,
        top_n=int(len(similar_candidates) * 0.8),
    )

    results = response.results

    ranked_docs = [
        (similar_candidates[item.index], item.relevance_score)
        for item in results
    ]    
    for doc, score in ranked_docs:
        logger.info(f"Score {score:.3f}: {doc}")

    reranked_candidates = [(candidate[0]) for candidate in ranked_docs]
    logger.info(f"Found {int(len(similar_candidates) * 0.8)} reranked candidates of {len(similar_candidates)} similar candidates")
    logger.info(f"Reranked candidates: {reranked_candidates}")
    further_filtered_candidates = filter_further(reranked_candidates, state)
    if not state["emails"]:
        logger.warning("No candidates found matching the criteria.")
    else:
        logger.info(f"Candidates found: {state['emails']}")
    return state

def filter_further(reranked_candidates, state: CampaignState):
    """
    Use the LLM to filter candidates based on role, skills, experience and location.
    """
    messages = [
        SystemMessage(content="You are a helpful assistant that finds candidates based on their skills, experience, role, location and extract EMAIL and NAMES of those candidate."),
        HumanMessage(
            content=(f"""
                Extract NAME and EMAIL of any candidate whose
                - Role is similar to {state['role']} (case-insensitive),
                - AND has at least {state['experience_years']} years experience,
                - AND is located in {state['location']}.
                
                Candidates list (one per line):
                {reranked_candidates}"""
            )
        ),
    ]

    llm_struc = llm.with_structured_output(FilteredCandidate)
    response = llm_struc.invoke(messages)
    logger.info(f"Final candidates : {response}")
    state['candidates'] = response.dict()
    for email in response.email:
        logger.info(f"emails: {email}")
    state['emails'] = response.email