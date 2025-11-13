import logging
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("weasyprint").setLevel(logging.ERROR)
logging.getLogger("fontTools").setLevel(logging.ERROR)
TEMPLATE_FILE = "certificado.html"
TEMPLATE_PATH = "app/core/pdf_chat/graph/tools"

def run_pdf_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo PDF: Genera un PDF basado en la plantilla HTML (certificado.html) y los datos del documento,
    usando WeasyPrint.
    """
    logger.info("---NODE: PDF Agent (WeasyPrint)---")

    conversation_state = state.get("conversation_state", {})
    document_number = state.get("document_number")
    result_data = state.get("document_data")

    if not document_number:
        logger.warning("[pdf node] No document number provided")
        conversation_state["awaiting_document_number"] = True
        state["conversation_state"] = conversation_state
        return {"next_node": "supervisor", "conversation_state": conversation_state}

    if not result_data or not result_data.get("creditos"):
        msg = f"El documento {document_number} no posee movimientos o información."
        logger.info(f"[pdf node] {msg}")
        return {
            "next_node": "chat",
            "conversation_state": conversation_state,
            "message": msg
        }

    try:
        print("DEBUG DATA >>>", result_data)
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_PATH),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template(TEMPLATE_FILE)
        html_content = template.render(
            document_number=document_number,
            data=result_data
        )

        # Carpeta de salida
        output_dir = os.path.join("app", "core", "pdf_chat", "generated_pdfs")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"certificado_{document_number}.pdf"
        pdf_path = os.path.join(output_dir, filename)

        # Generar PDF con WeasyPrint
        # Si tienes CSS externo en la plantilla, puedes cargarlo con CSS(filename="ruta.css")
        HTML(string=html_content, base_url=TEMPLATE_PATH).write_pdf(pdf_path)


        # Leer bytes del PDF generado
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        success_message = f"Se generó el PDF satisfactoriamente para el documento {document_number}."
        logger.info(f"[pdf node] {success_message}")
        logger.info(f"[pdf node] Ruta del PDF: {pdf_path}")

        # Actualizar estado
        state.update({
            "pdf_bytes": pdf_bytes,
            "pdf_filename": filename,
            "conversation_state": conversation_state,
            "pdf_path": pdf_path,
            "message": success_message,
            "next_node": "chat"
        })

        return state

    except Exception as e:
        logger.error(f"[pdf node] Error generando PDF: {str(e)}", exc_info=True)
        return {
            "next_node": "chat",
            "conversation_state": conversation_state,
            "error": f"Error al generar el PDF: {str(e)}"
        }
