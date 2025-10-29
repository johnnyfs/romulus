import uuid
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

type NESRef = uuid.UUID  # UUID referencing a component


class GameType(str, Enum):
    """Types of games/platforms supported."""

    NES = "nes"
    # Future: GAMEBOY = "gameboy", SNES = "snes", etc.


class ComponentType(str, Enum):
    """Types of components that can be attached to entities.

    Components define visual and behavioral aspects of entities.
    """

    # DEPRECATED: Palette components have been migrated to palette assets.
    # This exists only to keep the enum non-empty. Will be removed when real components are added.
    PALETTE = "palette"
    SPRITE = "sprite"


class ResourceType(str, Enum):
    """Types of raw resources that can be uploaded."""

    IMAGE = "image"


class AssetType(str, Enum):
    """Types of game assets."""

    PALETTE = "palette"


class ImageState(str, Enum):
    """Processing state of an image asset."""

    RAW = "raw"
    GROUPED = "grouped"
    CLEANED = "cleaned"


class ImageType(str, Enum):
    """Type of image asset."""

    SPRITE = "sprite"
    BACKGROUND = "background"
    MAP = "map"
    UI = "ui"
    ICON = "icon"
    PORTRAIT = "portrait"
    MISC = "misc"


class ImageTag(str, Enum):
    """Tags for image assets (hints for processing pipeline)."""

    OUTLINE = "outline"
    SCIFI = "scifi"
    FANTASY = "fantasy"
    CONTEMPORARY = "contemporary"
    OVERHEAD = "overhead"
    SIDE_VIEW = "side-view"
    PSEUDO_OVERHEAD = "pseudo-overhead"
    HI_RES = "hi-res"
    HI_COLOR = "hi-color"
    DESATURATED = "desaturated"
    DEDUPLICATED = "deduplicated"
    PADDED = "padded"


class NESColor(BaseModel):
    index: int


class NESPalette(BaseModel):
    # Color 0 is always transparent in NES palettes
    colors: tuple[NESColor, NESColor, NESColor]


# Component data schemas (discriminated union based on type)


class NESPaletteData(BaseModel):
    """Data for a palette component."""

    type: Literal[ComponentType.PALETTE] = ComponentType.PALETTE
    palettes: list[NESPalette]  # Up to 4 palettes for background or sprites


class NESSpriteData(BaseModel):
    """Data for a sprite component.

    Sprite dimensions are in sprite units:
    - For 8x8 mode: 1 unit = 8 pixels
    - For 8x16 mode: 1 unit = 8x16 pixels
    """

    type: Literal[ComponentType.SPRITE] = ComponentType.SPRITE
    width: int  # Width in sprite units (e.g., 2 = 16px in 8x8 mode, 2 = 16px wide in 8x16 mode)
    height: int  # Height in sprite units (e.g., 2 = 16px in 8x8 mode, 2 = 2 sprites tall in 8x16 mode)
    sprite_set: NESRef | None = None  # Reference to a sprite set asset (not implemented yet)


# Discriminated union of all component data types
ComponentData = Annotated[NESPaletteData | NESSpriteData, Field(discriminator="type")]


class NESEntity(BaseModel):
    """An entity with position data."""

    x: int  # X position (byte: 0-255)
    y: int  # Y position (byte: 0-255)


class NESScene(BaseModel):
    background_color: NESColor
    background_palettes: NESRef | None = None
    sprite_palettes: NESRef | None = None
    components: list[NESRef] = []
    entities: list[NESRef] = []  # References to game-level entities


# Resource data schemas (discriminated union based on type)


class ImageResourceData(BaseModel):
    """Data for an image resource."""

    type: Literal[ResourceType.IMAGE] = ResourceType.IMAGE
    state: ImageState
    image_type: ImageType
    tags: list[ImageTag] = []
    source_url: str | None = None  # URL to parent resource (for grouped/cleaned stages)
    license: str | None = None
    processed: bool = False  # Marks if this resource has been processed to the next stage


# Discriminated union of all resource data types
ResourceData = Annotated[ImageResourceData, Field(discriminator="type")]


# Asset data schemas (discriminated union based on type)


class NESPaletteAssetData(BaseModel):
    """Data for a palette asset."""

    type: Literal[AssetType.PALETTE] = AssetType.PALETTE
    palettes: list[NESPalette]  # Up to 4 palettes for background or sprites


# Discriminated union of all asset data types
AssetData = Annotated[NESPaletteAssetData, Field(discriminator="type")]


# Game data schemas (discriminated union based on game type)


class NESSpriteSize(str, Enum):
    """Sprite sizes supported by the NES."""

    SIZE_8X8 = "8x8"
    SIZE_8X16 = "8x16"


class NESGameData(BaseModel):
    """Data specific to NES games."""

    type: Literal[GameType.NES] = GameType.NES
    sprite_size: NESSpriteSize = NESSpriteSize.SIZE_8X8


# Discriminated union of all game data types
GameData = Annotated[NESGameData, Field(discriminator="type")]
