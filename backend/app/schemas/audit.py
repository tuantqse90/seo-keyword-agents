from uuid import UUID

from pydantic import BaseModel


class AuditIssueOut(BaseModel):
    id: UUID
    severity: str
    category: str
    title: str
    description: str | None
    fix_suggestion: str | None
    code_snippet: str | None
    effort_level: str | None

    model_config = {"from_attributes": True}


class AuditResultOut(BaseModel):
    id: UUID
    overall_score: int | None
    letter_grade: str | None
    quick_wins: dict | None
    tech_checklist: dict | None
    issues: list[AuditIssueOut]

    model_config = {"from_attributes": True}


class AuditReportOut(BaseModel):
    report: "ReportOut"
    audit_result: AuditResultOut | None

    model_config = {"from_attributes": True}


from app.schemas.report import ReportOut  # noqa: E402

AuditReportOut.model_rebuild()
