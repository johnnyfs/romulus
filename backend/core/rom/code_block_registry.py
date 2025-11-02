from api.games.assets.models import Asset
from api.games.entities.models import Entity
from api.games.models import Game
from core.rom.code_block import CodeBlock, CodeBlockType
from core.rom.data import EntityData, PaletteData, SpriteSetCHRData
from core.rom.label_registry import LabelRegistry
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource1, ZeroPageSource2
from core.schemas import AssetType

DEFAULT_REGISTRY = {
    # Zero page
    "zp__src1": ZeroPageSource1(),
    "zp__src2": ZeroPageSource2(),
    # Subroutines
    "load_scene": LoadSceneSubroutine(),
}

class CodeBlockRegistry:
    def __init__(self, label_registry: LabelRegistry):
        self._label_registry = label_registry
        self._code_blocks_by_label: dict[str, CodeBlock] = {}

    def _asset_to_code_block(self, asset: Asset) -> CodeBlock:
        """Convert an asset to code blocks (data blocks)."""
        if asset.data.type == AssetType.PALETTE:
            return PaletteData.from_model(asset.id, asset.data, self._label_registry)
        elif asset.data.type == AssetType.SPRITE_SET:
            return SpriteSetCHRData.from_model(asset.id, asset.data, self._label_registry)
        else:
            raise ValueError(f"Unsupported asset type: {asset.type}")
        
    def _entity_to_code_block(self, entity: Entity) -> CodeBlock:
        """Convert an entity to code blocks."""
        # For now, entities do not yield any code blocks.
        return EntityData.from_model(entity=entity, registry=self._label_registry)

    def add_assets(self, assets: list[Asset]):
        """Add game assets to the registry as data blocks."""
        for asset in assets:
            code_block = self._asset_to_code_block(asset)
            self.add_code_block(code_block)
    
    def add_entities(self, entities: list[Entity]):
        """Add game entities to the registry as code blocks."""
        for entity in entities:
            code_block = self._entity_to_code_block(entity)
            self.add_code_block(code_block)
            for component in entity.components:
                # TODO: Add component code blocks if needed
                pass

    def add_game(self, game: Game):
        """Add all code blocks for a game's assets and entities."""
        self.add_assets(game.assets)
        self.add_entities(game.entities)

    def add_code_block(self, code_block: CodeBlock):
        self._code_blocks_by_label[code_block.label] = code_block

    def __contains__(self, label: str) -> bool:
        return label in self._code_blocks_by_label

    def __getitem__(self, label: str) -> CodeBlock:
        if label not in self._code_blocks_by_label:
            raise KeyError(f"Code block '{label}' not found in registry.")
        return self._code_blocks_by_label[label]
