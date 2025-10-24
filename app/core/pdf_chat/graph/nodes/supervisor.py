import logging
from typing import Dict, Any, List
from app.core.pdf_chat.schemas.graph_states import GraphState
from app.core.pdf_chat.services.supervisor_pipeline import question_router, RouteQuery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def supervisor_router_node(state: GraphState) -> Dict[str, Any]:
    """
    Nodo supervisor que enruta la pregunta del usuario al flujo correspondiente
    (por ejemplo, sql_flow, pdf_flow, default_flow, etc.).
    Mantiene el estado de la conversación y asegura que las claves previas no se pierdan.
    """
    logger.info("---NODO: Supervisor Router---")

    try:
        question = state.get("question", "")
        if not question:
            logger.warning("No question found in state. Defaulting to 'default_flow'.")
            state.update({"route": "default_flow", "next_node": "default_flow"})
            return state

        if "messages" not in state or not isinstance(state["messages"], list):
            state["messages"] = []

        state["messages"].append({"type": "human", "content": question})

        # Serializar mensajes
        serialized_messages = []
        for m in state["messages"]:
            if isinstance(m, dict):
                serialized_messages.append(m)
            elif hasattr(m, "content"):
                serialized_messages.append({"type": m.__class__.__name__, "content": m.content})
            else:
                serialized_messages.append({"type": "unknown", "content": str(m)})

        router_result: RouteQuery = question_router.invoke({
            "question": question,
            "chat_history": serialized_messages
        })

        route = router_result.datasource
        task_description = router_result.task_description

        logger.info(f"[supervisor] Routing to: {route} with task: {task_description}")

        state.update({
            "route": route,
            "task_description": task_description,
            "question": question,
            "messages": serialized_messages,
            "next_node": route
        })

        return state

    except Exception as e:
        logger.exception(f"[supervisor] Error in router: {e}")
        state.update({
            "route": "default_flow",
            "next_node": "default_flow",
            "error": str(e)
        })
        return state
