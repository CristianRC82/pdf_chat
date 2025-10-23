import logging
from fastapi import HTTPException
from typing import Dict, Any
from app.core.singleton.magic_chat_graph import GraphSingleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Pdf_chat_service:
    def __init__(self):
        self.graph_instance = GraphSingleton()

    def execute_and_process_graph(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        function in charge of invoking the graph and returning the graph's response.
        :param payload: body request
        :return: response graph
        """
        try:
            user_id = payload.get('userId')
            question = payload.get('question')
            conversation_id = payload.get('conversationId')
            config = {"configurable": {"thread_id": conversation_id, "langfuse_session_id": conversation_id, "langfuse_user_id": user_id}}
            response = self.graph_instance.run({"question": question }, config)
            content = response["messages"][-1].content
            return {
                "status": "200",
                "result": content
            }
        except (ValueError, TypeError, KeyError, IndexError) as e:
            logger.error('[graph service] Exception while executing:', exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

        except Exception as e:
            logger.error('[graph service] Interval server error:', exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")
