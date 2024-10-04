import pathlib
from dotenv import load_dotenv
import os
import secrets
import warnings
from typing import Annotated, Any, Literal


from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    computed_field,
)

from pydantic_settings import BaseSettings, SettingsConfigDict

df = os.path.join(pathlib.Path(__file__).parent.parent.parent.parent.absolute(), ".env")

print("LOADED ENV:", load_dotenv(df, verbose=True))


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=df,
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "")

    SENTRY_DSN: HttpUrl | None = None

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "db")

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    EMAIL_TEST_USER: str = "test@example.com"

    HF_TKN: str = os.getenv("HF_TKN", "")

    LLM_MODEL_ID: str = os.getenv("LLM_MODEL_ID", "")


settings = Settings()  # type: ignore
