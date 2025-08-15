from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, List,Optional, Tuple
# from langchain.embeddings import OpenAIEmbeddings
import os
import openai
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import pyodbc
import numpy as np
import json
import cohere
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

from prompt import intent_prompt, genric_prompt, final_response_prompt

# Load environment variables from .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4", temperature=0)


class MyState(TypedDict):
    query: str
    messages: List[str]
    chat_history: List[Tuple[str, str]]  
    intent: Literal["new_question", "follow_up", "genric"]
    query_embedding: List[float] 
    semantic_results: Optional[List[dict]]  
    reranked_results: Optional[List[dict]]  
    final_response: Optional[str] 


def intent_decision_node(state: MyState) -> Literal["new_question", "follow_up", "genric"]:
    formatted_prompt = intent_prompt.format(messages="\n".join(state["messages"]), query=state["query"])
    response = llm.invoke(formatted_prompt).content.strip().lower()
    print(f"LLM Intent Detected---->: {response}")
        # Safety check: only allow expected values
    intent = response if response in ["new_question", "follow_up", "genric"] else "new_question"
    print(f"LLM Intent Detected---->: {intent}")
    return {**state, "intent": intent}

def handle_new_question(state: MyState) -> MyState:
    print("Handling new question")
    return state

def handle_follow_up(state: MyState) -> MyState:
    # Combine last few messages for better context
    history = state.get("chat_history", [])
    # context = "\n".join(state["messages"][-6:])  # last 3 Q-A pairs
    context = "\n".join([f"User: {q}\nBot: {a}" for q, a in history[-3:]])  # last 3 turns
    new_query = state["query"]
    updated_query = f"{context}\nFollow-up: {new_query}"
    return {**state, "query": updated_query}

def handle_genric_message(state: MyState) -> MyState:
    query = state["query"]
    prompt = genric_prompt.format(query=query)
    response = llm.invoke(prompt).content.strip()
    return {**state, "final_response": response}


# ---------------- Create query_embeddings Node-----------------

def query_embeddings(state: MyState) -> MyState:
    print("Enter Query Embeddinsg")
    query = state["query"]
    embedding_model = client.embeddings.create(
        input= query,
        model="text-embedding-ada-002"
    )
    embedding = embedding_model.data[0].embedding  # Extracting the embedding from the response
    print(f"[Query Embedding] Created embedding of length {len(embedding)}")
    return {**state, "query_embedding": embedding}

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
    print(f"[Semantic Search] Found {len(top_results)} top matches.")
    return {**state, "semantic_results": top_results}

#----------------------- Store the semantic chunks -------------------------------------
def store_chunks_results(state: MyState) -> MyState:
    semantic_results = state.get("semantic_results", [])
    return {**state, "semantic_results": semantic_results}

#------------------------ Coher Ranking --------------------------------------------------
def cohere_rerank(state: MyState) -> MyState:
    # print("State-->",state)
    user_query = state["query"]
    retrieved_candidates = state.get("semantic_results", [])
    print("semantic_results  ---->", retrieved_candidates)
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


    print("ranked_docs use coher rank ---> ",ranked_docs)
    # print("State after coher rank ---> ",state)
    # for candidate in ranked_docs:
    #     print(f"Score {candidate['rerank_score']:.3f} - {candidate['name']}")

    return {**state, "reranked_results": ranked_docs}

#------------------------- Final response ---------------------------------------------

def final_response_node(state: MyState) -> MyState:
    query = state["query"]
    reranked = state.get("reranked_results", [])

    reranked_json = json.dumps(reranked, indent=2)

    prompt = final_response_prompt.format(
        query=query,
        reranked_json=reranked_json
    )

    # print("\n📤 Final prompt sent to LLM:\n", prompt)

    response = llm.invoke(prompt)
    final_reply = response.content.strip()
    # Append query and response to messages
    updated_messages = state.get("messages", []) + [query, final_reply]
     
    # Update chat history
    chat_history = state.get("chat_history", [])
    chat_history.append((query, final_reply))

    return {
        **state,
        "final_response": final_reply,
        "messages": updated_messages,
        "chat_history": chat_history
    }

    # print("\n📥 Final response from LLM:\n", response.content)
    # return {**state, "final_response": response.content}


from langgraph.graph import StateGraph

graph_builder = StateGraph(MyState)
graph_builder.add_node("intent_decision", intent_decision_node)

# Add edges from decision node to next nodes
graph_builder.add_conditional_edges(
    "intent_decision",
    lambda state: state["intent"],  # decision based on `intent` in state
    {
        "new_question": "handle_new_question",
        "follow_up": "handle_follow_up",
        "genric": "handle_genric_message"
    }
)

graph_builder.add_node("handle_new_question", handle_new_question)
graph_builder.add_node("handle_follow_up", handle_follow_up)
graph_builder.add_node("handle_genric_message", handle_genric_message)
graph_builder.add_node("query_embeddings", query_embeddings)
graph_builder.add_node("semantic_search", semantic_search)
graph_builder.add_node("store_chunks_results", store_chunks_results)
graph_builder.add_node("cohere_rerank", cohere_rerank)
graph_builder.add_node("final_response_node", final_response_node)

# Set the END nodes
graph_builder.set_entry_point("intent_decision")

# graph_builder.add_edge("handle_new_question", END)
graph_builder.add_edge("handle_new_question", "query_embeddings")
graph_builder.add_edge("query_embeddings", "semantic_search")
graph_builder.add_edge("semantic_search", "store_chunks_results")
graph_builder.add_edge("store_chunks_results", END)

graph_builder.add_edge("handle_follow_up", "store_chunks_results")
graph_builder.add_edge("store_chunks_results", "cohere_rerank")
graph_builder.add_edge("cohere_rerank", "final_response_node")
graph_builder.add_edge("final_response_node", END)


graph_builder.add_edge("handle_genric_message", END)
# graph_builder.add_edge("handle_follow_up", END)
graph = graph_builder.compile()

from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))

# Example Usagae
# test_state = {
#     "query": "7+ years of expereince with React JS, HTML5 in pune ",
#     "messages": [],
#     "intent": "",  # Will be set by intent_decision
#     "query_embedding": None,
#     "semantic_results": None,
#     "reranked_results": None,
#     "final_response": None

# }

# final_output = graph.invoke(test_state)

# from pprint import pprint
# print("\n🧾 Final Output State---->:\n")
# pprint(final_output)

# print("\n✅ FINAL RESPONSE TO USER ---->:\n")
# print(final_output["final_response"])


# Round 1 - New question
state_1 = {
    "query": "Do you have a Power BI Developer with ETL experience?",
    "messages": [],
    "intent": "",
    "query_embedding": None,
    "semantic_results": None,
    "reranked_results": None,
    "final_response": None
}

response_1 = graph.invoke(state_1)

print(response_1)

# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# # Round 2 - Follow-up question
# state_2 = {
#     "query": "What are the projects Priyanka worked on?",
#     "messages": response_1["messages"],
#     "intent": "",  # Will be detected as follow-up
#     "query_embedding": None,
#     "semantic_results": response_1["semantic_results"],
#     "reranked_results": None,
#     "final_response": None
# }

# response_2 = graph.invoke(state_2)

# # Output full conversation
# from pprint import pprint
# print("\n🧠 Conversation History:")
# pprint(response_2["messages"])

# print("\n✅ Final Bot Response:")
# print(response_2["final_response"])
