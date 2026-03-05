from uuid import UUID

from pydantic import BaseModel


class CompetitorOut(BaseModel):
    id: UUID
    name: str
    url: str | None
    estimated_traffic: int | None
    domain_authority: int | None
    top_keywords: dict | None
    strengths: dict | None
    weaknesses: dict | None

    model_config = {"from_attributes": True}


class KeywordGapOut(BaseModel):
    id: UUID
    keyword: str
    target_rank: int | None
    competitor_ranks: dict | None

    model_config = {"from_attributes": True}


class CompetitorReportOut(BaseModel):
    report: "ReportOut"
    competitors: list[CompetitorOut]
    keyword_gaps: list[KeywordGapOut]

    model_config = {"from_attributes": True}


from app.schemas.report import ReportOut  # noqa: E402

CompetitorReportOut.model_rebuild()
