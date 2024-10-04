from fastapi import APIRouter
from app.core.config import settings
from fastapi import APIRouter
from app.utils.system import get_system_metrics

router = APIRouter()


# default system health check
@router.get("/", tags=["utils"])
def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "testing": "hello world",
        "settings": {
            "API_V1_STR": settings.API_V1_STR,
            "PROJECT_NAME": settings.PROJECT_NAME,
        },
    }


# resolves current capacity utilisation
@router.get("/capacity", tags=["utils"])
def measure_system_capacity():
    metrics = get_system_metrics()
    return metrics


__all__ = ["router"]
