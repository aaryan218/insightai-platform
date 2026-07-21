from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    UserCreate,
    UserOut,
    LoginRequest,
    Token,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    VerifyEmailRequest,
)
from app.core.database import get_db
from app.services import auth_service
from app.services.email_service import email_service
from app.dependencies.auth import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(db, payload.name, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # send verification email (dev-mode prints link)
    token = await auth_service.create_email_verification_token(db, user)
    verify_link = f"/api/auth/verify-email?token={token}"
    email_service.send(user.email, "Verify your email", f"Click here: {verify_link}")
    return user


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = auth_service.jwt_handler.create_access_token(str(user.id))
    refresh = auth_service.jwt_handler.create_refresh_token(str(user.id))
    # store refresh
    await auth_service.create_refresh_token_entry(db, refresh, user)
    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh", response_model=Token)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    res = await auth_service.refresh_tokens(db, req.refresh_token)
    if not res:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return {"access_token": res["access_token"], "refresh_token": res["refresh_token"]}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = auth_service.jwt_handler.decode_token(req.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    jti = payload.get("jti")
    await auth_service.revoke_refresh_token(db, jti)
    return None


@router.get("/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return user


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Do not reveal whether user exists
    q = await db.execute(auth_service.select_user_by_email(req.email))
    user = q.scalars().first()
    if user:
        token = await auth_service.create_password_reset_token(db, user)
        reset_link = f"/api/auth/reset-password?token={token}"
        email_service.send(user.email, "Reset your password", f"Reset link: {reset_link}")
    return None


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = auth_service.jwt_handler.decode_token(req.token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    if payload.get("type") != "reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")
    user_id = int(payload.get("sub"))
    q = await db.execute(auth_service.select_user_by_id(user_id))
    user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    # update password
    user.hashed_password = auth_service.hash_password(req.new_password)
    # revoke all refresh tokens for user
    await auth_service.revoke_all_refresh_tokens_for_user(db, user.id)
    db.add(user)
    await db.commit()
    return {"ok": True}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(req: ChangePasswordRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not auth_service.verify_password(req.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid current password")
    user.hashed_password = auth_service.hash_password(req.new_password)
    db.add(user)
    await db.commit()
    # revoke refresh tokens
    await auth_service.revoke_all_refresh_tokens_for_user(db, user.id)
    return {"ok": True}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(req: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = auth_service.jwt_handler.decode_token(req.token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    if payload.get("type") != "verify":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")
    user_id = int(payload.get("sub"))
    q = await db.execute(auth_service.select_user_by_id(user_id))
    user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user.is_verified = True
    db.add(user)
    await db.commit()
    return {"ok": True}


@router.post("/admin-only", dependencies=[Depends(require_admin)])
async def admin_only():
    return {"ok": True}
