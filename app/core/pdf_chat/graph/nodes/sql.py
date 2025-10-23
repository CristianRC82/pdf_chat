import logging
from app.core.pdf_chat.graph.tools.postgresql_tool import query_postgres_tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run_sql_agent_node(documento: str) -> str:
    """
    SQL node: builds a fixed query for a given client document
    and executes it through the PostgreSQL tool.
    """
    logger.info("[sql node] Executing SQL node")

    if not documento or not documento.strip():
        return "Error: Client document cannot be empty."

    query = f"""
        SELECT 
            c.nombre AS nombre_cliente,
            c.documento AS cedula,
            cr.id_credito AS numero_cuenta,
            cr.monto_total,
            cr.fecha_aprobacion AS fecha_emision,
            p.id_pago AS numero_cuota,
            p.monto AS valor_cuota,
            p.fecha_pago,
            CASE 
                WHEN p.fecha_pago > CURRENT_DATE THEN 'Pendiente'
                ELSE 'Pagado'
            END AS estado_pago
        FROM clientes c
        JOIN creditos cr ON c.id_cliente = cr.id_cliente
        LEFT JOIN pagos p ON cr.id_credito = p.id_credito
        WHERE c.documento = '{documento}';
    """

    try:
        result = query_postgres_tool(query=query)
        logger.info(f"[sql node] Query executed for document {documento}")
        return result
    except Exception as e:
        logger.error("[sql node] Error running query:", exc_info=True)
        return f"Error executing query: {e}"
