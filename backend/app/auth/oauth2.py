from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# tokenUrl just tells the OpenAPI/Swagger UI where to POST for a token (for the "Authorize" button).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")