from dataclasses import dataclass
import uuid
from core.rom.code_block import CodeBlock
from core.rom.data import SceneData
from core.rom.preamble import PreambleCodeBlock
from core.rom.rom import Rom
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource1, ZeroPageSource2
from dependencies import get_db
from fastapi import Depends
from game.models import Game
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


@dataclass
class RomBuilder:
    db: AsyncSession
    registry = {
        # Zero page
        "zp__src1": ZeroPageSource1(),
        "zp__src2": ZeroPageSource2(),

        # Subroutines
        "load_scene": LoadSceneSubroutine(),
    }

    async def build(self, game_id: uuid.UUID, initial_scene_name: str = "main") -> bytes:
        game = await self.db.get(Game, game_id, options=[
            selectinload(Game.scenes)
        ])

        if game is None or not game.scenes:
            raise ValueError(f"Game with ID {game_id} not found or has no scenes.")

        rom = Rom()

        saw_main = False
        for scene in game.scenes:
            saw_main = saw_main or (scene.name == initial_scene_name)
            scene_block = SceneData(_scene=scene)
            self._add(rom, scene_block)

        preamble = PreambleCodeBlock(_main_scene_name=initial_scene_name)
        self._add(rom, preamble)
        
        if not saw_main:
            raise ValueError(f"Game must have a scene named '{initial_scene_name}'.")       

        return rom.render()
    
    def _add(self, rom: Rom, code_block: CodeBlock):
        """
        First add all dependencies, recursively depth-first. Then add the code block itself.
        Adding a code block idempotently does nothing if it is already present.
        """
        for dependency_name in code_block.dependencies:
            if dependency_name not in self.registry:
                raise ValueError(f"Unknown dependency: {dependency_name}")
            dependency = self.registry[dependency_name]
            self._add(rom, dependency)
        rom.add(code_block)
        self.registry[code_block.name] = code_block

def get_rom_builder(db: AsyncSession = Depends(get_db)) -> RomBuilder:
    return RomBuilder(db=db)
    