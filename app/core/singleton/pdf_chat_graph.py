import logging
from typing import Dict, Any
from langgraph.graph import END, StateGraph
from fastapi import HTTPException

from app.core.pdf_chat.schemas.graph_const import CHAT, SQL, PDF, SUPERVISOR, POSTPROCESSING
from app.core.pdf_chat.schemas.graph_states import GraphState
from app.core.pdf_chat.graph.nodes.supervisor import supervisor_router_node
from app.core.pdf_chat.graph.nodes.chat import run_chat_agent_node
from app.core.pdf_chat.graph.nodes.sql import run_sql_agent_node
from app.core.pdf_chat.graph.nodes.pdf import run_pdf_agent_node
from app.core.pdf_chat.graph.nodes.postprocessing import run_postprocessing_pdf_node
from app.core.singleton.postgres import get_postgres_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphSingleton:
    """
    Singleton que compila y mantiene el grafo de LangGraph para el flujo PDF Chat.
    Valida la conexión a PostgreSQL al inicializarse y permite ejecutar el grafo
    completo con un estado inicial.
    """

    _instance = None
    _compiled_graph = None
    _db_connection = None
    _graph_image_path = None

    def __new__(cls):
        """
        Crea y retorna una única instancia de la clase.
        Si no existe, la inicializa y compila el grafo.
        """
        if cls._instance is None:
            logger.info("[GraphSingleton] First-time graph compilation initiated.")
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Inicializa el grafo y verifica la conexión a PostgreSQL.
        """
        try:
            if self._compiled_graph is None:
                logger.info("[GraphSingleton] Building the LangGraph...")
                self._compiled_graph = self._build_graph()
                self._generate_graph_image()

            if self._db_connection is None:
                logger.info("[GraphSingleton] Connecting to PostgreSQL...")
                self._db_connection = get_postgres_instance()

                with self._db_connection.cursor() as cur:
                    cur.execute("SELECT 1;")
                    result = cur.fetchone()
                    if result and result[0] == 1:
                        logger.info("[GraphSingleton] PostgreSQL connection verified successfully.")
                    else:
                        logger.warning("[GraphSingleton] Unexpected result testing DB connection.")

            logger.info("[GraphSingleton] Initialization completed successfully.")

        except Exception as e:
            logger.error("[GraphSingleton] Initialization error", exc_info=True)
            raise RuntimeError(f"Graph initialization failed: {e}")

    def _build_graph(self):
        """
        Construye el grafo LangGraph con sus nodos y rutas condicionales.
        """
        try:
            graph = StateGraph(GraphState)

            # --- Nodos ---
            graph.add_node(SUPERVISOR, supervisor_router_node)
            graph.add_node(CHAT, run_chat_agent_node)
            graph.add_node(SQL, run_sql_agent_node)
            graph.add_node(POSTPROCESSING, run_postprocessing_pdf_node)
            graph.add_node(PDF, run_pdf_agent_node)

            graph.set_entry_point(SUPERVISOR)

            def route_selector(state: GraphState):
                route = state.get("route", "").lower()
                if route in [CHAT, SQL]:
                    return route
                logger.warning(f"[Graph] Unknown route '{route}', defaulting to {CHAT}")
                return CHAT

            graph.add_conditional_edges(
                SUPERVISOR,
                route_selector,
                {
                    CHAT: CHAT,
                    SQL: SQL,
                },
            )

            graph.add_edge(SQL, POSTPROCESSING)
            graph.add_edge(POSTPROCESSING, PDF)
            graph.add_edge(PDF, END)
            graph.add_edge(CHAT, END)

            return graph.compile()

        except Exception as e:
            logger.error("[GraphSingleton] Error while building the graph.", exc_info=True)
            raise RuntimeError(f"Graph build failed: {e}")

    def _generate_graph_image(self, output_file_path: str = "graph.png"):
        """
        Genera una imagen visual del grafo para depuración (opcional).
        """
        try:
            self._compiled_graph.get_graph().draw_mermaid_png(output_file_path=output_file_path)
            self._graph_image_path = output_file_path
        except Exception:
            logger.warning("[GraphSingleton] Unable to generate graph image (optional).")

    def run(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el grafo con los datos de entrada y configuración.
        """
        try:
            result = self._compiled_graph.invoke(input_data, config=config)
            return result
        except Exception as e:
            logger.error("[GraphSingleton] Error executing the graph.", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
