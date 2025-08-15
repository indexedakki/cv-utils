from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, List,Optional, Tuple
from intent_decision_node import intent_decision_node, handle_new_question, handle_follow_up, handle_generic_message
from query_embeddings_node import query_embeddings, semantic_search, store_chunks_results
from coher_ranking_node import cohere_rerank
from final_response_node import final_response_node

# class MyState(TypedDict):
#     query: str
#     messages: List[str]
#     chat_history: List[Tuple[str, str]]  
#     intent: Literal["new_question", "follow_up", "genric"]
#     query_embedding: List[float] 
#     semantic_results: Optional[List[dict]]  
#     reranked_results: Optional[List[dict]]  
#     final_response: Optional[str] 

# -------------------------------------------------------------------------------
from state_types import MyState  # ✅ Import from new file
# graph_builder = StateGraph(MyState)
# graph_builder.add_node("intent_decision", intent_decision_node)
# graph_builder.add_conditional_edges(
#     "intent_decision",
#     lambda state: state["intent"],  
#     {
#         "new_question": "handle_new_question",
#         "follow_up": "handle_follow_up",
#         "genric": "handle_genric_message"
#     }
# )
# graph_builder.add_node("handle_new_question", handle_new_question)
# graph_builder.add_node("handle_follow_up", handle_follow_up)
# graph_builder.add_node("handle_genric_message", handle_genric_message)
# graph_builder.add_node("query_embeddings", query_embeddings)
# graph_builder.add_node("semantic_search", semantic_search)
# graph_builder.add_node("store_chunks_results", store_chunks_results)
# graph_builder.add_node("cohere_rerank", cohere_rerank)
# graph_builder.add_node("final_response_node", final_response_node)

# graph_builder.set_entry_point("intent_decision")

# graph_builder.add_edge("handle_new_question", "query_embeddings")
# graph_builder.add_edge("query_embeddings", "semantic_search")
# graph_builder.add_edge("semantic_search", "store_chunks_results")
# # graph_builder.add_edge("store_chunks_results", END)

# graph_builder.add_edge("handle_follow_up", "store_chunks_results")
# graph_builder.add_edge("store_chunks_results", "cohere_rerank")
# graph_builder.add_edge("cohere_rerank", "final_response_node")
# graph_builder.add_edge("final_response_node", END)


# graph_builder.add_edge("handle_genric_message", END)
# graph = graph_builder.compile()


# -------------------------------------------------------------------------------------



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
        "generic": "handle_generic_message"
    }
)


graph_builder.add_node("handle_new_question", handle_new_question)
graph_builder.add_node("handle_follow_up", handle_follow_up)
graph_builder.add_node("handle_generic_message", handle_generic_message)

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
graph_builder.add_edge("store_chunks_results", "cohere_rerank")
graph_builder.add_edge("cohere_rerank", "final_response_node")
graph_builder.add_edge("final_response_node", END)

# graph_builder.add_edge("store_chunks_results", END)

graph_builder.add_edge("handle_follow_up", "store_chunks_results")
graph_builder.add_edge("store_chunks_results", "cohere_rerank")
graph_builder.add_edge("cohere_rerank", "final_response_node")
graph_builder.add_edge("final_response_node", END)

graph_builder.add_edge("handle_generic_message", END)

# graph_builder.add_edge("handle_follow_up", END)
graph = graph_builder.compile()
