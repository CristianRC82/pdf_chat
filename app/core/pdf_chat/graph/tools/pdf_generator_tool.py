import logging
import os
import tempfile
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from langchain_core.tools import tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _generate_pdf_from_text(text: str, output_path: str) -> str:
    """
    Internal helper that generates a PDF file from text using reportlab.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER

    # Dividir el texto en líneas para no salir del límite de la página
    lines = text.split("\n")
    y = height - 50  # margen superior
    for line in lines:
        c.drawString(50, y, line)
        y -= 15
        if y < 50:  # crear nueva página si se llega al margen inferior
            c.showPage()
            y = height - 50

    c.save()
    return output_path


@tool
def pdf_generator_tool(text_content: str, file_name: str | None = None) -> str:
    """
    Tool that generates a PDF from text content using reportlab.

    :param text_content: Text string to convert into PDF.
    :param file_name: Optional filename. If not provided, a temp name is generated.
    :return: Path to the generated PDF or an error message.
    """
    logger.info("[pdf_generator_tool] Starting PDF generation")

    if not text_content or not text_content.strip():
        return "Error: Text content cannot be empty."

    try:
        # Determine output filename
        if file_name and file_name.strip():
            safe_name = file_name
        else:
            fd, tmp_path = tempfile.mkstemp(prefix="pdf_", suffix=".pdf")
            os.close(fd)
            safe_name = os.path.basename(tmp_path)

        output_path = os.path.join(tempfile.gettempdir(), safe_name)

        pdf_path = _generate_pdf_from_text(text_content, output_path)
        logger.info(f"[pdf_generator_tool] PDF generated at: {pdf_path}")
        return f"PDF generated successfully: {pdf_path}"

    except Exception as e:
        logger.error("[pdf_generator_tool] Error generating PDF", exc_info=True)
        return f"Error generating PDF: {e}"
