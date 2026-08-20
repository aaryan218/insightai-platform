from functools import lru_cache

from pydantic import AnyUrl, Field         #type: ignore
from pydantic_settings import BaseSettings, SettingsConfigDict      #type:ignore


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl | str = "sqlite+aiosqlite:///./dev.db"
    SECRET_KEY: str = Field(..., validation_alias="JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    BCRYPT_ROUNDS: int = 12
 
    API_V1_PREFIX: str = "/api"

    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()