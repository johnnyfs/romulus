import logging
import uuid
from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.games.models import Game
from api.games.scenes.models import Scene
from core.rom.code_block import CodeBlock
from core.rom.data import EntityData, SceneData
from core.rom.preamble import PreambleCodeBlock
from core.rom.registry import CodeBlockRegistry, get_new_registry
from core.rom.rom import Rom, get_empty_rom
from dependencies import get_db

logger = logging.getLogger(__name__)


@dataclass
class RomBuilder:
    db: AsyncSession
    rom: Rom
    registry: CodeBlockRegistry

    async def build(self, game_id: uuid.UUID, initial_scene_name: str = "main") -> bytes:
        game = await self.db.get(
            Game,
            game_id,
            options=[
                selectinload(Game.scenes).selectinload(Scene.entities),
                selectinload(Game.assets),
            ],
        )

        if game is None or not game.scenes:
            raise ValueError(f"Game with ID {game_id} not found or has no scenes.")

        rom = Rom()

        # Pre-populate the registry with all code blocks yielded by assets.
        # This is to avoid the need to sort by dependency order beforehand.
        self.registry.add_assets(game.assets)

        saw_main = False
        for scene in game.scenes:
            saw_main = saw_main or (scene.name == initial_scene_name)
            scene_block = SceneData(_name=scene.name, _scene=scene.scene_data)
            self._add(rom, scene_block)

            # Add entities for this scene
            for entity in scene.entities:
                entity_block = EntityData(_name=entity.name, _entity=entity.entity_data)
                self._add(rom, entity_block)

        if not saw_main:
            raise ValueError(f"Game must have a scene named '{initial_scene_name}'.")

        preamble = PreambleCodeBlock(_main_scene_name=initial_scene_name)
        self._add(rom, preamble)

        for asset in game.assets:
            for code_block in self.registry.get_asset_code_blocks(asset):
                self._add(rom, code_block)

        return rom.render()

    def _add(self, rom: Rom, code_block: CodeBlock):
        """
        First add all dependencies, recursively depth-first. Then add the code block itself.
        Adding a code block idempotently does nothing if it is already present.
        """
        for dependency_name in code_block.dependencies:
            dependency = self.registry[dependency_name]
            self._add(rom, dependency)
        rom.add(code_block)
        self.registry.add_code_block(code_block)


def get_rom_builder(
    db: AsyncSession = Depends(get_db),
    rom: Rom = Depends(get_empty_rom),
    registry: CodeBlockRegistry = Depends(get_new_registry),
) -> RomBuilder:
    return RomBuilder(db=db, rom=rom, registry=registry)
