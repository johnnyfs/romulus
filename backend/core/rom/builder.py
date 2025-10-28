import logging
import uuid
from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.rom.code_block import CodeBlock
from core.rom.data import SceneData
from core.rom.preamble import PreambleCodeBlock
from core.rom.registry import CodeBlockRegistry, get_new_registry
from core.rom.rom import Rom, get_empty_rom
from dependencies import get_db
from api.games.models import Game

logger = logging.getLogger(__name__)


@dataclass
class RomBuilder:
    db: AsyncSession
    rom: Rom
    registry: CodeBlockRegistry

    async def build(self, game_id: uuid.UUID, initial_scene_name: str = "main") -> bytes:
        game = await self.db.get(Game, game_id, options=[selectinload(Game.scenes), selectinload(Game.components)])

        if game is None or not game.scenes:
            raise ValueError(f"Game with ID {game_id} not found or has no scenes.")

        rom = Rom()

        # Pre-populate the registry with all code blocks yielded by the components.
        # This is to avoid the need to sort components by dependency order beforehand.
        self.registry.add_components(game.components)

        # Debug logging for components
        logger.info(f"Building ROM for game {game.name} (ID: {game_id})")
        logger.info(f"Found {len(game.components)} components:")
        for component in game.components:
            logger.info(f"  - Component '{component.name}' (type: {component.type})")
            if component.component_data.type == "palette":
                logger.info(f"    Palette data ({len(component.component_data.palettes)} sub-palettes):")
                for i, palette in enumerate(component.component_data.palettes):
                    colors = [f"${c.index:02X}" for c in palette.colors]
                    logger.info(f"      Palette {i}: {', '.join(colors)}")

        saw_main = False
        for scene in game.scenes:
            saw_main = saw_main or (scene.name == initial_scene_name)

            # Debug logging for scenes
            logger.info(f"Adding scene '{scene.name}':")
            logger.info(f"  Background color: ${scene.scene_data.background_color.index:02X}")
            logger.info(f"  Background palettes: {scene.scene_data.background_palettes or 'None'}")
            logger.info(f"  Sprite palettes: {scene.scene_data.sprite_palettes or 'None'}")

            scene_block = SceneData(_name=scene.name, _scene=scene.scene_data)
            self._add(rom, scene_block)

        if not saw_main:
            raise ValueError(f"Game must have a scene named '{initial_scene_name}'.")

        preamble = PreambleCodeBlock(_main_scene_name=initial_scene_name)
        self._add(rom, preamble)

        for component in game.components:
            for code_block in self.registry.get_code_blocks(component):
                logger.info(f"Adding code block: {code_block.name} (size: {code_block.size} bytes)")
                self._add(rom, code_block)

        rom_bytes = rom.render()
        logger.info(f"ROM build complete: {len(rom_bytes)} bytes")
        return rom_bytes

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
