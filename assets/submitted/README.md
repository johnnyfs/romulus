# Submitted NES-Compatible Assets

**Total Submitted:** 32 high-quality NES-compatible assets
**Upload Status:** ✓ All successful
**Backend:** MinIO storage + PostgreSQL database

## Quick Stats

- **Tiles/Maps:** 17 assets (8x8 and 16x16, including monochrome)
- **Sprites:** 5 assets (characters and enemies)
- **Icons:** 3 assets (collectibles)
- **UI Elements:** 5 assets (hearts, gems, keys)
- **Fonts:** 2 assets (pixel fonts)
- **Backgrounds:** 1 asset (parallax layer)

## Batches

### [Batch 1](SUBMITTED_ASSETS.md) - General NES-Compatible (16 assets)
Wide variety of NES-friendly assets including tilesets, sprites, UI, and fonts.

### [Batch 2](BATCH2_SUBMITTED.md) - NES/Game Boy Focused (16 assets)
Specifically targeted authentic NES and Game Boy constrained assets:
- NES palette-limited tilesets
- Monochrome 8x8 tiles
- Game Boy 4-color assets
- Low-color enemy sprites

## NES Compatibility Highlights

### Perfect for NES (Can use as-is):
- **8x8 monochrome tiles** (5 assets) - Direct CHR conversion ready
- **8x8 colored tiles** (3 assets from batch 1)
- **Game Boy 4-color tilesets** (2 assets)

### Excellent for NES (Minor reduction needed):
- **16x16 tilesets** (8 assets) - Can be split or reduced
- **NES-constrained palettes** (3 assets) - Already use NES limitations
- **Simple sprites** - Low color count, easy palette mapping

### NES-Friendly (Processing required):
- **Larger tilesets** - Need palette reduction and splitting
- **Character sprites** - May need color reduction

## Directory Structure

```
assets/submitted/
├── tiles/          17 tilesets (8x8, 16x16, NES, Game Boy)
├── sprites/         5 character and enemy sprites
├── icons/           3 collectible items
├── ui/              5 HUD elements
├── fonts/           2 pixel fonts
├── parallax-bg-3.png
├── README.md        (this file)
├── SUBMITTED_ASSETS.md       (Batch 1 details)
├── BATCH2_SUBMITTED.md       (Batch 2 details)
├── upload_manifest.json      (Batch 1 manifest)
└── upload_manifest_batch2.json (Batch 2 manifest)
```

## License Summary

- **30/32 assets** are CC0 (public domain)
- **1 asset** is CC-BY 3.0 (Hyptosis - requires attribution)
- **1 asset** is CC-BY 4.0 (parallax background - requires attribution)
- **1 asset** has unknown license (good_neighbors font)

## Asset Pipeline Ready

All assets are now in the backend system and ready for:
1. ✓ Stored in MinIO
2. ✓ Database records created
3. ✓ Metadata tagged (type, tags, license)
4. → Palette extraction
5. → Color reduction
6. → Sprite sheet extraction
7. → CHR file generation
8. → NES ROM integration

## Accessing Assets

**Database:** Query `resources` table in PostgreSQL
**Storage:** MinIO bucket at `http://localhost:9000/assets/`
**API:** `GET /api/v1/resources` for full list
**Manifests:** JSON files with all resource IDs and download URLs

## Next Steps for Asset Pipeline

1. **Process monochrome 8x8 tiles** → Direct CHR conversion
2. **Extract NES palettes** from constrained tilesets
3. **Reduce 16x16 tiles** to 8x8 or keep as meta-tiles
4. **Create sprite animations** from character sprites
5. **Build tile atlases** for efficient ROM usage

---

**Generated:** October 29, 2025
**Source Collection:** 6,338+ images (~200MB) in [assets/art/raw/](../art/raw/)
**Curated & Uploaded:** 32 premium NES-compatible assets

---

## Batch 3: Collectibles & More Tiles (16 assets)

**Date:** October 29, 2025
See [BATCH3_SUBMITTED.md](BATCH3_SUBMITTED.md) for details.

### Batch 3 Highlights:
- Complete collectible sets (coins, gems, keys)
- 4 more monochrome 8x8 assets
- Castle, cave, and simple tilesets
- Completes heart set (full, half, empty)

**GRAND TOTAL: 48 ASSETS SUBMITTED!** 🎉
