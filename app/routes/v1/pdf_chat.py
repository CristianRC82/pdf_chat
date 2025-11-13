import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, FileResponse
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
    description="Crea respuesta AI y genera un certificado PDF si aplica",
    summary="Devuelve la respuesta o el PDF directamente"
)
def execute_graph(payload: Pdf_chat_payload):
    logger.info("Start process to request graph")
    response = service.execute_and_process_graph(payload.model_dump())

    ai_text = response.get("result", "")
    message = response.get("message", "")
    pdf_path = response.get("pdf_path")
    error = response.get("error")

    # ⚠️ Si hubo error
    if error:
        return JSONResponse(
            content={"result": error, "status": "500"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 📄 Si existe PDF → mostramos link en JSON (para Swagger)
    if pdf_path and Path(pdf_path).exists():
        filename = Path(pdf_path).name
        download_url = f"/api/v1/pdf_chat/download/{filename}"
        logger.info(f"[pdf node] PDF disponible en {download_url}")
        return JSONResponse(
            content={
                "result": f"Se generó el PDF satisfactoriamente para el documento.",
                "status": "200",
                "download_url": download_url
            },
            status_code=status.HTTP_200_OK
        )

    # 💬 Si no hay PDF → JSON normal
    return JSONResponse(
        content={
            "result": ai_text or message or "Sin respuesta disponible.",
            "status": "200"
        },
        status_code=status.HTTP_200_OK
    )


@router.get("/download/{filename}", description="Descarga un PDF generado previamente")
def download_pdf(filename: str):
    pdf_file = Path("app/core/pdf_chat/generated_pdfs") / filename
    if not pdf_file.exists():
        return JSONResponse(
            content={"result": "Archivo no encontrado", "status": "404"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    return FileResponse(
        path=pdf_file,
        filename=filename,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
