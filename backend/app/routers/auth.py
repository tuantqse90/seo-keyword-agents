from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth_service import hash_password, verify_password, create_token, create_refresh_token, refresh_access_token, require_auth

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
