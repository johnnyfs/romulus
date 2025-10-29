"""add_sprite_set_to_assettype_enum

Revision ID: 5e33375f7d87
Revises: 2cdc53e397ad
Create Date: 2025-10-28 21:46:06.618240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e33375f7d87'
down_revision: Union[str, Sequence[str], None] = '2cdc53e397ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add SPRITE_SET to the assettype enum
    op.execute("ALTER TYPE assettype ADD VALUE 'SPRITE_SET'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL doesn't support removing enum values directly
    # Would require recreating the enum and updating all references
    pass
