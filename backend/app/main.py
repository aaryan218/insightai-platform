from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base


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

	# include routers lazily to avoid import cycles
	from app.api.v1.routes import auth as auth_router

	app.include_router(auth_router.router, prefix=f"{settings.API_V1_PREFIX}")

	@app.on_event("startup")
	async def startup() -> None:
		# create tables if they don't exist (useful for dev)
		async with engine.begin() as conn:
			await conn.run_sync(Base.metadata.create_all)

	return app


app = create_app()

