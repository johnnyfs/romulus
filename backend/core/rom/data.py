from pydantic import PrivateAttr

from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.schemas import NESEntity, NESPaletteData, NESScene


class AddressData(CodeBlock):
    """
    A word (2-byte) data code block.

    - used to store 2-byte values
    """

    _name: str = PrivateAttr()
    _referenced_value_name: str = PrivateAttr()

    def __init__(self, _name: str, _referenced_value_name: str):
        super().__init__()
        self._name = _name
        self._referenced_value_name = _referenced_value_name

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.DATA

    @property
    def name(self) -> str:
        return f"data__{self._name}"

    @property
    def dependencies(self) -> list[str]:
        return [self._referenced_value_name]

    @property
    def size(self) -> int:
        return 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        if self._referenced_value_name not in names:
            raise ValueError(f"Referenced value name '{self._referenced_value_name}' not found in names.")
        value = names[self._referenced_value_name]
        code = value.to_bytes(2, "little")
        return RenderedCodeBlock(code=code, exported_names={self.name: start_offset})


class PaletteData(CodeBlock):
    """
    A palette data code block.

    - contains NES palette data
    - can be from a component (legacy) or an asset
    """

    _id: str = PrivateAttr()  # UUID as string
    _palette_data: NESPaletteData = PrivateAttr()
    _is_asset: bool = PrivateAttr()  # True if this is an asset, False if component

    def __init__(self, _component_id: str, _palette_data: NESPaletteData, _is_asset: bool = False):
        super().__init__()
        self._id = _component_id  # Keep param name for backward compatibility
        self._palette_data = _palette_data
        self._is_asset = _is_asset

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.DATA

    @property
    def name(self) -> str:
        # TODO: Standardize all names to {component|asset}__{type}__{id} format
        # for better type safety and clearer error messages
        if self._is_asset:
            return f"asset__palette__{self._id}"
        else:
            return f"component__{self._id}"

    @property
    def dependencies(self) -> list[str]:
        return []

    @property
    def size(self) -> int:
        # Each palette has 3 colors, each color is 1 byte
        return len(self._palette_data.palettes) * 3

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = bytearray()
        for palette in self._palette_data.palettes:
            for color in palette.colors:
                code.append(color.index)

        return RenderedCodeBlock(code=bytes(code), exported_names={self.name: start_offset})


class SceneData(CodeBlock):
    """
    A scene data code block.

    - contains the data for a scene
    """

    _name: str = PrivateAttr()
    _scene: NESScene = PrivateAttr()

    def __init__(self, _name: str, _scene: NESScene):
        super().__init__()
        self._name = _name
        self._scene = _scene

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.DATA

    @property
    def name(self) -> str:
        return f"scene_data__{self._name}"

    @property
    def dependencies(self) -> list[str]:
        # TODO: Once we fully migrate to assets, we should add type info to NESScene
        # to distinguish between component and asset references. For now, we try both
        # naming conventions: asset__palette__{id} first (new), then component__{id} (legacy)
        dependencies = []
        if (bp := self._scene.background_palettes) is not None:
            # Try asset naming first, will fall back to component if not found
            dependencies.append(f"asset__palette__{bp}")
        if (sp := self._scene.sprite_palettes) is not None:
            dependencies.append(f"asset__palette__{sp}")
        return dependencies

    @property
    def size(self) -> int:
        """Scene is 1 byte for background color + 4 bytes for the palette addresses (which must still be present if null.)"""
        return 1 + 2 + 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        scene_data = self._scene
        code = bytearray()

        # Background color
        code.append(scene_data.background_color.index)

        # Background palettes address
        # Try asset naming first, fall back to component naming (legacy)
        bg_pal_addr = 0
        if scene_data.background_palettes:
            asset_name = f"asset__palette__{scene_data.background_palettes}"
            component_name = f"component__{scene_data.background_palettes}"
            bg_pal_addr = names.get(asset_name, names.get(component_name, 0))
        code.extend(bg_pal_addr.to_bytes(2, "little"))

        # Sprite palettes address
        # Try asset naming first, fall back to component naming (legacy)
        sprite_pal_addr = 0
        if scene_data.sprite_palettes:
            asset_name = f"asset__palette__{scene_data.sprite_palettes}"
            component_name = f"component__{scene_data.sprite_palettes}"
            sprite_pal_addr = names.get(asset_name, names.get(component_name, 0))
        code.extend(sprite_pal_addr.to_bytes(2, "little"))

        return RenderedCodeBlock(code=bytes(code), exported_names={self.name: start_offset})


class EntityData(CodeBlock):
    """
    An entity data code block.

    - contains entity position data (x, y)
    """

    _name: str = PrivateAttr()
    _entity: NESEntity = PrivateAttr()

    def __init__(self, _name: str, _entity: NESEntity):
        super().__init__()
        self._name = _name
        self._entity = _entity

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.DATA

    @property
    def name(self) -> str:
        return f"entity_data__{self._name}"

    @property
    def dependencies(self) -> list[str]:
        return []

    @property
    def size(self) -> int:
        """Entity is 2 bytes: x position + y position."""
        return 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        entity_data = self._entity
        code = bytearray()

        # X position (byte)
        code.append(entity_data.x & 0xFF)

        # Y position (byte)
        code.append(entity_data.y & 0xFF)

        return RenderedCodeBlock(code=bytes(code), exported_names={self.name: start_offset})
