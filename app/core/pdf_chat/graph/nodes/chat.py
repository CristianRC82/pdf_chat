import logging
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.pdf_chat.services.chat_pipeline import chat_chain

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_chat_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo de chat encargado de procesar la pregunta del usuario con el pipeline de chat.
    Si se solicita un certificado, el agente responderá indicando que se está generando.
    """
    try:
        logger.info("[chat node] Start chat node execution")

        question = state.get("question")
        if not question:
            logger.warning("[chat node] No question provided")
            state["final_answer"] = "No question provided."
            return state

        # Ejecuta el pipeline LLM
        answer = chat_chain.invoke({"user_input": question})
        logger.debug(f"[chat node] Model answer: {answer}")

        # Guarda el mensaje en el historial
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(AIMessage(content=answer))

        # Guarda el resultado final
        state["final_answer"] = answer

        logger.info("[chat node] Chat node executed successfully")
        return state

    except Exception as e:
        logger.error(f"[chat node] Error running chat agent: {str(e)}", exc_info=True)
        state["final_answer"] = "Error executing chat node."
        return state
