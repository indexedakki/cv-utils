from state_types import MyState 
from typing import TypedDict, Literal, List,Optional, Tuple
import cohere


def cohere_rerank(state: MyState) -> MyState:
    # print("State-->",state)
    user_query = state["query"]
    retrieved_candidates = state.get("semantic_results", [])
    # print("semantic_results  ---->", retrieved_candidates)
    co = cohere.ClientV2()
    # Prepare documents with full details in text format
    documents = []
    for candidate in retrieved_candidates:
        doc_text = (
            f"Name: {candidate.get('name', '')}\n"
            f"Email: {candidate.get('email', '')}\n"
            f"Phone: {candidate.get('phone', '')}\n"
            f"Role: {candidate.get('role', '')}\n"
            f"Experience: {candidate.get('experience_years', '')} years\n"
            f"Skills: {candidate.get('skills', '')}\n"
            f"Present Employer: {candidate.get('present_employer', '')}\n"
            f"LinkedIn: {candidate.get('linkedin', '')}\n"
            f"Career Gap: {candidate.get('career_gap', '')}\n"
            f"Achievements: {candidate.get('achievements', '')}\n"
            f"Summary: {candidate.get('summary', '')}"
        )
        documents.append(doc_text)

    # Ensure no empty strings
    documents = [doc for doc in documents if doc.strip()]

    if not documents:
        print("⚠️ No valid documents to rerank.")
        return {**state, "reranked_results": []}

    # Rerank with cohere
    response = co.rerank(
        model="rerank-v3.5",
        query=user_query,
        documents=documents,
    )

    results = response.results

    # Map results back to full candidate objects + score
    ranked_docs = [
        {
            **retrieved_candidates[item.index], 
            "rerank_score": round(item.relevance_score, 3)
        }
        for item in results
    ]


    # print("ranked_docs use coher rank ---> ",ranked_docs)
    # print("🔎 Ranked docs with cohere scores:")
    # for doc in ranked_docs:
    #     print(f"score: {doc.get('score', 'N/A')}, rerank_score: {doc.get('rerank_score', 'N/A')}")

    return {**state, "reranked_results": ranked_docs}

