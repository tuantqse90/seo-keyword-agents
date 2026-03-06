from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.report import ReportModule, ReportStatus


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    project_id: UUID | None = None

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        from app.utils.validators import sanitize_input
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return sanitize_input(v, max_length=2000)


class AnalyzeResponse(BaseModel):
    report_id: UUID
    stream_url: str


class ReportOut(BaseModel):
    id: UUID
    project_id: UUID | None
    module: ReportModule
    input_query: str
    status: ReportStatus
    raw_markdown: str | None
    summary: str | None
    metadata_json: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportListOut(BaseModel):
    id: UUID
    project_id: UUID | None
    module: ReportModule
    input_query: str
    status: ReportStatus
    summary: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
