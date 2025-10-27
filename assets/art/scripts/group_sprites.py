#!/usr/bin/env python3
"""
Sprite grouping script - extracts character/entity groups from raw sprite sheets.
Each group = one character with all its frames/animations/color variants.
"""

from PIL import Image
import yaml
import json
from pathlib import Path
from typing import Dict


def load_raw_metadata(image_path: Path) -> Dict:
    """Load metadata YAML for a raw sprite file."""
    yaml_path = image_path.with_suffix('.yaml')
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def save_grouped_metadata(grouped_sprites_dir: Path, name: str, metadata: Dict):
    """Save metadata YAML for a grouped sprite (left-aligned)."""
    yaml_path = grouped_sprites_dir / f"{name}.yaml"

    lines = []
    lines.append(f"source_url: {metadata.get('source_url', '')}")
    lines.append(f"raw_file: {metadata.get('raw_file', '')}")

    sr = metadata.get('source_rect', {})
    lines.append("source_rect:")
    lines.append(f"  x: {sr.get('x', 0)}")
    lines.append(f"  y: {sr.get('y', 0)}")
    lines.append(f"  width: {sr.get('width', 0)}")
    lines.append(f"  height: {sr.get('height', 0)}")

    lines.append(f"pov: {metadata.get('pov', 'unknown')}")
    lines.append(f"outlined: {str(metadata.get('outlined', False)).lower()}")

    genres = metadata.get('genres', [])
    if genres:
        lines.append("genres:")
        for g in genres:
            lines.append(f"- {g}")
    else:
        lines.append("genres: []")

    lines.append(f"gender: {metadata.get('gender', 'neuter')}")

    tags = metadata.get('tags', [])
    if tags:
        lines.append("tags:")
        for t in tags:
            lines.append(f"- {t}")
    else:
        lines.append("tags: []")

    with open(yaml_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def extract_region(image_path: Path, x: int, y: int, w: int, h: int,
                   grouped_sprites_dir: Path, group_name: str, metadata: Dict):
    """Extract a rectangular region as a group."""
    img = Image.open(image_path).convert('RGBA')
    region = img.crop((x, y, x + w, y + h))

    group_path = grouped_sprites_dir / f"{group_name}.png"
    region.save(group_path)

    metadata['source_rect'] = {'x': x, 'y': y, 'width': w, 'height': h}
    save_grouped_metadata(grouped_sprites_dir, group_name, metadata)

    return group_name


def main():
    repo_root = Path(__file__).parent.parent.parent.parent
    raw_sprites = repo_root / "assets/art/raw/sprites"
    grouped_sprites = repo_root / "assets/art/grouped/sprites"

    # Clear existing grouped sprites
    if grouped_sprites.exists():
        for f in grouped_sprites.glob("*"):
            f.unlink()
    grouped_sprites.mkdir(parents=True, exist_ok=True)

    print("Grouping sprites by character/entity...\n")
    group_count = 0

    # CORRECTED: mychars.png, bard.png, etc.
    # Structure: 8 characters in 4×2 layout
    # Each character: 96×128 pixels (3×4 grid of 32×32 frames)
    for filename, prefix in [
        ('mychars.png', 'nes_char'),
        ('bard.png', 'nes_bard'),
        ('conjurer.png', 'nes_conjurer'),
        ('scout.png', 'nes_scout'),
        ('soldier.png', 'nes_soldier')
    ]:
        print(f"Processing {filename}...")
        raw_meta = load_raw_metadata(raw_sprites / filename)

        # 4 characters across, 2 down
        char_num = 0
        for row in range(2):
            for col in range(4):
                x = col * 96  # Each character is 96px wide (6 tiles)
                y = row * 128  # Each character is 128px tall (8 tiles)

                extract_region(
                    raw_sprites / filename,
                    x=x, y=y, w=96, h=128,
                    grouped_sprites_dir=grouped_sprites,
                    group_name=f"{prefix}_{char_num:02d}",
                    metadata={
                        'source_url': raw_meta.get('source_url', ''),
                        'raw_file': f'assets/art/raw/sprites/{filename}',
                        'pov': 'pseudooverhead',
                        'outlined': True,
                        'genres': ['fantasy', 'rpg'],
                        'gender': 'neuter',
                        'tags': ['nes', '4directional', '12frames', prefix.split('_')[-1]]
                    }
                )
                char_num += 1
                group_count += 1

        print(f"  Created 8 character groups")

    # Single character walk cycles
    print("\nProcessing $delphinewalk_sheet.png (single character)...")
    img = Image.open(raw_sprites / "$delphinewalk_sheet.png")
    raw_meta = load_raw_metadata(raw_sprites / "$delphinewalk_sheet.png")
    extract_region(
        raw_sprites / "$delphinewalk_sheet.png",
        x=0, y=0, w=img.width, h=img.height,
        grouped_sprites_dir=grouped_sprites,
        group_name="tricolor_delphine",
        metadata={
            'source_url': raw_meta.get('source_url', ''),
            'raw_file': 'assets/art/raw/sprites/$delphinewalk_sheet.png',
            'pov': 'pseudooverhead',
            'outlined': False,
            'genres': ['fantasy', 'rpg'],
            'gender': 'female',
            'tags': ['nes', '4directional', 'walk_cycle', 'no_outline', 'tricolor']
        }
    )
    group_count += 1

    print("\nProcessing $popotawalk_sheet.png (single character)...")
    img = Image.open(raw_sprites / "$popotawalk_sheet.png")
    raw_meta = load_raw_metadata(raw_sprites / "$popotawalk_sheet.png")
    extract_region(
        raw_sprites / "$popotawalk_sheet.png",
        x=0, y=0, w=img.width, h=img.height,
        grouped_sprites_dir=grouped_sprites,
        group_name="tricolor_popota",
        metadata={
            'source_url': raw_meta.get('source_url', ''),
            'raw_file': 'assets/art/raw/sprites/$popotawalk_sheet.png',
            'pov': 'pseudooverhead',
            'outlined': False,
            'genres': ['fantasy', 'rpg'],
            'gender': 'male',
            'tags': ['nes', '4directional', 'walk_cycle', 'no_outline', 'tricolor', 'warrior']
        }
    )
    group_count += 1

    # popota_people.png - 4 characters, each 48×64 pixels (3×4 grid of 16×16 sprites)
    # Content bounding box: (6, 128, 380, 256) - so content starts at y=128
    print("\nProcessing popota_people.png (4 characters)...")
    raw_meta = load_raw_metadata(raw_sprites / "popota_people.png")

    # Expected: 4 groups, each 48×64, starting at y=128
    for col in range(4):
        x = 6 + (col * 48)  # Start at x=6 (bbox left), each character is 48px wide
        extract_region(
            raw_sprites / "popota_people.png",
            x=x, y=128, w=48, h=64,  # Content starts at y=128
            grouped_sprites_dir=grouped_sprites,
            group_name=f"tricolor_people_{col:02d}",
            metadata={
                'source_url': raw_meta.get('source_url', ''),
                'raw_file': 'assets/art/raw/sprites/popota_people.png',
                'pov': 'pseudooverhead',
                'outlined': False,
                'genres': ['fantasy', 'rpg'],
                'gender': 'neuter',
                'tags': ['nes', '4directional', 'no_outline', 'tricolor', '12frames']
            }
        )
        group_count += 1
    print(f"  Created 4 character groups (48×64 each, starting at y=128)")

    # Dragon boss
    print("\nProcessing $popota_dragonbosssprite.png (single boss)...")
    img = Image.open(raw_sprites / "$popota_dragonbosssprite.png")
    raw_meta = load_raw_metadata(raw_sprites / "$popota_dragonbosssprite.png")
    extract_region(
        raw_sprites / "$popota_dragonbosssprite.png",
        x=0, y=0, w=img.width, h=img.height,
        grouped_sprites_dir=grouped_sprites,
        group_name="tricolor_dragon_boss",
        metadata={
            'source_url': raw_meta.get('source_url', ''),
            'raw_file': 'assets/art/raw/sprites/$popota_dragonbosssprite.png',
            'pov': 'pseudooverhead',
            'outlined': False,
            'genres': ['fantasy', 'rpg'],
            'gender': 'neuter',
            'tags': ['nes', 'dragon', 'boss', 'monster', 'no_outline', 'tricolor', '32x32']
        }
    )
    group_count += 1

    # DENZI_CC0_32x48_monsters.png - extract individual monsters
    print("\nProcessing DENZI_CC0_32x48_monsters.png...")
    img = Image.open(raw_sprites / "DENZI_CC0_32x48_monsters.png")
    raw_meta = load_raw_metadata(raw_sprites / "DENZI_CC0_32x48_monsters.png")

    # This appears to be various sized sprites, extract as single group for now
    extract_region(
        raw_sprites / "DENZI_CC0_32x48_monsters.png",
        x=0, y=0, w=img.width, h=img.height,
        grouped_sprites_dir=grouped_sprites,
        group_name="denzi_monsters",
        metadata={
            'source_url': raw_meta.get('source_url', ''),
            'raw_file': 'assets/art/raw/sprites/DENZI_CC0_32x48_monsters.png',
            'pov': 'side',
            'outlined': True,
            'genres': ['fantasy', 'horror'],
            'gender': 'neuter',
            'tags': ['monsters', 'various_sizes', '32x48']
        }
    )
    group_count += 1

    print(f"\n✓ Sprite grouping complete! Created {group_count} groups")

    print("\nGenerating manifest...")
    generate_manifest(repo_root)
    print("✓ Done!")


def generate_manifest(repo_root: Path):
    """Generate manifest.json for grouped sprites."""
    grouped_sprites = repo_root / "assets/art/grouped/sprites"
    grouped_manifest = []
    grouped_by_prefix = {}

    for png_file in sorted(grouped_sprites.glob("*.png")):
        yaml_file = png_file.with_suffix('.yaml')
        metadata = {}
        if yaml_file.exists():
            with open(yaml_file, 'r') as f:
                metadata = yaml.safe_load(f) or {}

        asset = {
            'name': png_file.name,
            'path': f"/assets/art/grouped/sprites/{png_file.name}",
            'metadata': metadata
        }

        grouped_manifest.append(asset)

        prefix = png_file.name.split('_')[0]
        if prefix not in grouped_by_prefix:
            grouped_by_prefix[prefix] = []
        grouped_by_prefix[prefix].append(asset)

    grouped_manifest_path = grouped_sprites / "manifest.json"
    with open(grouped_manifest_path, 'w') as f:
        json.dump({
            'assets': grouped_manifest,
            'grouped': grouped_by_prefix
        }, f, indent=2)
    print(f"  Manifest: {len(grouped_manifest)} groups")


if __name__ == "__main__":
    main()
