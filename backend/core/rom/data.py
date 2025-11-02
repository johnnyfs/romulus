from typing import Self
import uuid
from api.games.entities.models import Entity
from api.games.scenes.models import Scene
from core.rom.label_registry import LabelRegistry

from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.schemas import NESColor, NESEntity, NESPaletteAssetData, NESSpriteSetAssetData, NESPaletteData


class AddressData(CodeBlock):
    """
    A word (2-byte) data code block.

    - used to store 2-byte values
    """
    referenced_value_name: str

    @classmethod
    def from_name(cls, name: str, referenced_value_name: str, registry: LabelRegistry) -> Self:
        return cls(
            label=f"data__{name}",
            type=CodeBlockType.DATA,
            referenced_value_name=referenced_value_name
        )

    @property
    def dependencies(self) -> list[str]:
        return [self.referenced_value_name]

    @property
    def size(self) -> int:
        return 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        if self.referenced_value_name not in names:
            raise ValueError(f"Referenced value name '{self.referenced_value_name}' not found in names.")
        value = names[self.referenced_value_name]
        code = value.to_bytes(2, "little")
        return RenderedCodeBlock(code=code, exported_labels={self.label: start_offset})


class PaletteData(CodeBlock):
    """
    A palette data code block.

    - contains NES palette data
    - can be from a component (legacy) or an asset
    """
    palette_data: NESPaletteAssetData

    @classmethod
    def from_model(cls, id: uuid.UUID, palette_data: NESPaletteAssetData, registry: LabelRegistry) -> Self:
        return cls(
            label=registry.get_asset_label(id),
            type=CodeBlockType.DATA,
            palette_data=palette_data
        )

    @property
    def dependencies(self) -> list[str]:
        return []

    @property
    def size(self) -> int:
        # Each palette has 3 colors, each color is 1 byte
        return len(self.palette_data.palettes) * 3

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = bytearray()
        for palette in self.palette_data.palettes:
            for color in palette.colors:
                code.append(color.index)

        return RenderedCodeBlock(code=bytes(code), exported_labels={self.label: start_offset})


class SceneData(CodeBlock):
    """
    A scene data code block.

    - contains the data for a scene
    """
    background_color: NESColor
    background_palette: str | None
    sprite_palette: str | None

    @classmethod
    def from_model(cls, scene: Scene, registry: LabelRegistry) -> Self:
        return cls(
            label=registry.get_scene_label(scene.id),
            type=CodeBlockType.DATA,
            background_color=scene.scene_data.background_color,
            background_palette=registry.get_asset_label(id) if (id := scene.scene_data.background_palettes) else None,
            sprite_palette=registry.get_asset_label(id) if (id := scene.scene_data.sprite_palettes) else None
        )

    @property
    def dependencies(self) -> list[str]:
        dependencies = []
        if (self.background_palette is not None):
            dependencies.append(self.background_palette)
        if (self.sprite_palette is not None):
            dependencies.append(self.sprite_palette)
        return dependencies

    @property
    def size(self) -> int:
        """Scene is 1 byte for background color + 4 bytes for the palette addresses (which must still be present if null.)"""
        return 1 + 2 + 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = bytearray()

        # Background color
        code.append(self.background_color.index)

        # Background palettes address
        # Try asset naming first, fall back to component naming (legacy)
        bg_pal_addr = 0
        if self.background_palette:
            bg_pal_addr = names.get(self.background_palette, 0)
        code.extend(bg_pal_addr.to_bytes(2, "little"))

        # Sprite palettes address
        # Try asset naming first, fall back to component naming (legacy)
        sprite_pal_addr = 0
        if self.sprite_palette:
            sprite_pal_addr = names.get(self.sprite_palette, 0)
        code.extend(sprite_pal_addr.to_bytes(2, "little"))

        return RenderedCodeBlock(code=bytes(code), exported_labels={self.label: start_offset})


class EntityData(CodeBlock):
    """
    An entity data code block.

    - contains entity position data (x, y)
    """
    entity_data: NESEntity
    component_labels: list[str]

    @classmethod
    def from_model(cls, entity: Entity, registry: LabelRegistry) -> Self:
        """Entity depends on components attached to it."""
        component_labels = []
        for component in entity.components:
            component_label = registry.get_component_label(component.id)
            component_labels.append(component_label)

        return cls(
            label=registry.get_entity_label(entity.id),
            type=CodeBlockType.DATA,
            entity_data=entity.entity_data,
            component_labels=component_labels
        )

    @property
    def dependencies(self) -> list[str]:
        return self.component_labels

    @property
    def size(self) -> int:
        """Entity is 2 bytes: x position + y position."""
        return 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = bytearray()

        # X position (byte)
        code.append(self.entity_data.x & 0xFF)

        # Y position (byte)
        code.append(self.entity_data.y & 0xFF)

        return RenderedCodeBlock(code=bytes(code), exported_labels={self.label: start_offset})


class SpriteSetCHRData(CodeBlock):
    """
    A CHR-ROM data block for sprite sets.

    - contains CHR tile data for sprites
    - exports a name that references the starting CHR index
    """
    sprite_set_data: NESSpriteSetAssetData

    @classmethod
    def from_model(cls, asset_id: uuid.UUID, sprite_set_data: NESSpriteSetAssetData, registry: LabelRegistry) -> Self:
        return cls(
            label=registry.get_asset_label(asset_id),
            type=CodeBlockType.CHR,
            sprite_set_data=sprite_set_data
        )

    @property
    def dependencies(self) -> list[str]:
        return []

    @property
    def size(self) -> int:
        # Return the size of the CHR data in bytes
        return len(self.sprite_set_data.chr_data)

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        # Render the actual CHR data
        # The exported name references the CHR index (start_offset in CHR-ROM space)
        code = self.sprite_set_data.chr_data
        return RenderedCodeBlock(code=code, exported_labels={self.label: start_offset})
