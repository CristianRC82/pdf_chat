from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.llm.azure_open_ai import llm_miniA
from app.core.pdf_chat.prompts.chat_prompt import system_prompt_chat
""" service in charge of managing the chat node"""
chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_chat),
        ("human", "{user_input}"),
    ]
)

chat_chain = chat_prompt_template | llm_miniA | StrOutputParser()