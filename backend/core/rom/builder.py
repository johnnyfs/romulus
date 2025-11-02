import logging
import uuid
from dataclasses import dataclass

from api.games.assets.models import Asset
from core.rom.label_registry import LabelRegistry
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.games.models import Game
from api.games.scenes.models import Scene
from core.rom.code_block import CodeBlock
from core.rom.data import EntityData, SceneData
from core.rom.preamble import PreambleCodeBlock
from core.rom.code_block_registry import CodeBlockRegistry
from core.rom.rom import Rom, get_empty_rom
from dependencies import get_db

logger = logging.getLogger(__name__)

@dataclass
class RomBuilder:
    """
    The rom builder is the bridge between the db model and the rom model.

    The db model consists of named games, scenes, assets, entities, and components that refer
    to each other via foreign key uuids.

    The rom model consists of a dependency graph of code blocks that refer to each other via labels.

    The builder
    - populates a label registry (uuid -> label)
    - populates a code block registry (*root* label -> code block) (which depends on the label registry)
    - populates the rom by adding code blocks and their dependencies in recursive depth-first order
    - invokes the rom to render the final binary
    """

    db: AsyncSession
    rom: Rom
    label_registry: LabelRegistry
    code_block_registry: CodeBlockRegistry

    async def build(self, game_id: uuid.UUID, initial_scene_name: str = "main") -> bytes:
        game = await self.db.get(
            Game,
            game_id,
            options=[
                selectinload(Game.scenes),
                selectinload(Game.assets),
                selectinload(Game.entities),
            ],
        )

        if game is None or not game.scenes:
            raise ValueError(f"Game with ID {game_id} not found or has no scenes.")

        # Pre-populate the registries
        self.label_registry.add_game(game)
        self.code_block_registry.add_game(game)

        # Add all the scenes and their dependencies. (The sum of their referenced objects
        # is the sum of the game.)
        main_label = None
        for scene in game.scenes:
            scene_label = self.label_registry.get_scene_label(scene.id)
            print(f"Adding scene '{scene.name}' with label '{scene_label}' to ROM.")
            if scene.name == initial_scene_name:
                print(f"  -> This is the initial scene.")
                main_label = scene_label
            scene_block = SceneData.from_model(scene=scene, registry=self.label_registry)
            self._add(self.rom, scene_block)

        if main_label is None:
            raise ValueError(f"Game must have a scene named '{initial_scene_name}'.")

        preamble = PreambleCodeBlock(main_scene_label=main_label)
        self._add(self.rom, preamble)

        # Asset code blocks are added automatically via dependencies
        # (e.g., sprite sets are added when entities reference them)
        # No need to add them unconditionally here

        return self.rom.render()

    def _add(self, rom: Rom, code_block: CodeBlock):
        """
        First add all dependencies, recursively depth-first. Then add the code block itself.
        Adding a code block idempotently does nothing if it is already present.
        """
        for dependency_name in code_block.dependencies:
            dependency = self.code_block_registry[dependency_name]
            self._add(rom, dependency)
        rom.add(code_block)
        self.code_block_registry.add_code_block(code_block)


def get_rom_builder(
    db: AsyncSession = Depends(get_db),
) -> RomBuilder:
    label_registry = LabelRegistry()
    code_block_registry = CodeBlockRegistry(label_registry=label_registry)
    return RomBuilder(db=db, rom=Rom(), label_registry=label_registry, code_block_registry=code_block_registry)
