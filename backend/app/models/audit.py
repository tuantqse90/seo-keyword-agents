import uuid

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditResult(Base):
    __tablename__ = "audit_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    overall_score: Mapped[int | None] = mapped_column(Integer)
    letter_grade: Mapped[str | None] = mapped_column(String(5))
    quick_wins: Mapped[dict | None] = mapped_column(JSONB)
    tech_checklist: Mapped[dict | None] = mapped_column(JSONB)

    report: Mapped["Report"] = relationship(back_populates="audit_results")
    issues: Mapped[list["AuditIssue"]] = relationship(back_populates="audit_result", cascade="all, delete-orphan")


class AuditIssue(Base):
    __tablename__ = "audit_issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_results.id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    fix_suggestion: Mapped[str | None] = mapped_column(Text)
    code_snippet: Mapped[str | None] = mapped_column(Text)
    effort_level: Mapped[str | None] = mapped_column(String(50))

    audit_result: Mapped["AuditResult"] = relationship(back_populates="issues")
