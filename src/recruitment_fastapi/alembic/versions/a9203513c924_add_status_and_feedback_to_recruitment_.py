"""add status and feedback to recruitment steps

Revision ID: a9203513c924
Revises: 08df0d4ca88b
Create Date: 2026-09-20 16:01:49.511873

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a9203513c924"
down_revision: Union[str, Sequence[str], None] = "08df0d4ca88b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "recruitment_steps",
        sa.Column(
            "status",
            sa.String(length=255),
            nullable=False,
            server_default="initialized",
        ),
    )
    op.add_column("recruitment_steps", sa.Column("feedback", sa.Text(), nullable=True))
    op.create_index(
        op.f("ix_recruitment_steps_status"),
        "recruitment_steps",
        ["status"],
        unique=False,
    )
    op.alter_column("recruitment_steps", "status", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_recruitment_steps_status"), table_name="recruitment_steps")
    op.drop_column("recruitment_steps", "feedback")
    op.drop_column("recruitment_steps", "status")
