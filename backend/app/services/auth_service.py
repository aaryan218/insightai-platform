from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.auth.password_hashing import hash_password, verify_password
from app.core.config import settings
from app.auth import jwt_handler
from app.utils.hashing import random_token
from sqlalchemy import select, update


async def register_user(db: AsyncSession, name: str, email: str, password: str) -> User:
    # check exists
    q = select(User).where(User.email == email)
    existing = (await db.execute(q)).scalars().first()
    if existing:
        raise ValueError("Email already registered")

    user = User(
        name=name,
        email=email.lower(),
        hashed_password=hash_password(password),
        is_active=True,
        is_verified=False,
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    q = select(User).where(User.email == email.lower())
    user = (await db.execute(q)).scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_refresh_token_entry(db: AsyncSession, token: str, user: User):
    # token is raw jwt; hash and store with jti & expiry
    payload = jwt_handler.decode_token(token)
    jti = payload.get("jti")
    exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
    token_hash = jwt_handler.hash_token(token)
    rt = RefreshToken(jti=jti, user_id=user.id, token_hash=token_hash, expires_at=exp)
    db.add(rt)
    await db.commit()
    await db.refresh(rt)
    return rt


async def revoke_refresh_token(db: AsyncSession, jti: str):
    q = select(RefreshToken).where(RefreshToken.jti == jti)
    rt = (await db.execute(q)).scalars().first()
    if not rt:
        return False
    rt.revoked = True
    db.add(rt)
    await db.commit()
    return True


async def refresh_tokens(db: AsyncSession, refresh_token: str):
    try:
        payload = jwt_handler.decode_token(refresh_token)
    except Exception:
        return None
    if payload.get("type") != "refresh":
        return None
    jti = payload.get("jti")
    q = select(RefreshToken).where(RefreshToken.jti == jti)
    rt = (await db.execute(q)).scalars().first()
    if not rt or rt.revoked:
        return None
    if rt.expires_at < datetime.now(timezone.utc):
        return None

    # Issue new access token and rotate refresh token
    user_q = select(User).where(User.id == rt.user_id)
    user = (await db.execute(user_q)).scalars().first()
    if not user:
        return None

    access = jwt_handler.create_access_token(str(user.id))
    new_refresh = jwt_handler.create_refresh_token(str(user.id))
    # revoke old
    rt.revoked = True
    db.add(rt)
    await db.commit()
    # store new
    await create_refresh_token_entry(db, new_refresh, user)
    return {"access_token": access, "refresh_token": new_refresh}


def select_user_by_email(email: str):
    return select(User).where(User.email == email.lower())


def select_user_by_id(user_id: int):
    return select(User).where(User.id == int(user_id))


async def revoke_all_refresh_tokens_for_user(db: AsyncSession, user_id: int):
    q = select(RefreshToken).where(RefreshToken.user_id == user_id)
    rts = (await db.execute(q)).scalars().all()
    for rt in rts:
        rt.revoked = True
        db.add(rt)
    await db.commit()


async def create_password_reset_token(db: AsyncSession, user: User) -> str:
    # generate JWT token with type reset
    token = jwt_handler._create_token(str(user.id), timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES), "reset")
    return token


async def create_email_verification_token(db: AsyncSession, user: User) -> str:
    token = jwt_handler._create_token(str(user.id), timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES), "verify")
    return token
