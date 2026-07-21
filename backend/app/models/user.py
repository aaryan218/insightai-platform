from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Index
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    email = Column(String(320), nullable=False, unique=True, index=True)
    hashed_password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)


Index("ix_users_email", User.email)
