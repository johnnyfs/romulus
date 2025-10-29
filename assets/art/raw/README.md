# Raw Game Assets Collection

**Collection Date:** October 28, 2025
**Total Image Files:** 6,338+
**Total Size:** ~200MB
**Metadata Files:** 16

## Quick Start

1. **Browse by Type:** Check `/sprites/`, `/tiles/`, `/icons/`, `/fonts/`, `/unclassified/`
2. **NES-Specific Assets:** See [NES_COMPATIBLE_ASSETS.md](NES_COMPATIBLE_ASSETS.md)
3. **Full Inventory:** See [DOWNLOAD_SUMMARY.md](DOWNLOAD_SUMMARY.md)
4. **License Info:** Check `.metadata.json` files in each directory

## Directory Structure

```
assets/art/raw/
├── sprites/          # Character sprites, enemies, items (~133MB)
├── tiles/            # Terrain, platformer, dungeon tiles (~16MB)
├── icons/            # 496+ RPG icons (~3.5MB)
├── fonts/            # Pixel fonts
├── unclassified/     # Backgrounds, misc (~54MB)
├── README.md         # This file
├── DOWNLOAD_SUMMARY.md       # Comprehensive download list
└── NES_COMPATIBLE_ASSETS.md  # NES-specific asset index
```

## Highlights

### 🎮 NES-Ready Assets
- **Authentic .CHR File:** `tiles/nes-tileset-files/NES Tile Set 1 U1.chr`
- **8x8 Tiles:** Kenney Micro Roguelike, various roguelike packs
- **16x16 Tiles:** Zelda-like, Game Boy platformer, Hyptosis batch 5
- **4-Color Palettes:** All Game Boy assets

### 🎨 Asset Categories
- **Platformers:** Multiple Kenney packs, Game Boy platformer art
- **RPG:** Zelda-like tileset, 16x16 character sprites, 496 icons
- **Roguelike:** Kenney Micro Roguelike, 8x8 dungeon tiles
- **Space/Shmup:** Kenney space shooters, pixel shmup
- **Characters:** Aliens, enemies, player sprites with animations
- **UI/HUD:** Hearts, health bars, gems, coins, keys, numbers

### 📜 Licenses
- **CC0 (Public Domain):** Most Kenney assets, many OpenGameArt assets
- **CC-BY:** Hyptosis tiles, some OpenGameArt (attribution required)
- **Free with Credit Appreciated:** Many itch.io assets

## Key Sources

- **[Kenney.nl](https://kenney.nl)** - Professional CC0 asset packs
- **[OpenGameArt.org](https://opengameart.org)** - Community game assets
- **[itch.io](https://itch.io)** - Indie game asset marketplace

## Metadata Format

Each major download includes a `.metadata.json` file:

```json
{
  "source_url": "https://...",
  "download_url": "https://...",
  "license": "CC0",
  "author": "Creator Name",
  "asset_type": "sprites|tiles|fonts|ui",
  "style_hints": ["nes-compatible", "16x16", "pixel art", ...],
  "description": "Asset description",
  "tile_size": "8x8|16x16|32x32",
  "nes_compatible": true|false
}
```

## Finding Assets

### By Size
- **8x8:** Search for `tile_size: "8x8"` in metadata
- **16x16:** Search for `tile_size: "16x16"` in metadata
- **Small sprites:** Check Kenney micro/pixel packs

### By Style
Search `style_hints` in metadata files for:
- `nes-compatible`, `nes-style`
- `gameboy`, `4-color`
- `platformer`, `rpg`, `roguelike`
- `retro`, `pixel art`

### By License
- **No attribution needed:** Look for `CC0` license
- **Attribution required:** Look for `CC-BY` license

## Usage Examples

### For NES Game Development
1. Start with `tiles/nes-tileset-files/` for authentic NES tiles
2. Use Game Boy assets (4-color) as-is
3. Reduce 16x16 assets from Zelda-like or Hyptosis packs
4. Extract sprites from Kenney Micro Roguelike

### For Retro Platformer
1. Use Kenney Platformer Pack Redux for tiles
2. Use Game Boy platformer art for character
3. Use Base pack HUD elements for UI
4. Use parallax backgrounds from unclassified/

### For RPG
1. Use Zelda-like tileset for overworld
2. Use 496 RPG icons for items/inventory
3. Use 16x16 character sprites
4. Use enemy sprites from Extra animations pack

## Contributing Assets

To add new assets to this collection:

1. Download asset pack
2. Extract to appropriate directory
3. Create `.metadata.json` file with source info
4. Update DOWNLOAD_SUMMARY.md
5. If NES-compatible, update NES_COMPATIBLE_ASSETS.md

## Tools & Processing

### Recommended Tools
- **Aseprite:** Sprite editing, animation
- **Tiled:** Tilemap editing
- **GIMP:** Image editing, palette reduction
- **NES Screen Tool:** CHR editing
- **YY-CHR:** CHR editing

### Processing Pipeline
1. **Palette Analysis:** Identify colors used
2. **Color Reduction:** Reduce to NES palette
3. **Size Validation:** Ensure 8x8/16x16 alignment
4. **CHR Conversion:** Convert to .chr if needed
5. **Sprite Sheet Creation:** Combine related sprites

## Archive Files

All original `.zip` files are preserved alongside extracted directories for reference and redistribution.

## Notes

- **Not all assets are NES-compatible** - some require reduction/processing
- **Check licenses** before using in commercial projects
- **Metadata files** provide filtering capabilities for automation
- **Some archives may have nested structures** - explore extracted directories

## Questions?

See documentation files:
- [DOWNLOAD_SUMMARY.md](DOWNLOAD_SUMMARY.md) - Full asset list
- [NES_COMPATIBLE_ASSETS.md](NES_COMPATIBLE_ASSETS.md) - NES-specific guide
- Individual `.metadata.json` files - Detailed asset info
