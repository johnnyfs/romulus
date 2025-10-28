"""add_game_assets_table

Revision ID: 17331b8d005f
Revises: f6d0a8cccb2b
Create Date: 2025-10-28 11:44:08.456842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.pydantic_type import PydanticType
from core.schemas import GameAssetData


# revision identifiers, used by Alembic.
revision: str = '17331b8d005f'
down_revision: Union[str, Sequence[str], None] = 'f6d0a8cccb2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('game_assets',
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('PALETTE', name='gameassettype'), nullable=False),
        sa.Column('data', PydanticType(GameAssetData), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], name='fk_game_assets_game_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'name', 'type', name='uq_game_asset_game_name_type')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('game_assets')
    op.execute('DROP TYPE gameassettype')
