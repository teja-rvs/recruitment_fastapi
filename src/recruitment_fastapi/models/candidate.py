from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from recruitment_fastapi.database import Base
from recruitment_fastapi.states.base_machine import BaseMachine
from recruitment_fastapi.states.candidate_status import CandidateStatusMachine


class Candidate(Base, BaseMachine):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    phone: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    experience: Mapped[int] = mapped_column(Integer, nullable=False)

    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    __mapper_args__: ClassVar = {
        "polymorphic_on": "type",
        "polymorphic_identity": "candidate",
    }

    recruitment_steps: Mapped[list["RecruitmentStep"]] = relationship(  # noqa: F821, UP037 # type: ignore
        back_populates="candidate"
    )

    status: Mapped[String] = mapped_column(
        String(255),
        nullable=False,
        index=True,
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

    RECRUITMENT_STEPS: ClassVar = []
    STAGES: ClassVar = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = CandidateStatusMachine.initial_state.value

    @property
    def status_machine(self) -> CandidateStatusMachine:
        if not hasattr(self, "_status_machine"):
            self._status_machine = CandidateStatusMachine(
                model=self, state_field="status"
            )
        return self._status_machine

    def recruit(self):
        self.status_machine.recruit()

    def reject(self):
        self.status_machine.reject()
