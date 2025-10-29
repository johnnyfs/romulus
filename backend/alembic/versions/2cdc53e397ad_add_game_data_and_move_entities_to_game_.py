"""add_game_data_and_move_entities_to_game_level

Revision ID: 2cdc53e397ad
Revises: 17331b8d005f
Create Date: 2025-10-28 19:41:19.043443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.pydantic_type import PydanticType
from core.schemas import GameData, NESEntity


# revision identifiers, used by Alembic.
revision: str = '2cdc53e397ad'
down_revision: Union[str, Sequence[str], None] = '17331b8d005f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add game_data column to games table with a default NES game config
    op.add_column('games', sa.Column('game_data', PydanticType(GameData), nullable=False,
                                     server_default='{"type": "nes", "sprite_size": "8x8"}'))

    # Drop old entities table (with scene_id foreign key)
    op.drop_table('entities')

    # Recreate entities table with game_id foreign key
    op.create_table('entities',
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('entity_data', PydanticType(NESEntity), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'name', name='uq_entity_game_name')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new entities table (with game_id)
    op.drop_table('entities')

    # Recreate old entities table (with scene_id)
    op.create_table('entities',
        sa.Column('scene_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('entity_data', PydanticType(NESEntity), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scene_id', 'name', name='uq_entity_scene_name')
    )

    # Remove game_data column from games table
    op.drop_column('games', 'game_data')
