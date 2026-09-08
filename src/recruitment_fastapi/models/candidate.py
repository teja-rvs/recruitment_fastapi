from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from recruitment_fastapi.database import Base


class Candidate(Base):
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

    type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "candidate"
    }
