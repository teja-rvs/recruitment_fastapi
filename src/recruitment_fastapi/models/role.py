from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from recruitment_fastapi.database import Base
from recruitment_fastapi.models.role_permissions import role_permissions
from recruitment_fastapi.models.user_role import user_roles


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[String] = mapped_column(String(255), nullable=False, unique=True)
    key: Mapped[String] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )

    users: Mapped[list["User"]] = relationship(  # noqa: F821, UP037 # type: ignore
        secondary=user_roles, back_populates="roles"
    )

    permissions: Mapped[list["Permission"]] = relationship(  # noqa: F821, UP037 # type: ignore
        "Permission", secondary=role_permissions, back_populates="roles"
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
