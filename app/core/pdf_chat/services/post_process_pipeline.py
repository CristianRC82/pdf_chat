from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.llm.azure_open_ai import llm_miniA
from app.core.pdf_chat.prompts.post_proccess_prompt import system_prompt_postprocessing

""" service in charge of managing the post process node """

postprocessing_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_postprocessing),
        ("human", "La pregunta original del usuario fue: '{original_question}'\n\nLa descripcion de la consulta que mando a realizar fue: '{task_description}'\n\nLos datos crudos obtenidos de la base de datos son:\n{raw_sql_results}\n\nInterpreta estos datos y genera la respuesta final."),
    ]
)

postprocessing_chain = postprocessing_prompt_template | llm_miniA | StrOutputParser()