from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage


class GraphState(TypedDict):
    messages: List[BaseMessage]
    question: str
    route: str
    task_description: Optional[str]
    sql_query: Optional[str]
    sql_results: Optional[str]
    processed_results: Optional[str]
    final_answer: Optional[str]