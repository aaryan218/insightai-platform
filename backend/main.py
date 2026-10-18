from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    status,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import json
import logging
from dotenv import load_dotenv

load_dotenv()

from models import (
    SignupRequest,
    LoginRequest,
    DeleteUserRequest,
    AddTokensRequest,
    TrainResponse,
    PredictResponse,
    parse_features,
    create_jwt,
    decode_jwt,
)

from dal import init_storage

from bl import (
    bl_signup,
    bl_login,
    bl_delete_user,
    bl_add_tokens,
    bl_get_tokens,
    require_tokens,
    df_from_upload,
    train_model,
    predict_latest,
    list_user_models,
    compute_eda,
    generate_eda_html_report,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_storage()
    logging.info("Application started")
    yield


app = FastAPI(
    title="ML Model Server",
    description="FastAPI backend for training and serving machine learning models",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUTHENTICATION
# ============================================================

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:

    token = credentials.credentials

    try:
        payload = decode_jwt(token)
        return str(payload["sub"])

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "online",
        "service": "ML Model Server",
    }


# ============================================================
# USER AUTHENTICATION
# ============================================================

@app.post("/signup")
def signup(req: SignupRequest):

    try:
        bl_signup(req.username, req.password)

        return {
            "status": "ok",
            "message": "User created successfully",
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@app.post("/login")
def login(req: LoginRequest):

    if not bl_login(req.username, req.password):

        raise HTTPException(
            status_code=401,
            detail="Bad credentials",
        )

    token = create_jwt(req.username)

    logging.info(
        f"User {req.username} logged in"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.delete("/remove_user")
def remove_user(
    req: DeleteUserRequest,
    current_user: str = Depends(get_current_username),
):

    if req.username != current_user:

        raise HTTPException(
            status_code=403,
            detail="Can delete only your own user",
        )

    try:

        bl_delete_user(
            req.username,
            req.password,
        )

        return {
            "status": "deleted"
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ============================================================
# TOKENS
# ============================================================

@app.get("/tokens/{username}")
def tokens(
    username: str,
    current_user: str = Depends(get_current_username),
):

    if username != current_user:

        raise HTTPException(
            status_code=403,
            detail="Can view only your own tokens",
        )

    return {
        "tokens": bl_get_tokens(username)
    }


@app.post("/add_tokens")
def add_tokens(
    req: AddTokensRequest,
    current_user: str = Depends(get_current_username),
):

    if req.username != current_user:

        raise HTTPException(
            status_code=403,
            detail="Can add tokens only to yourself",
        )

    if req.amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Amount must be positive",
        )

    tokens = bl_add_tokens(
        req.username,
        req.amount,
    )

    return {
        "status": "tokens added",
        "tokens": tokens,
    }


# ============================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================

@app.post("/eda")
async def eda(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_username),
):
    """
    Perform automated Exploratory Data Analysis (EDA) on an uploaded CSV file.
    Does not consume tokens.
    """
    content = await file.read()
    try:
        df = df_from_upload(content)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file",
        )

    try:
        results = compute_eda(df)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error computing EDA: {str(e)}",
        )


@app.post("/eda/report")
async def eda_report(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_username),
):
    """
    Generate a complete, self-contained HTML EDA report for download.
    Does not consume tokens.
    """
    content = await file.read()
    try:
        df = df_from_upload(content)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file",
        )

    try:
        results = compute_eda(df)
        html_content = generate_eda_html_report(
            df,
            results,
            dataset_name=file.filename or "Uploaded Dataset",
        )
        safe_filename = file.filename or "dataset.csv"
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f'attachment; filename="eda_report_{safe_filename}.html"'
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating EDA report: {str(e)}",
        )


# ============================================================
# TRAIN MODEL
# ============================================================

@app.post(
    "/train",
    response_model=TrainResponse,
)
async def train(
    model_name: str = Form(...),
    features: str = Form(...),
    label: str = Form(...),
    file: UploadFile = File(...),
    model_params: Optional[str] = Form(None),
    current_user: str = Depends(get_current_username),
):

    # Training costs 1 token
    try:

        require_tokens(
            current_user,
            1,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=402,
            detail=str(e),
        )

    # Read CSV
    content = await file.read()

    try:

        df = df_from_upload(content)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file",
        )

    # Parse selected features
    feats = parse_features(features)

    # Parse optional model parameters
    params: Dict[str, Any] = {}

    if model_params:

        try:

            params = json.loads(
                model_params
            )

        except Exception:

            params = {}

    # Train model
    try:

        result = train_model(
            current_user,
            df,
            model_name,
            feats,
            label,
            params,
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ============================================================
# LIST USER MODELS
# ============================================================

@app.get("/models")
def models(
    current_user: str = Depends(get_current_username),
):

    # IMPORTANT:
    # Listing models should NOT consume tokens.
    return {
        "models": list_user_models(
            current_user
        )
    }


# ============================================================
# PREDICT
# ============================================================

@app.post(
    "/predict/{model_name}",
    response_model=PredictResponse,
)
def predict(
    model_name: str,
    body: Dict[str, Any],
    current_user: str = Depends(get_current_username),
):

    # Prediction costs 5 tokens
    try:

        require_tokens(
            current_user,
            5,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=402,
            detail=str(e),
        )

    try:

        prediction = predict_latest(
            current_user,
            model_name,
            body,
        )

        return {
            "prediction": prediction
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )