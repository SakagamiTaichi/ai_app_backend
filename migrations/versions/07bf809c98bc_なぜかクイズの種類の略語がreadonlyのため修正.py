"""なぜかクイズの種類の略語がReadOnlyのため修正

Revision ID: 07bf809c98bc
Revises: 95c1f6721233
Create Date: 2025-07-20 01:14:05.009830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07bf809c98bc'
down_revision: Union[str, None] = '95c1f6721233'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
