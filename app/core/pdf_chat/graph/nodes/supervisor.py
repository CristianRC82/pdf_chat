import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from app.core.pdf_chat.schemas.graph_states import GraphState
from app.core.pdf_chat.services.supervisor_pipeline import question_router, RouteQuery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def supervisor_router_node(state: GraphState) -> Dict[str, Any]:
    """
    function in charge of managing the supervisor
    :param state: graph state
    :return:dictionary with the instruction to the next node together with the user's query
    """
    try:
        logger.info("[supervisor node] start supervisor node")

        question = state["question"]

        if "messages" not in state:
            state["messages"] = []

        state["messages"].append(HumanMessage(content=question))

        router_result: RouteQuery = question_router.invoke({
            "question": state["question"],
            "chat_history": state["messages"]
        })

        route = router_result.datasource
        task_description = router_result.task_description

        return {
            "route": route,
            "task_description": task_description,
            "question": question,
            "messages": state["messages"]
        }
    except Exception as e:
        logger.error(f"[supervisor node] Error when invoking supervisor node: {e}", exc_info=True)