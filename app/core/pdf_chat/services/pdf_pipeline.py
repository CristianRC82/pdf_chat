from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.llm.azure_open_ai import llm_miniA
from app.core.pdf_chat.prompts.pdf_prompt import system_prompt_postprocessing

""" Service in charge of post-processing node """

postprocessing_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_postprocessing),
        ("human", "La pregunta original del usuario fue: '{original_question}'\n\n"
                  "La descripción de la consulta enviada fue: '{task_description}'\n\n"
                  "Los datos crudos obtenidos de la base de datos son:\n{raw_sql_results}\n\n"
                  "Genera un JSON listo para la plantilla HTML si corresponde."),
    ]
)

postprocessing_chain = postprocessing_prompt_template | llm_miniA | StrOutputParser()
