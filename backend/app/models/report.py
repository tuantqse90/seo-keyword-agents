import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportModule(str, enum.Enum):
    KEYWORDS = "keywords"
    COMPETITOR = "competitor"
    CONTENT = "content"
    AUDIT = "audit"
    FULL = "full"
    STRATEGY = "strategy"
    FIX = "fix"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    module: Mapped[ReportModule] = mapped_column(SAEnum(ReportModule), nullable=False)
    input_query: Mapped[str] = mapped_column(String(2048), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(SAEnum(ReportStatus), default=ReportStatus.PENDING)
    raw_markdown: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project | None"] = relationship(back_populates="reports")
    keywords: Mapped[list["Keyword"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    competitors: Mapped[list["Competitor"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    keyword_gaps: Mapped[list["KeywordGap"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    content_briefs: Mapped[list["ContentBrief"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    audit_results: Mapped[list["AuditResult"]] = relationship(back_populates="report", cascade="all, delete-orphan")
