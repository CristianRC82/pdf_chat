import logging
from fastapi import HTTPException
from app.core.singleton.pdf_chat_graph import GraphSingleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Pdf_chat_service:
    """
    Service to handle PDF chat flow using a LangGraph with SQL and PDF nodes.
    """

    def __init__(self):
        self.graph_instance = GraphSingleton()

    def execute_and_process_graph(self, payload: dict, conversation_state: dict = None) -> dict:
        try:
            user_id = payload.get("userId")
            question = payload.get("question")
            conversation_id = payload.get("conversationId")

            logger.info(f"[graph service] Starting execution for user {user_id} - conversation {conversation_id}")

            config = {
                "configurable": {
                    "thread_id": conversation_id,
                    "langfuse_session_id": conversation_id,
                    "langfuse_user_id": user_id,
                }
            }

            input_data = {"question": question}

            if conversation_state:
                input_data["conversation_state"] = conversation_state
                if conversation_state.get("document_number"):
                    input_data["document_number"] = conversation_state["document_number"]

            # Ejecutar el grafo
            response = self.graph_instance.run(input_data, config=config)
            new_state = response.get("conversation_state", {})

            # 🔍 Depuración para ver toda la estructura
            logger.debug(f"[graph service] Raw graph response: {response}")

            message = (
                response.get("message")
                or response.get("final_message")
                or response.get("output", {}).get("message")
                or new_state.get("message")
                or new_state.get("output", {}).get("message")
                or ""
            )

            pdf_path = (
                response.get("pdf_path")
                or response.get("output", {}).get("pdf_path")
                or new_state.get("pdf_path")
                or new_state.get("output", {}).get("pdf_path")
                or ""
            )

            content = response.get("final_answer", "") or message
            logger.info(f"message {message}")
            logger.info(f"response {response.get('final_answer', '')}")

            logger.info(f"[graph service] Final answer: {content}")

            return {
                "status": response.get("status", "200"),
                "result": content or "Sin respuesta disponible.",
                "message": message,
                "pdf_path": pdf_path,
                "conversation_state": new_state,
                "error": response.get("error")
            }

        except Exception as e:
            logger.error("[graph service] Internal server error:", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
