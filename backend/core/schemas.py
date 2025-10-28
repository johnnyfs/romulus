import uuid
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

type NESRef = uuid.UUID  # UUID referencing a component


class ComponentType(str, Enum):
    """Types of components that can be attached to a game."""

    PALETTE = "palette"


class AssetType(str, Enum):
    """Types of assets that can be stored."""

    IMAGE = "image"


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


# Discriminated union of all component data types
ComponentData = Annotated[NESPaletteData, Field(discriminator="type")]


class NESEntity(BaseModel):
    """An entity with position data."""

    x: int  # X position (byte: 0-255)
    y: int  # Y position (byte: 0-255)


class NESScene(BaseModel):
    background_color: NESColor
    background_palettes: NESRef | None = None
    sprite_palettes: NESRef | None = None
    components: list[NESRef] = []


# Asset data schemas (discriminated union based on type)


class ImageAssetData(BaseModel):
    """Data for an image asset."""

    type: Literal[AssetType.IMAGE] = AssetType.IMAGE
    state: ImageState
    image_type: ImageType
    tags: list[ImageTag] = []
    source_url: str | None = None  # URL to parent asset (for grouped/cleaned stages)
    license: str | None = None


# Discriminated union of all asset data types
AssetData = Annotated[ImageAssetData, Field(discriminator="type")]
