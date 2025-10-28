"""add_compiled_assets_table

Revision ID: 17331b8d005f
Revises: f6d0a8cccb2b
Create Date: 2025-10-28 11:44:08.456842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.pydantic_type import PydanticType
from core.schemas import CompiledAssetData


# revision identifiers, used by Alembic.
revision: str = '17331b8d005f'
down_revision: Union[str, Sequence[str], None] = 'f6d0a8cccb2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('compiled_assets',
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('PALETTE', name='compiledassettype'), nullable=False),
        sa.Column('data', PydanticType(CompiledAssetData), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], name='fk_compiled_assets_game_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'name', 'type', name='uq_compiled_asset_game_name_type')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('compiled_assets')
    op.execute('DROP TYPE compiledassettype')
