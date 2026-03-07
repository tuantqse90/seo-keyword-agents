from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth_service import require_admin, hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


class UserListItem(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    name: str | None = None
    role: str | None = Field(None, pattern=r"^(user|admin)$")
    is_active: bool | None = None


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field("user", pattern=r"^(user|admin)$")


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users with pagination and search."""
    query = select(User).order_by(User.created_at.desc())

    if search:
        query = query.where(
            (User.email.ilike(f"%{search}%")) | (User.name.ilike(f"%{search}%"))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "name": u.name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get user details."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update user role or status."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    # Prevent admin from deactivating themselves
    if str(user.id) == str(admin.id) and data.is_active is False:
        raise HTTPException(400, "Cannot deactivate your own account")

    # Prevent admin from removing their own admin role
    if str(user.id) == str(admin.id) and data.role and data.role != "admin":
        raise HTTPException(400, "Cannot remove your own admin role")

    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active

    await db.commit()
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/users", status_code=201)
async def create_user(
    data: CreateUserRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin creates a new user."""
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        name=data.name,
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if str(user.id) == str(admin.id):
        raise HTTPException(400, "Cannot delete your own account")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}
