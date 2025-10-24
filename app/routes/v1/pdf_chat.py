import logging
from fastapi import APIRouter, status, Body, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.pdf_chat_service import Pdf_chat_service
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/pdf_chat", tags=["pdf_chat"])
service = Pdf_chat_service()


class Pdf_chat_payload(BaseModel):
    userId: str
    question: str
    conversationId: str


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    description="Create an AI response and optionally generate a certificate PDF",
    summary="Returns AI answer and downloadable PDF if requested"
)
def execute_graph(payload: Pdf_chat_payload):
    """
    Receives a user question, forwards it to the service,
    and optionally returns the PDF certificate if generated.
    """
    logger.info("Start process to request graph")
    response = service.execute_and_process_graph(payload.model_dump())

    ai_text = response.get("result", "")
    pdf_path = response.get("pdf_path")

    # If a PDF was generated, return it as a downloadable file
    if pdf_path and Path(pdf_path).exists():
        logger.info(f"Certificate generated at {pdf_path}")
        return FileResponse(
            path=pdf_path,
            filename=Path(pdf_path).name,
            media_type="application/pdf"
        )

    # Otherwise, return AI answer only
    return {"status": "200", "result": ai_text}
