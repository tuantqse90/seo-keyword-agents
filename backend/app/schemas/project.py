from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    url: str | None = None
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    description: str | None = None


class ProjectOut(BaseModel):
    id: UUID
    name: str
    url: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
