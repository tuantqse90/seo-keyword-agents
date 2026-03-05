from uuid import UUID

from pydantic import BaseModel


class KeywordOut(BaseModel):
    id: UUID
    keyword: str
    cluster: str | None
    search_volume: int | None
    keyword_difficulty: int | None
    search_intent: str | None
    cpc: float | None
    opportunity_score: int | None
    is_golden: bool

    model_config = {"from_attributes": True}


class KeywordReportOut(BaseModel):
    report: "ReportOut"
    keywords: list[KeywordOut]

    model_config = {"from_attributes": True}


from app.schemas.report import ReportOut  # noqa: E402

KeywordReportOut.model_rebuild()
