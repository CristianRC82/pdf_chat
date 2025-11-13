import logging
import re
from typing import Dict, Any
from app.core.singleton.postgres import get_postgres_instance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOCUMENT_REGEX = r"\b\d{6,11}\b"


def run_sql_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch data from PostgreSQL based on a document number and return structured info.
    """
    logger.info("---NODE: SQL Agent---")

    question = state.get("question", "")
    document_number = state.get("document_number")

    # 🔹 Intentar extraer número de documento si no viene explícito
    if not document_number:
        match = re.search(DOCUMENT_REGEX, question)
        if match:
            document_number = match.group(0)
            logger.info(f"Extracted document number: {document_number}")
        else:
            logger.warning("No document number found in question.")
            return {**state, "next_node": "supervisor"}

    logger.info(f"Running SQL for document: {document_number}")

    query = """
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
        WHERE c.documento = %s;
    """

    try:
        conn = get_postgres_instance()
        with conn.cursor() as cursor:
            cursor.execute(query, (document_number,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

        if not rows:
            logger.warning(f"No data found for document: {document_number}")
            return {
                **state,
                "document_number": document_number,
                "document_data": {},
                "sql_results": None,
                "next_node": "postprocessing",
            }

        # 🔹 Convertir filas a diccionarios
        result_rows = [dict(zip(columns, row)) for row in rows]

        # 🔹 Estructura base del resultado
        result = {
            "nombre_cliente": result_rows[0]["nombre_cliente"],
            "cedula": result_rows[0]["cedula"],
            "creditos": []
        }

        # 🔹 Agrupar créditos y pagos
        credit_dict = {}
        for row in result_rows:
            credit_id = row["numero_cuenta"]
            if credit_id not in credit_dict:
                credit_dict[credit_id] = {
                    "numero_cuenta": credit_id,  # ✅ AHORA SE INCLUYE EN EL RESULTADO
                    "monto_total": row["monto_total"],
                    "fecha_emision": row["fecha_emision"],
                    "pagos": []
                }

            if row["numero_cuota"]:
                credit_dict[credit_id]["pagos"].append({
                    "numero_cuota": row["numero_cuota"],
                    "valor_cuota": row["valor_cuota"],
                    "fecha_pago": row["fecha_pago"],
                    "estado_pago": row["estado_pago"]
                })

        # 🔹 Añadir créditos a la respuesta
        result["creditos"] = list(credit_dict.values())

        new_state = {
            **state,
            "document_number": document_number,
            "document_data": result,
            "sql_results": result,
            "next_node": "postprocessing"
        }

        logger.info(f"Retrieved data successfully for document {document_number}")
        logger.debug(f"[sql node] Outgoing state sample: {result['creditos'][:1]}")

        return new_state

    except Exception as e:
        logger.exception(f"Error running SQL for document {document_number}: {e}")
        return {
            **state,
            "document_number": document_number,
            "document_data": {},
            "sql_results": None,
            "error": str(e),
            "next_node": "postprocessing"
        }
