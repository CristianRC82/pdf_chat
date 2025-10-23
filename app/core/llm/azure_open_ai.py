from langchain_openai import AzureChatOpenAI
from app.core.config import settings
from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_API_KEY = settings.AZURE_OPENAI_API_KEY
llm_miniA = AzureChatOpenAI(
    azure_endpoint= settings.AZURE_OPENAI_ENDPOINT,
    azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    temperature=0.0,
)
llm_3mini = AzureChatOpenAI(
    azure_endpoint= settings.AZURE_OPENAI_ENDPOINT_o3_MINI,
    azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME_o3_MINI,
    api_version=settings.AZURE_OPENAI_API_VERSION_o3_MINI,
)