# Submitted Assets to Backend

**Date:** October 29, 2025
**Total Submitted:** 16 assets
**All Successfully Uploaded:** ✓

## Summary

16 carefully curated NES-compatible assets have been uploaded to the backend MinIO storage and registered in the resource database. These assets represent a diverse collection of high-quality, NES-friendly pixel art including tiles, sprites, UI elements, fonts, and backgrounds.

## Uploaded Assets

### Tiles (8 assets)

1. **tiny16-basictiles.png** → [tiles/tiny16-basictiles.png](tiles/tiny16-basictiles.png)
   - Resource ID: `60c66348-3203-4ebf-ba08-d51239c526bd`
   - Type: map (overhead)
   - License: CC0
   - 16x16 RPG basic tileset

2. **tiny16-characters.png** → [tiles/tiny16-characters.png](tiles/tiny16-characters.png)
   - Resource ID: `1e0fc809-8640-4ed5-a55d-3459360fbd01`
   - Type: sprite (overhead)
   - License: CC0
   - 16x16 character sprites

3. **gameboy-tileset-1.png** → [tiles/gameboy-tileset-1.png](tiles/gameboy-tileset-1.png)
   - Resource ID: `e5c3b8bb-b106-4ae1-b799-c57321c70ad3`
   - Type: map (side-view, desaturated)
   - License: CC0
   - 4-color authentic Game Boy palette platformer tileset

4. **tile_0000.png** → [tiles/tile_0000.png](tiles/tile_0000.png)
   - Resource ID: `675fd7ae-f821-4842-ba12-dc8f8422445e`
   - Type: map (overhead)
   - License: CC0
   - 8x8 Kenney Micro Roguelike dungeon floor tile

5. **tile_0015.png** → [tiles/tile_0015.png](tiles/tile_0015.png)
   - Resource ID: `0c7e66dd-a0c9-4089-bece-a1d8371a1166`
   - Type: map (overhead)
   - License: CC0
   - 8x8 Kenney Micro Roguelike dungeon wall tile

6. **tile_0024.png** → [tiles/tile_0024.png](tiles/tile_0024.png)
   - Resource ID: `83a5cbb0-6c04-405f-a60d-00ccadeb4dd8`
   - Type: map (overhead)
   - License: CC0
   - 8x8 Kenney Micro Roguelike dungeon door tile

7. **hyptosis_batch5.png** → [tiles/hyptosis_batch5.png](tiles/hyptosis_batch5.png)
   - Resource ID: `148ba010-85ab-4a05-9ef5-f23eebc2af7d`
   - Type: map (overhead, hi-color)
   - License: CC-BY 3.0
   - 16x16 large RPG tileset collection by Hyptosis

8. **puny-dungeon-tileset.png** → [tiles/puny-dungeon-tileset.png](tiles/puny-dungeon-tileset.png)
   - Resource ID: `13d111f9-52e0-4abd-b46c-c4414ba019e4`
   - Type: map (overhead)
   - License: CC0
   - 16x16 dungeon tileset (2025 release)

### Sprites (2 assets)

9. **p1_stand.png** → [sprites/p1_stand.png](sprites/p1_stand.png)
   - Resource ID: `f79631bc-f748-4eaf-83c9-bf1696162aff`
   - Type: sprite (side-view)
   - License: CC0
   - Player character standing sprite

10. **fish_blue.png** → [sprites/fish_blue.png](sprites/fish_blue.png)
    - Resource ID: `3fb3ed5d-7061-4e1d-a9d3-5fa3f69d331a`
    - Type: sprite (side-view)
    - License: CC0
    - Blue fish sprite - underwater enemy/character

### UI Elements (4 assets)

11. **hud_heartFull.png** → [ui/hud_heartFull.png](ui/hud_heartFull.png)
    - Resource ID: `c54ad695-79b4-4265-a2eb-8b4a71d6ab95`
    - Type: ui
    - License: CC0
    - Full heart HUD element

12. **hud_gem_red.png** → [ui/hud_gem_red.png](ui/hud_gem_red.png)
    - Resource ID: `442430db-6502-47dd-873f-5ebcf429b6d1`
    - Type: ui
    - License: CC0
    - Red gem collectible HUD icon

13. **hud_keyBlue.png** → [ui/hud_keyBlue.png](ui/hud_keyBlue.png)
    - Resource ID: `62c4ec2b-e684-42c8-a417-e709271142ad`
    - Type: ui
    - License: CC0
    - Blue key collectible HUD icon

### Fonts (2 assets)

14. **good_neighbors.png** → [fonts/good_neighbors.png](fonts/good_neighbors.png)
    - Resource ID: `76ea7d95-3206-4cc9-9f3f-3a1b07b16c31`
    - Type: ui
    - License: Unknown
    - Good Neighbors pixel font bitmap

15. **tiny16-fontlarge.png** → [fonts/tiny16-fontlarge.png](fonts/tiny16-fontlarge.png)
    - Resource ID: `f5572012-7e81-4d81-b33a-ca99f38d9b5a`
    - Type: ui
    - License: CC0
    - Tiny 16 large font - pixel font for text

### Backgrounds (1 asset)

16. **parallax-bg-3.png** → [parallax-bg-3.png](parallax-bg-3.png)
    - Resource ID: `d56d9e22-fbc2-49d8-a173-9c53ba20bd02`
    - Type: background
    - License: CC-BY 4.0
    - Parallax background layer 3

## Access

All assets are stored in MinIO at: `http://localhost:9000/assets/`

Database records created in: PostgreSQL `resources` table

Download URLs generated with 7-day expiry signed URLs.

## Next Steps

These raw assets are now ready for:
1. Processing by the asset pipeline
2. Palette extraction and reduction
3. Sprite sheet extraction
4. CHR file conversion (for 8x8 tiles)
5. NES game integration

## License Compliance

- **14/16 assets** are CC0 (public domain) - no attribution required
- **1 asset** is CC-BY 3.0 (Hyptosis) - requires attribution
- **1 asset** is CC-BY 4.0 (parallax BG) - requires attribution
- **1 asset** has unknown license (good_neighbors font) - needs verification

## Storage Manifest

Complete upload manifest with all resource IDs, storage keys, and download URLs available at:
[/tmp/upload_manifest.json](/tmp/upload_manifest.json)
