from pydantic import BaseModel


class NESColor(BaseModel):
    index: int


class NESPalette(BaseModel):
    # Color 0 is always transparent in NES palettes
    colors: tuple[NESColor, NESColor, NESColor]


class NESScene(BaseModel):
    background_color: NESColor
    background_palettes: tuple[NESPalette, NESPalette, NESPalette, NESPalette]
    sprite_palettes: tuple[NESPalette, NESPalette, NESPalette, NESPalette]