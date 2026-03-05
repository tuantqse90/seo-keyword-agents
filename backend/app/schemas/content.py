from uuid import UUID

from pydantic import BaseModel


class ContentBriefOut(BaseModel):
    id: UUID
    title_tag: str | None
    meta_description: str | None
    target_word_count: int | None
    outline: dict | None
    lsi_keywords: dict | None
    snippet_strategy: str | None
    eeat_signals: dict | None

    model_config = {"from_attributes": True}


class ContentReportOut(BaseModel):
    report: "ReportOut"
    content_brief: ContentBriefOut | None

    model_config = {"from_attributes": True}


from app.schemas.report import ReportOut  # noqa: E402

ContentReportOut.model_rebuild()
