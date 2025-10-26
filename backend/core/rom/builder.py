from dataclasses import dataclass
import uuid
from dependencies import get_db
from fastapi import Depends
from game.models import Game
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

@dataclass
class RomBuilder:
    db: AsyncSession

    async def build(self, game_id: uuid.UUID) -> bytes:
        # Preload the scenes
        game = await self.db.get(Game, game_id, options=[
            selectinload(Game.scenes)
        ])
        # For now, assume the first scene is the main scene
        if not game or len(game.scenes) == 0:
            raise ValueError("Game has no scenes")
        main_scene = game.scenes[0] if game.scenes else None

        # Placeholder implementation for building a ROM
        return b"ROM data for game " + str(game_id).encode()

def get_rom_builder(db: AsyncSession = Depends(get_db)) -> RomBuilder:
    return RomBuilder(db=db)
    