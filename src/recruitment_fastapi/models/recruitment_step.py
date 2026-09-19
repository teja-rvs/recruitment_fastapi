from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from recruitment_fastapi.database import Base


class RecruitmentStep(Base):
    __tablename__ = "recruitment_steps"

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    __mapper_args__: ClassVar = {
        "polymorphic_on": "type",
        "polymorphic_identity": "recruitment_step",
    }

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False
    )
    candidate: Mapped["Candidate"] = relationship(back_populates="recruitment_steps")  # type: ignore # noqa: F821, UP037

    interview_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
