#!/usr/bin/env python3
"""
Intelligent sprite grouping script.
Groups sprites by character/entity - each group contains all frames/variations of one character.
"""

from PIL import Image
import yaml
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


def load_raw_metadata(image_path: Path) -> Dict:
    """Load metadata YAML for a raw sprite file."""
    yaml_path = image_path.with_suffix('.yaml')
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def save_grouped_metadata(grouped_sprites_dir: Path, name: str, metadata: Dict):
    """Save metadata YAML for a grouped sprite (left-aligned, no indentation)."""
    yaml_path = grouped_sprites_dir / f"{name}.yaml"

    # Manually format YAML with no indentation
    lines = []
    lines.append(f"source_url: {metadata.get('source_url', '')}")
    lines.append(f"raw_file: {metadata.get('raw_file', '')}")

    # Source rect
    sr = metadata.get('source_rect', {})
    lines.append("source_rect:")
    lines.append(f"  x: {sr.get('x', 0)}")
    lines.append(f"  y: {sr.get('y', 0)}")
    lines.append(f"  width: {sr.get('width', 0)}")
    lines.append(f"  height: {sr.get('height', 0)}")

    lines.append(f"pov: {metadata.get('pov', 'unknown')}")
    lines.append(f"outlined: {str(metadata.get('outlined', False)).lower()}")

    # Genres
    genres = metadata.get('genres', [])
    if genres:
        lines.append("genres:")
        for g in genres:
            lines.append(f"- {g}")
    else:
        lines.append("genres: []")

    lines.append(f"gender: {metadata.get('gender', 'neuter')}")

    # Tags
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

    # Extract region
    region = img.crop((x, y, x + w, y + h))

    # Save
    group_path = grouped_sprites_dir / f"{group_name}.png"
    region.save(group_path)

    # Update metadata with source rect
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

    # mychars.png - 24x16 grid (384x256 pixels)
    # Looking at the image: appears to be 12 columns of 2-sprite-wide characters
    # Each character has 6 color variations vertically
    # Let's extract each 2x10 block as one character group (32x160 pixels)
    print("Processing mychars.png...")
    raw_meta = load_raw_metadata(raw_sprites / "mychars.png")
    for col in range(12):  # 12 character types
        x = col * 32  # 2 sprites wide (16*2)
        extract_region(
            raw_sprites / "mychars.png",
            x=x, y=0, w=32, h=160,  # 10 rows of color variations
            grouped_sprites_dir=grouped_sprites,
            group_name=f"nes_char_{col:02d}",
            metadata={
                'source_url': raw_meta.get('source_url', ''),
                'raw_file': 'assets/art/raw/sprites/mychars.png',
                'pov': 'pseudooverhead',
                'outlined': True,
                'genres': ['fantasy', 'rpg'],
                'gender': 'neuter',
                'tags': ['nes', '4directional', 'color_variants']
            }
        )
        group_count += 1
    print(f"  Created {12} character groups")

    # Apply same logic to other similar files
    for filename, prefix in [
        ('bard.png', 'nes_bard'),
        ('conjurer.png', 'nes_conjurer'),
        ('scout.png', 'nes_scout'),
        ('soldier.png', 'nes_soldier')
    ]:
        print(f"\nProcessing {filename}...")
        raw_meta = load_raw_metadata(raw_sprites / filename)
        for col in range(12):
            x = col * 32
            extract_region(
                raw_sprites / filename,
                x=x, y=0, w=32, h=160,
                grouped_sprites_dir=grouped_sprites,
                group_name=f"{prefix}_{col:02d}",
                metadata={
                    'source_url': raw_meta.get('source_url', ''),
                    'raw_file': f'assets/art/raw/sprites/{filename}',
                    'pov': 'pseudooverhead',
                    'outlined': True,
                    'genres': ['fantasy', 'rpg'],
                    'gender': 'neuter',
                    'tags': ['nes', '4directional', 'color_variants', prefix.split('_')[1]]
                }
            )
            group_count += 1
        print(f"  Created 12 character groups")

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

    # popota_people.png - 4 columns × 12 rows
    # Each column is one character
    print("\nProcessing popota_people.png (4 characters)...")
    raw_meta = load_raw_metadata(raw_sprites / "popota_people.png")
    for col in range(4):
        extract_region(
            raw_sprites / "popota_people.png",
            x=col * 16, y=0, w=16, h=192,  # 12 rows high
            grouped_sprites_dir=grouped_sprites,
            group_name=f"tricolor_people_{col:02d}",
            metadata={
                'source_url': raw_meta.get('source_url', ''),
                'raw_file': 'assets/art/raw/sprites/popota_people.png',
                'pov': 'pseudooverhead',
                'outlined': False,
                'genres': ['fantasy', 'rpg'],
                'gender': 'neuter',
                'tags': ['nes', '4directional', 'no_outline', 'tricolor']
            }
        )
        group_count += 1
    print(f"  Created 4 character groups")

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

        # Group by prefix
        prefix = png_file.name.split('_')[0]
        if prefix not in grouped_by_prefix:
            grouped_by_prefix[prefix] = []
        grouped_by_prefix[prefix].append(asset)

    # Write grouped manifest
    grouped_manifest_path = grouped_sprites / "manifest.json"
    with open(grouped_manifest_path, 'w') as f:
        json.dump({
            'assets': grouped_manifest,
            'grouped': grouped_by_prefix
        }, f, indent=2)
    print(f"  Manifest: {len(grouped_manifest)} groups")


if __name__ == "__main__":
    main()
