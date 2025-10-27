from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

type NESRef = str  # name referencing address in NES data


class ComponentType(str, Enum):
    """Types of components that can be attached to a game."""

    PALETTE = "palette"


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


class NESScene(BaseModel):
    background_color: NESColor
    background_palettes: NESRef | None = None
    sprite_palettes: NESRef | None = None
