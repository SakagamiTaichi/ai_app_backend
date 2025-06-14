"""暗記テーブルの追加

Revision ID: 5c234e732787
Revises: 6cf8d3d05f1f
Create Date: 2025-06-14 10:51:56.594754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c234e732787'
down_revision: Union[str, None] = '6cf8d3d05f1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
