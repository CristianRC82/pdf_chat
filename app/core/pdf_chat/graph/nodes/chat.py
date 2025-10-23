import logging
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.pdf_chat.schemas.graph_states import GraphState
from app.core.pdf_chat.services.chat_pipeline import chat_chain

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def run_chat_agent_node(state: GraphState) -> Dict[str, Any]:
    try:
        logger.info("[chat node] start chat node")
        original_question = state.get("question")
        if not original_question or not isinstance(original_question, str):
            logger.error("[chat node] no question provided")
            raise ValueError("No valid question was provided.")
        user_input_for_chain = original_question
        final_answer_for_user = chat_chain.invoke({"user_input": user_input_for_chain})
        state["messages"].append(AIMessage(content=final_answer_for_user))
    except Exception as ex:
        logger.error('[chat node] Exception while executing chat agent node:', exc_info=True)
