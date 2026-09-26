from abc import abstractmethod
from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from recruitment_fastapi.database import Base
from recruitment_fastapi.states.base_machine import BaseMachine
from recruitment_fastapi.states.recruitment_step_status import (
    RecruitmentStepStatusMachine,
)


class RecruitmentStep(Base, BaseMachine):
    __tablename__ = "recruitment_steps"

    STEP_TYPE: ClassVar = "recruitment_step"

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    __mapper_args__: ClassVar = {
        "polymorphic_on": "type",
        "polymorphic_identity": STEP_TYPE,
    }

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"), nullable=False
    )
    candidate: Mapped["Candidate"] = relationship(back_populates="recruitment_steps")  # type: ignore # noqa: F821, UP037

    interviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    interviewer: Mapped["User | None"] = relationship()  # type: ignore # noqa: F821, UP037

    interview_date: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    status: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = RecruitmentStepStatusMachine.initial_state.id

    @property
    def status_machine(self) -> RecruitmentStepStatusMachine:
        if not hasattr(self, "_status_machine"):
            self._status_machine = RecruitmentStepStatusMachine(
                model=self, state_field="status"
            )

        return self._status_machine

    @classmethod
    @abstractmethod
    def allowed_roles(cls) -> list[str]:
        pass

    def start(self):
        self.status_machine.start()

    def schedule_interview(self):
        self.status_machine.schedule_interview()

    def interview_complete(self):
        self.status_machine.interview_complete()

    def approve(self):
        self.status_machine.approve()

    def reject(self):
        self.status_machine.reject()

    def cancel(self):
        self.status_machine.cancel()
