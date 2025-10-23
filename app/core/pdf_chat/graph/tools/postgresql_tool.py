import logging
from psycopg2 import OperationalError
from langchain_core.tools import tool
from app.core.singleton.postgres import get_postgres_instance

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@tool("query_postgres_tool", return_direct=True)
def query_postgres_tool(query: str, max_rows_to_return: int = 20) -> str:
    """
    Executes a read-only SQL query (SELECT/WITH) in PostgreSQL and returns formatted results.
    Used by graph nodes that need to retrieve data from the database.

    Args:
        query (str): SQL query to execute (must be SELECT or WITH).
        max_rows_to_return (int, optional): Maximum number of rows to return. Defaults to 20.

    Returns:
        str: Formatted query results or an error message.
    """
    logger.info("[postgresql_tool] Starting query execution")

    if not query or not query.strip():
        return "Error: SQL query cannot be empty."

    first_word = query.strip().split()[0].upper()
    if first_word not in ("SELECT", "WITH"):
        return "Error: Only read-only queries (SELECT/WITH) are allowed."

    try:
        conn = get_postgres_instance()
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            if not rows:
                return "No results returned."

            limited_rows = rows[:max_rows_to_return]
            output_lines = [
                f"Results (showing {len(limited_rows)} of {len(rows)} rows):"
                if len(rows) > max_rows_to_return
                else "Results:"
            ]

            for row in limited_rows:
                output_lines.append(str(dict(zip(columns, row))))

            logger.info(f"[postgresql_tool] Query executed successfully ({len(rows)} rows).")
            return "\n".join(output_lines)

    except OperationalError as e:
        logger.error("[postgresql_tool] Database connection error:", exc_info=True)
        return f"Database connection error: {e}"

    except Exception as e:
        logger.error("[postgresql_tool] Unexpected error:", exc_info=True)
        return f"Unexpected error querying PostgreSQL: {e}"
