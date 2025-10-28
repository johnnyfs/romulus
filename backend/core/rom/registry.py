import uuid

from core.rom.code_block import CodeBlock
from core.rom.data import PaletteData
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource1, ZeroPageSource2
from core.schemas import ComponentType, AssetType
from api.games.components.models import Component
from api.games.assets.models import Asset

DEFAULT_REGISTRY = {
    # Zero page
    "zp__src1": ZeroPageSource1(),
    "zp__src2": ZeroPageSource2(),
    # Subroutines
    "load_scene": LoadSceneSubroutine(),
}


def _to_code_blocks(component: Component) -> list[CodeBlock]:
    if component.component_data.type == ComponentType.PALETTE:
        return [PaletteData(_component_id=str(component.id), _palette_data=component.component_data)]
    else:
        raise ValueError(f"Unsupported component type: {component.component_data.type}")


def _asset_to_code_blocks(asset: Asset) -> list[CodeBlock]:
    """Convert an asset to code blocks (data blocks)."""
    if asset.type == AssetType.PALETTE:
        return [PaletteData(_component_id=str(asset.id), _palette_data=asset.data, _is_asset=True)]
    else:
        raise ValueError(f"Unsupported asset type: {asset.type}")


class CodeBlockRegistry:
    def add_components(self, components: list[Component]):
        for component in components:
            code_blocks = _to_code_blocks(component)
            self._code_blocks_by_component_id[component.id] = code_blocks
            for code_block in code_blocks:
                self.add_code_block(code_block)

    def add_assets(self, assets: list[Asset]):
        """Add game assets to the registry as data blocks."""
        for asset in assets:
            code_blocks = _asset_to_code_blocks(asset)
            self._code_blocks_by_asset_id[asset.id] = code_blocks
            for code_block in code_blocks:
                self.add_code_block(code_block)

    def add_code_block(self, code_block: CodeBlock):
        self._code_blocks_by_name[code_block.name] = code_block

    def get_code_blocks(self, component: Component) -> list[CodeBlock]:
        return self._code_blocks_by_component_id.get(component.id, [])

    def get_asset_code_blocks(self, asset: Asset) -> list[CodeBlock]:
        return self._code_blocks_by_asset_id.get(asset.id, [])

    def __init__(self):
        self._code_blocks_by_component_id: dict[uuid.UUID, list[CodeBlock]] = {}
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
