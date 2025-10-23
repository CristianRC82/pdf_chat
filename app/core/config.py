from typing import Annotated, Any, Literal
from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env", env_ignore_empty=True, extra="ignore"
    )

    # --- General settings ---
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "creditos_api"
    ENV: Literal["local", "dev", "qa", "prod"] = "local"
    FRONTEND_HOST: str = "http://localhost:3000"


    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""
    AZURE_OPENAI_API_VERSION_o3_MINI: str = ""
    AZURE_OPENAI_ENDPOINT_o3_MINI: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME_o3_MINI: str = ""


    # --- PostgreSQL connection (local) ---
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = "8228"
    POSTGRES_DB: str = "creditos_db"


    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    @computed_field  # type: ignore
    @property
    def postgres_url(self) -> str:
        """
        Returns the full PostgreSQL connection URL.
        Example: postgresql://root:root@localhost:5432/creditos_db
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
