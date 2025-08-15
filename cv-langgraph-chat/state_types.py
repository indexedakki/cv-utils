from typing import TypedDict, Literal, List, Optional, Tuple

class MyState(TypedDict):
    query: str
    messages: List[str]
    chat_history: List[Tuple[str, str]]  
    intent: Literal["new_question", "follow_up", "generic"]
    query_embedding: List[float] 
    semantic_results: Optional[List[dict]]  
    reranked_results: Optional[List[dict]]  
    final_response: Optional[str] 