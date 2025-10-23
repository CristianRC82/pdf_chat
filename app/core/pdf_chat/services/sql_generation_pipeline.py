from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.pdf_chat.prompts.sql_generation_prompt import sql_generation_system_prompt
from app.core.llm.azure_open_ai import llm_3mini

""" service in charge of managing the sql_flow node """
sql_generation_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", sql_generation_system_prompt),
        ("human", "{question}"),
    ]
)
# La cadena final de generación de SQL
sql_generation_chain = sql_generation_prompt_template | llm_3mini | StrOutputParser()
#sql_generation_chain = sql_generation_prompt_template | llm_mini_03 | StrOutputParser()