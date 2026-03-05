import uuid

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentBrief(Base):
    __tablename__ = "content_briefs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    title_tag: Mapped[str | None] = mapped_column(String(255))
    meta_description: Mapped[str | None] = mapped_column(String(500))
    target_word_count: Mapped[int | None] = mapped_column(Integer)
    outline: Mapped[dict | None] = mapped_column(JSONB)
    lsi_keywords: Mapped[dict | None] = mapped_column(JSONB)
    snippet_strategy: Mapped[str | None] = mapped_column(Text)
    eeat_signals: Mapped[dict | None] = mapped_column(JSONB)

    report: Mapped["Report"] = relationship(back_populates="content_briefs")
