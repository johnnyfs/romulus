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
        import logging
        logger = logging.getLogger(__name__)

        code = bytearray()
        for palette in self._palette_data.palettes:
            for color in palette.colors:
                code.append(color.index)

        logger.info(f"Palette '{self._name}' rendering at ROM offset ${start_offset:04X}")
        logger.info(f"Palette '{self._name}' data: {code.hex()} ({len(code)} bytes)")
        logger.info(f"Palette '{self._name}' exporting as '{self.name}'")
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
            dependencies.append(f"palette_data__{bp}")
        if (sp := self._scene.sprite_palettes) is not None:
            dependencies.append(f"palette_data__{sp}")
        return dependencies

    @property
    def size(self) -> int:
        """Scene is 1 byte for background color + 4 bytes for the palette addresses (which must still be present if null.)"""
        return 1 + 2 + 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        import logging
        logger = logging.getLogger(__name__)

        scene_data = self._scene
        code = bytearray()

        # Background color
        code.append(scene_data.background_color.index)
        logger.info(f"Scene '{self._name}' render: BG color = ${scene_data.background_color.index:02X}")

        # Background palettes address
        # Look up the exported palette_data name, not the raw palette name
        bg_pal_name = f"palette_data__{scene_data.background_palettes}" if scene_data.background_palettes else None
        bg_pal_addr = 0 if not bg_pal_name else names.get(bg_pal_name, 0)
        logger.info(f"Scene '{self._name}' render: Looking for BG palette '{bg_pal_name}'")
        logger.info(f"Scene '{self._name}' render: BG palette address = ${bg_pal_addr:04X}")
        logger.info(f"Scene '{self._name}' render: Available names in registry: {list(names.keys())}")
        code.extend(bg_pal_addr.to_bytes(2, "little"))

        # Sprite palettes address
        # Look up the exported palette_data name, not the raw palette name
        sprite_pal_name = f"palette_data__{scene_data.sprite_palettes}" if scene_data.sprite_palettes else None
        sprite_pal_addr = 0 if not sprite_pal_name else names.get(sprite_pal_name, 0)
        logger.info(f"Scene '{self._name}' render: Sprite palette address = ${sprite_pal_addr:04X}")
        code.extend(sprite_pal_addr.to_bytes(2, "little"))

        logger.info(f"Scene '{self._name}' render: Final scene data bytes = {code.hex()}")
        return RenderedCodeBlock(code=bytes(code), exported_names={self.name: start_offset})
