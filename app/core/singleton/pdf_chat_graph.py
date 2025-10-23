import logging
from fastapi import HTTPException
from langgraph.graph import END, StateGraph
from typing import Dict, Any

# Estados y constantes
from ..pdf_chat.schemas.graph_const import CHAT, SQL, PDF, SUPERVISOR
from ..pdf_chat.schemas.graph_states import GraphState

# Nodos
from app.core.pdf_chat.graph.nodes.supervisor import supervisor_router_node
from app.core.pdf_chat.graph.nodes.chat import run_chat_agent_node
from app.core.pdf_chat.graph.nodes.sql import run_sql_agent_node
from app.core.pdf_chat.graph.nodes.pdf import run_pdf_agent_node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def route_question(state: GraphState):
    """
    Routing logic for the supervisor node.
    """
    route = state.get("route")
    if route == CHAT:
        return CHAT
    return SQL


class GraphSingleton:
    """
    Singleton that compiles and stores the LangGraph flow
    and generates a Mermaid PNG of the graph.
    """

    _instance = None
    _compiled_graph = None
    _graph_image_path = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("[GraphSingleton] Compiling the graph for the first time")
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes and compiles the LangGraph once.
        """
        if self._compiled_graph is None:
            self._compiled_graph = self._build_graph()
            self._generate_graph_image()

    def _build_graph(self):
        """
        Builds and compiles the LangGraph structure.
        """
        graph = StateGraph(GraphState)

        # Define nodes
        graph.add_node(SUPERVISOR, supervisor_router_node)
        graph.add_node(CHAT, run_chat_agent_node)
        graph.add_node(SQL, run_sql_agent_node)
        graph.add_node(PDF, run_pdf_agent_node)

        # Entry point
        graph.set_entry_point(SUPERVISOR)

        # Supervisor routing
        graph.add_conditional_edges(
            SUPERVISOR,
            route_question,
            {
                CHAT: CHAT,
                SQL: SQL,
            },
        )

        # SQL → PDF → END
        graph.add_edge(SQL, PDF)
        graph.add_edge(PDF, END)

        # CHAT → END
        graph.add_edge(CHAT, END)

        logger.info("[GraphSingleton] Chat flow successfully built.")
        return graph.compile()  # Compile simple, sin Redis ni callbacks

    def _generate_graph_image(self, output_file_path: str = "graph.png"):
        """
        Generates a PNG image of the graph using Mermaid via StateGraph.
        """
        try:
            self._compiled_graph.get_graph().draw_mermaid_png(output_file_path=output_file_path)
            self._graph_image_path = output_file_path
            logger.info(f"[GraphSingleton] Graph image generated at {output_file_path}")
        except Exception as e:
            logger.error("[GraphSingleton] Error generating graph image:", exc_info=True)

    def run(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the compiled graph using the given input and config.
        """
        try:
            return self._compiled_graph.invoke(input_data, config=config)
        except Exception as e:
            logger.error(
                "[GraphSingleton] Error executing the graph:", exc_info=True
            )
            raise HTTPException(status_code=500, detail="Internal server error")
