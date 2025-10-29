# NES-Compatible Assets Index

This document highlights assets that are most suitable for NES game development, based on tile size, color constraints, and overall aesthetic.

## Authentic NES Assets

### True NES Format
- **NES Tile Set Files** (`tiles/nes-tileset-files/`)
  - Contains actual `.chr` file: `NES Tile Set 1 U1.chr`
  - Ready for NES homebrew development
  - Includes PNG versions for preview/editing
  - 8x8 tiles, RPG themed (grass, stone, trees, water)

## 8x8 Pixel Assets (Perfect for NES)

### Tiles
- **Kenney Micro Roguelike** (`sprites/kenney_micro-roguelike/Tiles/`)
  - Monochrome and colored versions
  - Dungeon/roguelike themed
  - Tiny retro aesthetic

### Sprites
- **Kenney Pixel Shmup** (`sprites/kenney_pixel-shmup/`)
  - Space shooter sprites
  - Small, clean pixel art
  - Good for reduction to NES palette

## 16x16 Pixel Assets (NES-Friendly)

### Tiles - Excellent for NES
- **Zelda-like Tileset** (`tiles/zelda-like-tileset/`)
  - 16x16 RPG tiles
  - Overworld, cave, indoor tilesets
  - Character with sword animations
  - CC0 license

- **Hyptosis Batch 5** (`tiles/hyptosis_batch5.png`)
  - 16x16 tile sheet
  - RPG/fantasy themed
  - Good variety for NES games

- **16x16 Game Assets** (`tiles/16x16-tilesets/`, `tiles/16x16-base-items/`)
  - Multiple tilesets and items
  - Base character sprites
  - RPG themed

### Game Boy Assets (4-Color, Perfect for NES)
- **Game Boy Platformer Art** (`tiles/gameboy-platformer-art/`)
  - 16x16, 4 colors only
  - Ninja themed platformer
  - Authentic Game Boy palette
  - Includes tileset, character, weapons, effects

- **Game Boy Tilesets** (`tiles/gameboy-tileset-1.png`, `gameboy-tileset-2.png`)
  - Authentic GB color palette
  - Platform tiles
  - 4 colors (grayscale)

- **Game Boy Character - Fluffy** (`tiles/gameboy-character-fluffy/`)
  - Character sprite
  - 4-color palette
  - CC0 license

## 18x18 Pixel Assets (Reducible to 16x16)

- **Kenney Pixel Platformer** (`tiles/kenney_pixel-platformer/`)
  - 200 files, 18x18 tiles
  - Can be reduced to 16x16
  - Platformer themed

## UI Elements (NES-Compatible)

### Hearts & Health
Perfect for NES HUD elements:
- 8x8 health hearts (search results found)
- 16x16 health hearts (search results found)
- Various health bar designs

### HUD Elements
From existing assets in `sprites/Base pack/HUD/`:
- Numbers (hud_0.png through hud_9.png)
- Hearts (hud_heartEmpty.png, hud_heartFull.png, hud_heartHalf.png)
- Gems (hud_gem_*.png)
- Keys (hud_key*.png)
- Player indicators (hud_p1.png, hud_p2.png, hud_p3.png)

## Collectibles (Small, Simple, NES-Appropriate)

### From Existing Downloads
- **Coins** - Base pack has coin sprites
- **Gems** - Multiple gem sprites in base pack
- **Keys** - Colored keys (blue, green, red, yellow)
- **Stars** - Star collectibles

### Recommended Downloads
- Gems/Coins Free pack (16x16, animated, CC0)
- 8x8 collectibles from OpenGameArt

## Characters & Enemies

### Small Sprites (Reducible)
- **16x16 RPG Characters** (multiple packs found)
- **Game Boy Characters** (4-color, authentic)
- **Alien Sprites** (`sprites/Extra animations and enemies/Alien sprites/`)
  - Multiple color variants
  - Walk, climb, swim, jump animations

### Enemies
- **Enemy Sprites** (`sprites/Extra animations and enemies/Enemy sprites/`)
  - Bat, bee, fly, fish, frog, ghost
  - Mouse, piranha, slime, snail, snake
  - Spider, worm
  - Multiple animation states

## Backgrounds

### Parallax Layers
- **Pixel Art Parallax** (`unclassified/parallax-bg-*.png`)
  - 6 layers
  - Low-res, simple colors
  - Potentially NES-compatible with palette reduction

### Solid Backgrounds
- **Simple Backgrounds** (`sprites/Backgrounds/`)
  - black.png, blue.png, purple.png, darkPurple.png
  - Solid colors, perfect for NES

## Fonts

### Existing
- **Good Neighbors** (`fonts/good_neighbors.png`)
  - Pixel font bitmap

### Available to Download
- 8x8 bitmap fonts
- Monogram font (8x8, CC0)
- Various retro pixel fonts

## Reduction Strategies

### 32x32 → 16x16 Reduction Candidates
- Hyptosis batches 1-4 (32x32) could be reduced
- Many Kenney assets could work at half size
- Character sprites from platformer packs

### Color Reduction Candidates
Assets with clean designs and limited colors:
- Kenney Fish Pack
- Kenney Micro Roguelike
- Platformer base packs

## License Summary for NES Assets

- **CC0 (Public Domain):** Most Kenney assets, Game Boy assets, many OpenGameArt assets
- **CC-BY 3.0/4.0:** Hyptosis tiles (requires attribution)
- **Mixed:** Check individual metadata files

## File Formats

- **PNG:** Primary format for all assets
- **CHR:** Authentic NES format (`nes-tileset-files`)
- **Sprite Sheets:** Many assets include sprite sheet compilations
- **Individual Frames:** Most packs include separated frames

## Total Stats

- **~133MB** sprite assets
- **~16MB** tile assets
- **~3.5MB** icon assets
- **6,338** total image files
- **25+** archive downloads
- **1** authentic .CHR file

## Next Steps for NES Development

1. **Palette Analysis:** Scan images to identify 4-color palette candidates
2. **Sprite Extraction:** Extract individual sprites from sheets
3. **CHR Conversion:** Convert PNG tiles to .CHR format
4. **Size Validation:** Confirm 8x8 and 16x16 dimensions
5. **Color Reduction:** Reduce to NES palette (54 colors, 4 per sprite/bg)
