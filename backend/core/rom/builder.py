from dataclasses import dataclass
import uuid
from core.rom.code_block import CodeBlock
from core.rom.data import SceneData
from core.rom.preamble import PreambleCodeBlock
from core.rom.rom import Rom
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource
from dependencies import get_db
from fastapi import Depends
from game.models import Game
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

REGISTRY = {
    # Zero page
    "zp_src": ZeroPageSource(),

    # Preambles
    "preamble": PreambleCodeBlock(),

    # Subroutines
    "load_scene": LoadSceneSubroutine(),
}

@dataclass
class RomBuilder:
    db: AsyncSession

    async def build(self, game_id: uuid.UUID, initial_scene_name: str = "main") -> bytes:
        game = await self.db.get(Game, game_id, options=[
            selectinload(Game.scenes)
        ])

        # For now, assume the first scene is the main scene
        if not game or len(game.scenes) == 0:
            raise ValueError("Game has no scenes")
        main_scenes = [scene for scene in game.scenes if scene.name == initial_scene_name]
        if len(main_scenes) != 1:
            raise ValueError(f"Game must have a scene named '{initial_scene_name}' (found {len(main_scenes)})")
        main_scene = main_scenes[0]

        rom = Rom()
        scene_block = SceneData(_scene=main_scene)
        self._add(rom, scene_block)

        # Placeholder implementation for building a ROM
        return b"ROM data for game " + str(game_id).encode()
    
    def _add(self, rom: Rom, code_block: CodeBlock):
        """
        First add all dependencies, recursively depth-first. Then add the code block itself.
        Adding a code block idempotently does nothing if it is already present.
        """
        for dependency_name in code_block.dependencies:
            if dependency_name not in REGISTRY:
                raise ValueError(f"Unknown dependency: {dependency_name}")
            dependency = REGISTRY[dependency_name]
            self._add(rom, dependency)
        rom.add(code_block)

def get_rom_builder(db: AsyncSession = Depends(get_db)) -> RomBuilder:
    return RomBuilder(db=db)
    