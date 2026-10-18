from pydantic import BaseModel
from typing import List, Dict, Any
import time, os, json, jwt

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

try:
    from xgboost import XGBRegressor, XGBClassifier
except Exception:
    pass

# ===== JWT =====
SECRET_KEY = os.environ.get("APP_SECRET_KEY", "change_me_in_prod")
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 60 * 4  # 4h

def create_jwt(username: str) -> str:
    now = int(time.time())
    payload = {"sub": username, "iat": now, "exp": now + TOKEN_TTL_SECONDS}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class DeleteUserRequest(BaseModel):
    username: str
    password: str

class AddTokensRequest(BaseModel):
    username: str
    credit_card: str
    amount: int

class TrainResponse(BaseModel):
    status: str
    model_name: str
    features: List[str]
    label: str
    metrics: Dict[str, float]
    created_at: str

class PredictResponse(BaseModel):
    prediction: float | int

# ===== Utilities =====
def parse_features(raw) -> List[str]:
    if isinstance(raw, list):
        return [str(x).strip() for x in raw]
    s = str(raw).strip()
    try:
        arr = json.loads(s)
        if isinstance(arr, list):
            return [str(x).strip() for x in arr]
    except Exception:
        pass
    return [p.strip().strip('"').strip("'") for p in s.split(",") if p.strip()]

MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "linear":        {"type": "regression",    "ctor": LinearRegression},
    "random_forest": {"type": "regression",    "ctor": RandomForestRegressor},
    "logistic":      {"type": "classification","ctor": LogisticRegression},
    "svr":           {"type": "regression",    "ctor": SVR},
}
try:
    MODEL_REGISTRY["xgboost"] = {"type": "regression", "ctor": XGBRegressor}
except Exception:
    pass
