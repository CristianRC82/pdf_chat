import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_postprocessing_pdf_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("---NODE: Postprocessing (PDF Preparation)---")

    document_number = state.get("document_number")
    logger.info(f"[postprocessing] Document number: {document_number}")
    #name_client = state.get("nombre_cliente")
    sql_results = state.get("document_data")

    if not document_number or not sql_results:
        logger.warning("[postprocessing] No valid SQL results found. Passing empty data to PDF.")
        state["document_data"] = {}
    else:
        logger.info(f"[postprocessing] Data ready for PDF generation for {document_number}")

    return state
