from pydantic import BaseSettings, AnyUrl
from functools import lru_cache
from pydantic import BaseSettings, AnyUrl, Field
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl | str = "sqlite+aiosqlite:///./dev.db"
    SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BCRYPT_ROUNDS: int = 12
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
