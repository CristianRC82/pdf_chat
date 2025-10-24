from typing import TypedDict, Optional, List,Dict, Any
from langchain_core.messages import BaseMessage


class GraphState(TypedDict, total=False):
    messages: List[BaseMessage]
    question: str
    route: str
    task_description: Optional[str]
    sql_query: Optional[str]
    sql_results: Optional[Dict[str, Any]]  
    processed_results: Optional[str]
    final_answer: Optional[str]
    document_number: Optional[str]
    document_data: Optional[Dict[str, Any]]
    pdf_ready_data: Optional[Dict[str, Any]]
    next_node: Optional[str]