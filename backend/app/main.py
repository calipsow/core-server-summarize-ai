import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

print(
    f"Running in environment: {settings.ENVIRONMENT}",
    f"Project name: {settings.PROJECT_NAME}",
    f"API version: {settings.API_V1_STR}",
    f"Origins: {settings.all_cors_origins}",
    f"Sentry DSN: {settings.SENTRY_DSN}",
    f"Postgres server: {settings.POSTGRES_SERVER}",
    f"Postgres port: {settings.POSTGRES_PORT}",
    f"Postgres user: {settings.POSTGRES_USER}",
    f"Postgres db: {settings.POSTGRES_DB}",
    f"Postgres password: {'Yes' if settings.POSTGRES_PASSWORD else 'No'}",
    f"" f"SMTP host: {settings.SMTP_HOST}",
    f"SMTP user: {settings.SMTP_USER}",
    f"Emails from email: {settings.EMAILS_FROM_EMAIL}",
    f"Emails from name: {settings.EMAILS_FROM_NAME}",
    sep="\n",
)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
