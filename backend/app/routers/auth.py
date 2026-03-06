import logging
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth_service import hash_password, verify_password, create_token, create_refresh_token, refresh_access_token, require_auth

logger = logging.getLogger("app.auth")

# In-memory reset tokens: {token: {email, expires_at}}
_reset_tokens: dict[str, dict] = {}

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        import re
        v = v.strip()
        v = re.sub(r"<[^>]+>", "", v)
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class AuthResponse(BaseModel):
    token: str
    refresh_token: str
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str

    model_config = {"from_attributes": True}


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check existing
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email da ton tai")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        name=data.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(str(user.id))
    r_token = create_refresh_token(str(user.id))
    return AuthResponse(
        token=token,
        refresh_token=r_token,
        user={"id": str(user.id), "email": user.email, "name": user.name, "role": user.role},
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Email hoac mat khau khong dung")

    token = create_token(str(user.id))
    r_token = create_refresh_token(str(user.id))
    return AuthResponse(
        token=token,
        refresh_token=r_token,
        user={"id": str(user.id), "email": user.email, "name": user.name, "role": user.role},
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token for a new access + refresh token pair."""
    result = await refresh_access_token(data.refresh_token, db)
    user = result["user"]
    return AuthResponse(
        token=result["token"],
        refresh_token=result["refresh_token"],
        user={"id": str(user.id), "email": user.email, "name": user.name, "role": user.role},
    )


@router.get("/me")
async def get_me(user: User = Depends(require_auth)):
    return {"id": str(user.id), "email": user.email, "name": user.name, "role": user.role}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request a password reset. Always returns success (no email enumeration)."""
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = {
            "email": data.email,
            "expires_at": datetime.utcnow() + timedelta(hours=1),
        }
        logger.info(f"Password reset token generated for {data.email}")

        # Send email if SMTP configured
        try:
            from app.services.email_service import send_notification
            from app.config import settings
            if settings.smtp_host:
                await send_notification(
                    to_email=data.email,
                    subject="SEO Dashboard — Dat lai mat khau",
                    html_body=f"""
                    <p>Ban da yeu cau dat lai mat khau.</p>
                    <p>Ma xac nhan cua ban: <strong>{token}</strong></p>
                    <p>Ma nay het han sau 1 gio.</p>
                    <p>Neu ban khong yeu cau, hay bo qua email nay.</p>
                    """,
                )
        except Exception:
            pass  # Email is best-effort

    # Always return success to prevent email enumeration
    return {"message": "Neu email ton tai, chung toi da gui huong dan dat lai mat khau."}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using a reset token."""
    token_data = _reset_tokens.get(data.token)
    if not token_data:
        raise HTTPException(400, "Token khong hop le hoac da het han")

    if datetime.utcnow() > token_data["expires_at"]:
        _reset_tokens.pop(data.token, None)
        raise HTTPException(400, "Token da het han")

    stmt = select(User).where(User.email == token_data["email"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(400, "Token khong hop le")

    user.hashed_password = hash_password(data.new_password)
    await db.commit()

    # Invalidate used token
    _reset_tokens.pop(data.token, None)

    return {"message": "Mat khau da duoc dat lai thanh cong"}


@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    """Change password for authenticated user."""
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(400, "Mat khau hien tai khong dung")

    user.hashed_password = hash_password(data.new_password)
    await db.commit()

    return {"message": "Mat khau da duoc thay doi thanh cong"}
