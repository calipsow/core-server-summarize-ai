from fastapi import APIRouter

from app.api.routes import utils, service

api_router = APIRouter()


api_router.include_router(utils.router, prefix="/utils", tags=["utils"])


api_router.include_router(service.router, prefix="/service", tags=["service"])
