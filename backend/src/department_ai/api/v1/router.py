from fastapi import APIRouter

from department_ai.api.v1.endpoints.health import router as health_router
from department_ai.modules.identity.presentation.router import router as identity_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(identity_router)
