from langchain_core.prompts import ChatPromptTemplate
from app.core.magic_chat_flow.prompts.sql_verify_query_prompt import SQL_GRADER_SYSTEM_PROMPT
from app.core.llm.azure_open_ai import llm_3mini
from app.core.pdf_chat.schemas.check_sql_query_schema import GradeSQLQuery

"""service in charge of managing the verify query node """
structured_llm_sql_grader = llm_3mini.with_structured_output(GradeSQLQuery)

sql_grader_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", SQL_GRADER_SYSTEM_PROMPT),
        ("human", "Pregunta Original del Usuario:\n```{user_question}```\n\n"
                  "Consulta SQL Generada para Evaluar:\n```sql\n{generated_sql}\n```"),
    ]
)

sql_query_grader_chain = sql_grader_prompt_template | structured_llm_sql_grader