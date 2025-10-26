from enum import Enum

from pydantic import BaseModel


type NESRef = str # name referencing address in NES data


class ComponentType(str, Enum):
    """Types of components that can be attached to a game."""
    PALETTE = "palette"

class NESColor(BaseModel):
    index: int


class NESPalette(BaseModel):
    # Color 0 is always transparent in NES palettes
    colors: tuple[NESColor, NESColor, NESColor]


class NESScene(BaseModel):
    background_color: NESColor
    background_palettes: NESRef | None = None
    sprite_palettes: NESRef | None = None