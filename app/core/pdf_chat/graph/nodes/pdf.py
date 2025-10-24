import logging
from typing import Dict, Any
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader, select_autoescape
from io import BytesIO
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TEMPLATE_FILE = "certificado.html"
TEMPLATE_PATH = "app/core/pdf_chat/graph/tools"

def run_pdf_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo PDF:
    Genera un PDF basado en los datos procesados por SQL/PostProcessing y lo deja en memoria (bytes).
    Si se desea, puede guardarse también en disco para verificación.
    """
    logger.info("---NODE: PDF Agent---")

    conversation_state = state.get("conversation_state", {})
    document_number = state.get("document_number")
    result_data = state.get("document_data")

    if not document_number:
        logger.warning("[pdf node] No document number provided")
        conversation_state["awaiting_document_number"] = True
        state["conversation_state"] = conversation_state
        return {"next_node": "supervisor", "conversation_state": conversation_state}

    if not result_data:
        logger.warning(f"[pdf node] No information found for document {document_number}")
        return {
            "next_node": "chat",
            "conversation_state": conversation_state,
            "message": f"No se encontró información para el documento {document_number}"
        }

    try:
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_PATH),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template(TEMPLATE_FILE)

        html_content = template.render(
            document_number=document_number,
            data=result_data
        )

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

        if pisa_status.err:
            logger.error("[pdf node] Error generating PDF")
            return {
                "next_node": "chat",
                "conversation_state": conversation_state,
                "error": "Error al generar el PDF"
            }

        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()

        filename = f"certificado_{document_number}.pdf"

        output_path = os.path.join("app", "core", "pdf_chat", "generated_pdfs")
        os.makedirs(output_path, exist_ok=True)
        pdf_path = os.path.join(output_path, filename)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"[pdf node] PDF generado correctamente para {document_number}")
        logger.info(f"[pdf node] Ruta del PDF: {pdf_path}")

        state.update({
            "pdf_bytes": pdf_bytes,
            "pdf_filename": filename,
            "conversation_state": conversation_state,
            "pdf_path": pdf_path,
            "next_node": "chat"
        })

        return state

    except Exception as e:
        logger.error(f"[pdf node] Error generating PDF: {str(e)}", exc_info=True)
        return {
            "next_node": "chat",
            "conversation_state": conversation_state,
            "error": str(e)
        }
