import logging
from fastapi import APIRouter, status, Body,HTTPException
from pydantic import BaseModel
from app.services.pdf_chat_service import Pdf_chat_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/pdf_chat", tags=["magic_chat"])
service = Pdf_chat_service()

class Pdf_chat_payload(BaseModel):
    userId: str
    question: str
    conversationId: str

@router.post(
    "",
    status_code=status.HTTP_200_OK,
    description="create an answer",
    summary="gives an answer according to the value of the parameters received."
)
def execute_graph(payload: Pdf_chat_payload):
    """
    receive the application and forward it to the service
    :param payload: body request
    :return: response
    """
    logger.info("Start process to request graph")
    response = service.execute_and_process_graph(payload.model_dump())
    return response
