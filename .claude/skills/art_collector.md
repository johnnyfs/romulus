# Art Collector Skill

This skill helps collect and organize public domain/CC0 pixel art assets for the Romulus game project.

## Directory Structure

```
assets/art/
├── raw/                    # Raw downloaded assets
│   ├── sprites/           # Character sprites, enemies, etc.
│   ├── tiles/             # Tilesets, backgrounds, environments
│   ├── portraits/         # Character portraits
│   ├── fonts/             # Pixel fonts
│   ├── icons/             # UI icons, item icons
│   ├── misc/              # Miscellaneous assets
│   └── unclassified/      # Assets pending classification
└── examples/
    └── screenshots/       # Reference screenshots from published games
```

## Collection Process

### Step 1: Check for Existing Downloads

Archives serve as markers for already-downloaded content. Before downloading:
- Check for existing `.zip` files in `raw/*/`
- Look for extracted folder names that match potential downloads

### Step 2: Search for Assets

Target sources:
- **OpenGameArt.org** - Focus on CC0 and public domain tags
- **itch.io** - Filter by CC0/public domain licenses
- **Kenney.nl** - All assets are CC0
- **Internet Archive** - For reference screenshots

Search categories:
- NES-compatible art (3-4 colors, appropriate palettes)
- 8-bit/16-bit pixel art (broader compatibility)
- Character sprites with animations
- Tilesets (platformer, RPG, dungeon, etc.)
- UI elements and icons
- Pixel fonts
- Background/parallax layers

### Step 3: Download Assets

For each new asset:
1. Download to appropriate `raw/` subdirectory
2. Keep archives intact (they serve as download markers)
3. Extract archives in place (files alongside .zip)
4. Note source URL and license in commit message

### Step 4: Document Downloads

Track in this file:
- Asset name
- Source URL
- License
- Date downloaded
- Initial category (may be reclassified later)

## Downloaded Assets Log

### 2025-10-26 - Initial Collection

#### Sprites
- **NES-Style RPG Characters** - opengameart.org - CC-BY-SA 3.0
- **Tricolor NES RPG Characters** - opengameart.org - CC-BY 4.0, OGA-BY 3.0
- **DENZI CC0 Monsters** (32x48) - opengameart.org - CC0
- **Kenney Platformer Complete Pack** - opengameart.org - CC0
- **Kenney Platformer Pixel Redux** - opengameart.org - CC0
- **Kenney Space Shooter Redux** - kenney.nl - CC0
- **Kenney Top-Down Shooter** - kenney.nl - CC0
- **Stick Figure Character 2D** - opengameart.org - CC0

#### Tiles
- **8-bit RPG Basic Tileset** - opengameart.org - CC0
- **8-bit City Tileset** - opengameart.org - CC0
- **Cave Tileset** (16x16) - opengameart.org - CC-BY 3.0, GPL 2.0
- **Castle 8-bit** - opengameart.org - CC0
- **16x16 Fantasy Tileset** - opengameart.org - CC-BY-SA 3.0
- **Simple Broad-Purpose Tileset** - opengameart.org - CC0
- **Parallax Forest Background** - opengameart.org - CC0
- **Parallax Forest Pack** - opengameart.org - CC0

#### Portraits
- **200 Lorestrome Portraits** - opengameart.org - CC0

#### Fonts
- **Good Neighbors Pixel Font** - opengameart.org - CC0

#### Icons
- **496 RPG Icons** - opengameart.org - CC0 (Public Domain)

#### Unclassified
- **DENZI CC0 Pack** - opengameart.org - CC0 (organized sprites, dungeons, monsters, items)
- **Public Domain Game Pack** - opengameart.org - CC0 (animals, architecture, nature, portraits, decorations)

#### Screenshots
- **NES Screenshots Archive** - archive.org - Collection for reference/training

## Asset Organization

**Three Levels:**

1. **Raw** (`assets/art/raw/sprites/`)
   - Original downloaded sprite sheets
   - Metadata YAML files with source URLs
   - Example: `mychars.png` (24×16 grid of multiple characters)

2. **Grouped** (`assets/art/grouped/sprites/`)
   - Character/entity groups extracted from raw files
   - Each group = one character's complete sprite set (all frames/colors)
   - Example: `nes_char_00.png` (one character type with 10 color variants)
   - Currently: 67 groups from processed files

3. **Refined** (future)
   - Individual frames sliced to 8×8 or 16×16 tiles
   - Optimized for NES CHR ROM format
   - Deduplicated and palette-optimized

## Asset Viewing

The project includes a React-based admin interface for viewing and vetting assets:

**Frontend Routes:**
- `/admin/assets/raw` - Browse all raw sprite files
- `/admin/assets/raw/:filename` - View raw asset details and derived groups
- `/admin/assets/grouped` - Browse all character/entity groups
- `/admin/assets/grouped/:filename` - View group details

**How It Works:**
1. Assets are symlinked: `frontend/public/assets` → `assets/`
2. Scripts generate manifest files:
   - `assets/art/raw/sprites/manifest.json`
   - `assets/art/grouped/sprites/manifest.json`
3. React components read manifests to display assets
4. Images served directly from public folder
5. **No backend API needed** - all static files

**After adding new raw assets:**
```bash
python3 assets/art/scripts/group_sprites.py
```

This script:
- Analyzes raw sprite sheets
- Extracts character/entity groups
- Generates left-aligned YAML metadata
- Updates manifest.json

## Next Steps

1. Classify extracted assets (automatic or manual)
2. Convert assets to NES-compatible palettes where needed
3. Organize into refined asset library
4. Create asset metadata database
5. Build composition ranker training data from screenshots

## Asset Quality Criteria

### NES-Compatible
- Max 4 colors per 8x8 tile
- 8x8 or 16x16 base tile size
- NES palette colors
- Transparent backgrounds

### Acceptable for Downsampling
- Higher resolution pixel art
- More than 4 colors (can be reduced)
- Modern pixel art styles
- Clear subjects and good composition

## License Compatibility

Prioritize in order:
1. **CC0 / Public Domain** - No attribution required
2. **CC-BY** - Attribution required
3. **CC-BY-SA** - Attribution + Share-alike
4. **OGA-BY** - OpenGameArt specific attribution

Always track attribution requirements for non-CC0 assets.

## Metadata Schema

### Raw Asset Metadata (`{filename}.yaml`)

Located alongside raw assets in `art/raw/*/`:

```yaml
source_url: https://opengameart.org/content/asset-name
```

### Grouped Asset Metadata (`{filename}.yaml`)

Located alongside grouped assets in `art/grouped/*/`:

```yaml
source_url: https://opengameart.org/content/asset-name  # From raw file
raw_file: assets/art/raw/sprites/filename.png            # Repo-relative path
source_rect:                                             # Extraction rectangle
  x: 0
  y: 0
  width: 16
  height: 16
pov: pseudooverhead                                      # Point of view
outlined: true                                           # Uses outline style
genres:                                                  # Compatible genres
  - fantasy
  - rpg
  - scifi
  - contemporary
  - military
  - sports
gender: male                                             # male/female/neuter
tags:                                                    # Additional descriptors
  - nes
  - 4directional
  - warrior
  - mage
  - robe
  - crown
  - armor
```

### Field Definitions

**pov** (Point of View):
- `overhead` - Literal overhead view (looking down from above)
- `side` - Side-scroller profile view (Metroid, Castlevania style)
- `pseudooverhead` - 3/4 overhead RPG view (Zelda, Final Fantasy style)

**outlined**:
- `true` - Uses black outline style (Final Fantasy, Pokémon)
- `false` - No outline style (Dragon Warrior, classic NES)

**genres** (list):
Common values: `fantasy`, `rpg`, `scifi`, `contemporary`, `military`, `sports`, `horror`, `western`, `cyberpunk`

**gender**:
- `male` - Clearly male character
- `female` - Clearly female character
- `neuter` - Gender neutral, ambiguous, or non-character

**tags** (list):
Freeform descriptive tags. Common examples:
- Technical: `nes`, `4directional`, `animated`, `walk_cycle`
- Classes: `warrior`, `mage`, `rogue`, `cleric`, `bard`
- Equipment: `armor`, `robe`, `crown`, `sword`, `shield`
- Creature types: `humanoid`, `monster`, `dragon`, `undead`
- Visual style: `chibi`, `realistic`, `cartoon`
