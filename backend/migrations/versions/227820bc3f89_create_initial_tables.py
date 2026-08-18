"""Create initial tables

Revision ID: 227820bc3f89
Revises: 033f9866e739
Create Date: 2026-08-18 19:29:11.066497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '227820bc3f89'
down_revision: Union[str, Sequence[str], None] = '033f9866e739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
