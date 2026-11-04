"""add email check

Revision ID: 19c8922507b8
Revises: 1e3d47d6bd55
Create Date: 2026-10-28 10:20:32.607802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19c8922507b8'
down_revision: Union[str, Sequence[str], None] = '1e3d47d6bd55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
    "valid_email",
    "users",
    r"email ~* '^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$'",
)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("valid_email", "users")
