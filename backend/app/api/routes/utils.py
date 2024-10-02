from fastapi import APIRouter
from app.core.config import settings
from fastapi import APIRouter

router = APIRouter()


@router.get("/resolve")
def status():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "testing": "hello world",
        "settings": {
            "API_V1_STR": settings.API_V1_STR,
            "PROJECT_NAME": settings.PROJECT_NAME,
        },
    }


__all__ = ["router"]
