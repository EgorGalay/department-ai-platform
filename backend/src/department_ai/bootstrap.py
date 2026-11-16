from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from department_ai.api.v1.router import api_router
from department_ai.core.config.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()
    app = FastAPI(title=app_settings.app_name, version=app_settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=app_settings.api_v1_prefix)
    return app
