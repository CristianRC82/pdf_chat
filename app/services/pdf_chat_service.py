import logging
from fastapi import HTTPException
from app.core.singleton.pdf_chat_graph import GraphSingleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Pdf_chat_service:
    """
    Service to handle PDF chat flow using a LangGraph with SQL and PDF nodes.
    Handles conversation state to remember document number and user context.
    """

    def __init__(self):
        self.graph_instance = GraphSingleton()

    def execute_and_process_graph(self, payload: dict, conversation_state: dict = None) -> dict:
        """
        Executes the LangGraph for a user question, managing conversation state and PDF generation.
        
        Args:
            payload (dict): Incoming user data with keys 'userId', 'question', 'conversationId'.
            conversation_state (dict, optional): Previous conversation state.

        Returns:
            dict: Response containing status, result, and updated conversation_state.
        """
        try:
            user_id = payload.get("userId")
            question = payload.get("question")
            conversation_id = payload.get("conversationId")

            logger.info(f"[graph service] Starting execution for user {user_id} - conversation {conversation_id}")

            config = {"configurable": {"thread_id": conversation_id,"langfuse_session_id": conversation_id,"langfuse_user_id": user_id,}}

            input_data = {"question": question}

            if conversation_state:
                input_data["conversation_state"] = conversation_state
                if conversation_state.get("document_number"):
                    input_data["document_number"] = conversation_state["document_number"]

            response = self.graph_instance.run(input_data, config=config)

            logger.info(f"[graph service] Graph execution completed. Raw response: {response}")

            new_state = response.get("conversation_state", {})

            content = response.get("final_answer", "")

            logger.info(f"[graph service] Final answer: {content}")

            return {
                "status": response.get("status", "200"),
                "result": content,
                "conversation_state": new_state
            }

        except Exception as e:
            logger.error("[graph service] Internal server error:", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
