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
    entity_labels: list[str] = []

    @classmethod
    def from_model(cls, scene: Scene, registry: LabelRegistry) -> Self:
        entity_labels = [registry.get_entity_label(entity_id) for entity_id in scene.scene_data.entities]
        return cls(
            label=registry.get_scene_label(scene.id),
            type=CodeBlockType.DATA,
            background_color=scene.scene_data.background_color,
            background_palette=registry.get_asset_label(id) if (id := scene.scene_data.background_palettes) else None,
            sprite_palette=registry.get_asset_label(id) if (id := scene.scene_data.sprite_palettes) else None,
            entity_labels=entity_labels
        )

    @property
    def dependencies(self) -> list[str]:
        dependencies = []
        if (self.background_palette is not None):
            dependencies.append(self.background_palette)
        if (self.sprite_palette is not None):
            dependencies.append(self.sprite_palette)
        dependencies.extend(self.entity_labels)
        return dependencies

    @property
    def size(self) -> int:
        """
        Scene data is variable length:
        - 1 byte for background color
        - 2 bytes for background palette address
        - 2 bytes for sprite palette address
        - 2 bytes per entity address
        - 2 bytes for null terminator (0x0000)
        """
        return 1 + 2 + 2 + (len(self.entity_labels) * 2) + 2

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = bytearray()

        # Background color
        code.append(self.background_color.index)

        # Background palettes address
        bg_pal_addr = 0
        if self.background_palette:
            bg_pal_addr = names.get(self.background_palette, 0)
        code.extend(bg_pal_addr.to_bytes(2, "little"))

        # Sprite palettes address
        sprite_pal_addr = 0
        if self.sprite_palette:
            sprite_pal_addr = names.get(self.sprite_palette, 0)
        code.extend(sprite_pal_addr.to_bytes(2, "little"))

        # Entity addresses (null-terminated array)
        for entity_label in self.entity_labels:
            entity_addr = names.get(entity_label, 0)
            code.extend(entity_addr.to_bytes(2, "little"))

        # Null terminator (0x0000)
        code.extend((0).to_bytes(2, "little"))

        return RenderedCodeBlock(code=bytes(code), exported_labels={self.label: start_offset})


class EntityData(CodeBlock):
    """
    An entity data code block.

    - contains entity position data (x, y) and sprite information
    """
    entity_data: NESEntity
    spriteset_label: str | None = None
    palette_index: int = 0

    @classmethod
    def from_model(cls, entity: Entity, registry: LabelRegistry) -> Self:
        """Entity depends on its spriteset asset (if any)."""
        spriteset_label = None
        if entity.entity_data.spriteset:
            spriteset_label = registry.get_asset_label(entity.entity_data.spriteset)

        return cls(
            label=registry.get_entity_label(entity.id),
            type=CodeBlockType.DATA,
            entity_data=entity.entity_data,
            spriteset_label=spriteset_label,
            palette_index=entity.entity_data.palette_index
        )

    @property
    def dependencies(self) -> list[str]:
        # Entities depend on:
        # - Their spriteset asset (if any)
        # - render_entities subroutine (to convert entity data to sprites)
        # - render_sprites VBlank block (to DMA sprites to PPU)
        deps = ["render_entities", "render_sprites"]
        if self.spriteset_label:
            deps.append(self.spriteset_label)
        return deps

    @property
    def size(self) -> int:
        """Entity is 4 bytes: x position + y position + spriteset idx + palette idx."""
        return 4

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = bytearray()

        # X position (byte)
        code.append(self.entity_data.x & 0xFF)

        # Y position (byte)
        code.append(self.entity_data.y & 0xFF)

        # Sprite set index
        # The spriteset label in names dict contains the CHR tile index
        # (background pattern is at index 0, entity sprites start at index 1+)
        spriteset_index = names.get(self.spriteset_label, 0) if self.spriteset_label else 0
        code.append(spriteset_index & 0xFF)

        # Palette index
        code.append(self.palette_index & 0xFF)

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
        # The exported name references the CHR tile index (start_offset / 16)
        # Each CHR tile is 16 bytes (8 bytes per bitplane)
        code = self.sprite_set_data.chr_data
        chr_tile_index = start_offset // 16
        return RenderedCodeBlock(code=code, exported_labels={self.label: chr_tile_index})
