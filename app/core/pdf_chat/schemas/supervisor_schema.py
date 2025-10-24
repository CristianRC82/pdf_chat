from pydantic import BaseModel, Field
from typing import Literal

class RouteQuery(BaseModel):
    """Defines the routing decision for a user query"""

    datasource: Literal["sql_flow", "chat_flow"] = Field(
        ...,
        description="Dada una pregunta de usuario, decide si debe enrutarse a 'sql_flow' (para consultas de datos que requieren certificados) o 'chat_flow' (para saludos, preguntas generales o cualquier otra cosa que no sea una consulta de datos específica).",
    )
    task_description: str = Field(
        ...,
        description="Una instrucción o pregunta clara y directa para el siguiente agente, que incluye todo el contexto necesario del historial de la conversación."
    )