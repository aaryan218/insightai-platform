from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="InsightAI Platform API")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers lazily to avoid import cycles
    from app.api.v1.routes import auth as auth_router

    app.include_router(
        auth_router.router,
        prefix=settings.API_V1_PREFIX,
    )

    return app


app = create_app()