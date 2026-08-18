"""Create initial tables

Revision ID: 033f9866e739
Revises: a52c35b193e4
Create Date: 2026-08-18 19:26:43.619028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '033f9866e739'
down_revision: Union[str, Sequence[str], None] = 'a52c35b193e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
