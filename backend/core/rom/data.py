from pydantic import PrivateAttr

from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.schemas import NESPaletteData, NESScene


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
    """

    _name: str = PrivateAttr()
    _palette_data: NESPaletteData = PrivateAttr()

    def __init__(self, _name: str, _palette_data: NESPaletteData):
        super().__init__()
        self._name = _name
        self._palette_data = _palette_data

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.DATA

    @property
    def name(self) -> str:
        return f"palette_data__{self._name}"

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
        dependencies = []
        if (bp := self._scene.background_palettes) is not None:
            dependencies.append(bp)
        if (sp := self._scene.sprite_palettes) is not None:
            dependencies.append(sp)
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
        bg_pal_addr = 0 if not scene_data.background_palettes else names.get(scene_data.background_palettes, 0)
        code.extend(bg_pal_addr.to_bytes(2, "little"))

        # Sprite palettes address
        sprite_pal_addr = 0 if not scene_data.sprite_palettes else names.get(scene_data.sprite_palettes, 0)
        code.extend(sprite_pal_addr.to_bytes(2, "little"))

        return RenderedCodeBlock(code=bytes(code), exported_names={self.name: start_offset})
