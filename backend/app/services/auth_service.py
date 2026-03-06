"""JWT authentication service with access + refresh tokens."""

import uuid
from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    pw = password[:72].encode("utf-8")
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw = plain[:72].encode("utf-8")
    return bcrypt.checkpw(pw, hashed.encode("utf-8"))


def create_token(user_id: str) -> str:
    """Create short-lived access token."""
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create long-lived refresh token (30 days)."""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict:
    """Exchange refresh token for new access + refresh token pair."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(User, uuid.UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return {
        "token": create_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "user": user,
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns current user if auth header present, None otherwise."""
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if payload.get("type") == "refresh":
        return None  # Don't allow refresh tokens for API access
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = await db.get(User, uuid.UUID(user_id))
    if not user or not user.is_active:
        return None
    return user


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Requires authentication. Returns user or raises 401."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await get_current_user(credentials, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_admin(
    user: User = Depends(require_auth),
) -> User:
    """Requires admin role. Returns user or raises 403."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
