import uuid

from api.games.assets.models import Asset
from core.rom.code_block import CodeBlock
from core.rom.data import PaletteData, SpriteSetCHRData
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


def _asset_to_code_blocks(asset: Asset) -> list[CodeBlock]:
    """Convert an asset to code blocks (data blocks)."""
    if asset.type == AssetType.PALETTE:
        return [PaletteData(_component_id=str(asset.id), _palette_data=asset.data, _is_asset=True)]
    elif asset.type == AssetType.SPRITE_SET:
        return [SpriteSetCHRData(_asset_id=str(asset.id), _name=asset.name, _sprite_set_data=asset.data)]
    else:
        raise ValueError(f"Unsupported asset type: {asset.type}")


class CodeBlockRegistry:
    def add_assets(self, assets: list[Asset]):
        """Add game assets to the registry as data blocks."""
        for asset in assets:
            code_blocks = _asset_to_code_blocks(asset)
            self._code_blocks_by_asset_id[asset.id] = code_blocks
            for code_block in code_blocks:
                self.add_code_block(code_block)

    def add_code_block(self, code_block: CodeBlock):
        self._code_blocks_by_name[code_block.name] = code_block

    def get_asset_code_blocks(self, asset: Asset) -> list[CodeBlock]:
        return self._code_blocks_by_asset_id.get(asset.id, [])

    def get_asset_code_block_names(self, asset_id: uuid.UUID) -> list[str]:
        """Get code block names for an asset by its ID."""
        code_blocks = self._code_blocks_by_asset_id.get(asset_id, [])
        return [block.name for block in code_blocks]

    def __init__(self):
        self._code_blocks_by_asset_id: dict[uuid.UUID, list[CodeBlock]] = {}
        self._code_blocks_by_name = DEFAULT_REGISTRY.copy()

    def __contains__(self, name: str) -> bool:
        return name in self._code_blocks_by_name

    def __getitem__(self, name: str) -> CodeBlock:
        if name not in self._code_blocks_by_name:
            raise KeyError(f"Code block '{name}' not found in registry.")
        return self._code_blocks_by_name[name]


def get_new_registry() -> CodeBlockRegistry:
    return CodeBlockRegistry()
