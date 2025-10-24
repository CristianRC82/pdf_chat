import logging
from psycopg2 import OperationalError
from langchain_core.tools import tool
from app.core.singleton.postgres import get_postgres_instance

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@tool("query_postgres_tool", return_direct=True)
def query_postgres_tool(query: str, max_rows_to_return: int = 20) -> str:
    """
    Executes a read-only SQL query on PostgreSQL and returns results as a list of dictionaries.
    Compatible with LangGraph nodes (PDF, logic, etc.)
    """
    logger.info("[postgresql_tool] Starting query execution")

    if not query or not query.strip():
        return "Error: la consulta SQL no puede estar vacía."

    first_word = query.strip().split()[0].upper()
    if first_word not in ("SELECT", "WITH"):
        return "Error: solo se permiten consultas de solo lectura (SELECT/WITH)."

    try:
        conn = get_postgres_instance()
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            if not rows:
                return "No se encontraron resultados."

            limited_rows = rows[:max_rows_to_return]
            output_lines = [
                f"Resultados (mostrando {len(limited_rows)} de {len(rows)} filas):"
                if len(rows) > max_rows_to_return
                else "Resultados:"
            ]

            for row in limited_rows:
                output_lines.append(str(dict(zip(columns, row))))

            logger.info(f"[postgresql_tool] Query executed successfully ({len(rows)} rows).")
            return "\n".join(output_lines)

    except OperationalError as e:
        logger.error("[postgresql_tool] Database connection error:", exc_info=True)
        return f"Error de conexión a la base de datos: {e}"

    except Exception as e:
        logger.error("[postgresql_tool] Unexpected error:", exc_info=True)
        return f"Error inesperado al consultar PostgreSQL: {e}"
