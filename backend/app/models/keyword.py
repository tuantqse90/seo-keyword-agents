import uuid

from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(500), nullable=False)
    cluster: Mapped[str | None] = mapped_column(String(255))
    search_volume: Mapped[int | None] = mapped_column(Integer)
    keyword_difficulty: Mapped[int | None] = mapped_column(Integer)
    search_intent: Mapped[str | None] = mapped_column(String(50))
    cpc: Mapped[float | None] = mapped_column(Float)
    opportunity_score: Mapped[int | None] = mapped_column(Integer)
    is_golden: Mapped[bool] = mapped_column(Boolean, default=False)

    report: Mapped["Report"] = relationship(back_populates="keywords")
