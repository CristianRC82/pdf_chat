import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.pdf_chat.graph.tools.pdf_generator_tool import pdf_generator_tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Base project directory (current file location)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # Adjust to reach 'app' folder
TEMPLATE_PATH = BASE_DIR / "core" / "pdf_chat" / "graph" / "tools"
TEMPLATE_FILE = "certificado.html"

def run_pdf_agent_node(data: dict, file_name: str | None = None) -> str:
    """
    PDF node: receives a dictionary `data` with query results,
    fills the HTML template, and generates a PDF.

    Args:
        data (dict): Data to be inserted into the HTML template.
        file_name (str | None): Optional name for the generated PDF.

    Returns:
        str: Path to the generated PDF or an error message.
    """
    logger.info("[pdf node] Running PDF node")

    try:
        # Load the HTML template relative to the project directory
        env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
        template = env.get_template(TEMPLATE_FILE)
        html_content = template.render(data)  # Render HTML with the provided data

        # Generate PDF using the existing tool
        result = pdf_generator_tool(html_content, file_name)
        logger.info("[pdf node] PDF generation finished")
        return result

    except Exception as e:
        logger.error("[pdf node] Error generating PDF", exc_info=True)
        return f"Error in PDF node: {e}"
