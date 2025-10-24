from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.llm.azure_open_ai import llm_miniA
from app.core.pdf_chat.schemas.supervisor_schema import RouteQuery
from app.core.pdf_chat.prompts.supervisor_prompt import system

structured_llm_router = llm_miniA.with_structured_output(RouteQuery)
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router
