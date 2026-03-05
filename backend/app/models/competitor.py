import uuid

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048))
    estimated_traffic: Mapped[int | None] = mapped_column(Integer)
    domain_authority: Mapped[int | None] = mapped_column(Integer)
    top_keywords: Mapped[dict | None] = mapped_column(JSONB)
    strengths: Mapped[dict | None] = mapped_column(JSONB)
    weaknesses: Mapped[dict | None] = mapped_column(JSONB)

    report: Mapped["Report"] = relationship(back_populates="competitors")


class KeywordGap(Base):
    __tablename__ = "keyword_gaps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(500), nullable=False)
    target_rank: Mapped[int | None] = mapped_column(Integer)
    competitor_ranks: Mapped[dict | None] = mapped_column(JSONB)

    report: Mapped["Report"] = relationship(back_populates="keyword_gaps")
