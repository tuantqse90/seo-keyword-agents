from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.report import ReportModule, ReportStatus


class AnalyzeRequest(BaseModel):
    query: str
    project_id: UUID | None = None


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
