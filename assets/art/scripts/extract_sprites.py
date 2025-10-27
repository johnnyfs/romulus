#!/usr/bin/env python3
"""
Sprite extraction script for grouping and organizing game art assets.
Extracts individual sprites/characters from sprite sheets and creates metadata.
"""

from PIL import Image
import yaml
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class SpriteExtractor:
    def __init__(self, raw_sprites_dir: Path, grouped_sprites_dir: Path):
        self.raw_sprites_dir = raw_sprites_dir
        self.grouped_sprites_dir = grouped_sprites_dir
        self.grouped_sprites_dir.mkdir(parents=True, exist_ok=True)

    def load_raw_metadata(self, image_path: Path) -> Dict:
        """Load metadata YAML for a raw sprite file."""
        yaml_path = image_path.with_suffix('.yaml')
        if yaml_path.exists():
            with open(yaml_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}

    def save_grouped_metadata(self, name: str, metadata: Dict):
        """Save metadata YAML for a grouped sprite."""
        yaml_path = self.grouped_sprites_dir / f"{name}.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)

    def extract_grid_sprites(
        self,
        image_path: Path,
        sprite_width: int,
        sprite_height: int,
        name_prefix: str,
        pov: str,
        outlined: bool,
        genres: List[str],
        gender: str,
        tags: List[str],
        skip_empty: bool = True
    ):
        """
        Extract sprites arranged in a grid layout.

        Args:
            image_path: Path to source sprite sheet
            sprite_width: Width of each sprite in pixels
            sprite_height: Height of each sprite in pixels
            name_prefix: Prefix for generated sprite names
            pov: Point of view (overhead/side/pseudooverhead)
            outlined: Whether sprites use outline style
            genres: List of compatible genres
            gender: Gender classification (male/female/neuter)
            tags: Additional descriptive tags
            skip_empty: Skip fully transparent sprites
        """
        img = Image.open(image_path).convert('RGBA')
        raw_metadata = self.load_raw_metadata(image_path)

        width, height = img.size
        cols = width // sprite_width
        rows = height // sprite_height

        sprite_num = 0
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height

                # Extract sprite
                sprite = img.crop((x, y, x + sprite_width, y + sprite_height))

                # Skip if empty (all transparent)
                if skip_empty:
                    if sprite.getbbox() is None:
                        continue

                # Generate unique name
                sprite_name = f"{name_prefix}_{sprite_num:03d}"
                sprite_path = self.grouped_sprites_dir / f"{sprite_name}.png"

                # Save sprite
                sprite.save(sprite_path)

                # Create metadata
                metadata = {
                    'source_url': raw_metadata.get('source_url', ''),
                    'raw_file': str(image_path.relative_to(Path(__file__).parent.parent.parent.parent)),
                    'source_rect': {'x': x, 'y': y, 'width': sprite_width, 'height': sprite_height},
                    'pov': pov,
                    'outlined': outlined,
                    'genres': genres,
                    'gender': gender,
                    'tags': tags
                }

                self.save_grouped_metadata(sprite_name, metadata)
                sprite_num += 1

        print(f"Extracted {sprite_num} sprites from {image_path.name}")

    def extract_single_sprite(
        self,
        image_path: Path,
        name: str,
        pov: str,
        outlined: bool,
        genres: List[str],
        gender: str,
        tags: List[str],
        crop_rect: Optional[Tuple[int, int, int, int]] = None
    ):
        """Extract a single sprite (optionally cropping it)."""
        img = Image.open(image_path).convert('RGBA')
        raw_metadata = self.load_raw_metadata(image_path)

        if crop_rect:
            x, y, w, h = crop_rect
            sprite = img.crop((x, y, x + w, y + h))
            source_rect = {'x': x, 'y': y, 'width': w, 'height': h}
        else:
            sprite = img
            source_rect = {'x': 0, 'y': 0, 'width': img.width, 'height': img.height}

        # Save sprite
        sprite_path = self.grouped_sprites_dir / f"{name}.png"
        sprite.save(sprite_path)

        # Create metadata
        metadata = {
            'source_url': raw_metadata.get('source_url', ''),
            'raw_file': str(image_path.relative_to(Path(__file__).parent.parent.parent.parent)),
            'source_rect': source_rect,
            'pov': pov,
            'outlined': outlined,
            'genres': genres,
            'gender': gender,
            'tags': tags
        }

        self.save_grouped_metadata(name, metadata)
        print(f"Extracted sprite: {name}")


def main():
    # Set up paths
    repo_root = Path(__file__).parent.parent.parent.parent
    raw_sprites = repo_root / "assets/art/raw/sprites"
    grouped_sprites = repo_root / "assets/art/grouped/sprites"

    extractor = SpriteExtractor(raw_sprites, grouped_sprites)

    # Extract mychars.png - NES RPG characters with black outlines
    # This is a 12x10 grid of 16x16 sprites
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "mychars.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="nes_rpg_char",
        pov="pseudooverhead",
        outlined=True,
        genres=["fantasy", "rpg"],
        gender="neuter",  # Mixed genders in sheet
        tags=["nes", "4directional", "warrior", "mage"]
    )

    # Extract bard.png - single character sheet
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "bard.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="nes_bard",
        pov="pseudooverhead",
        outlined=True,
        genres=["fantasy", "rpg"],
        gender="neuter",
        tags=["nes", "4directional", "bard", "musician", "class"]
    )

    # Extract conjurer.png
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "conjurer.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="nes_conjurer",
        pov="pseudooverhead",
        outlined=True,
        genres=["fantasy", "rpg"],
        gender="neuter",
        tags=["nes", "4directional", "mage", "wizard", "class", "robe"]
    )

    # Extract scout.png
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "scout.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="nes_scout",
        pov="pseudooverhead",
        outlined=True,
        genres=["fantasy", "rpg"],
        gender="neuter",
        tags=["nes", "4directional", "scout", "ranger", "class"]
    )

    # Extract soldier.png
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "soldier.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="nes_soldier",
        pov="pseudooverhead",
        outlined=True,
        genres=["fantasy", "rpg", "military"],
        gender="neuter",
        tags=["nes", "4directional", "soldier", "warrior", "class", "armor"]
    )

    # Extract tricolor no-outline sprites (Dragon Warrior style)
    # $delphinewalk_sheet.png - 3x3 grid
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "$delphinewalk_sheet.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="tricolor_delphine",
        pov="pseudooverhead",
        outlined=False,
        genres=["fantasy", "rpg"],
        gender="female",
        tags=["nes", "4directional", "walk_cycle", "no_outline", "tricolor"]
    )

    # $popotawalk_sheet.png - 3x3 grid
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "$popotawalk_sheet.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="tricolor_popota",
        pov="pseudooverhead",
        outlined=False,
        genres=["fantasy", "rpg"],
        gender="male",
        tags=["nes", "4directional", "walk_cycle", "no_outline", "tricolor", "warrior"]
    )

    # popota_people.png - multiple characters
    extractor.extract_grid_sprites(
        image_path=raw_sprites / "popota_people.png",
        sprite_width=16,
        sprite_height=16,
        name_prefix="tricolor_people",
        pov="pseudooverhead",
        outlined=False,
        genres=["fantasy", "rpg"],
        gender="neuter",
        tags=["nes", "4directional", "no_outline", "tricolor"]
    )

    # $popota_dragonbosssprite.png - boss sprite
    extractor.extract_single_sprite(
        image_path=raw_sprites / "$popota_dragonbosssprite.png",
        name="tricolor_dragon_boss",
        pov="pseudooverhead",
        outlined=False,
        genres=["fantasy", "rpg"],
        gender="neuter",
        tags=["nes", "dragon", "boss", "monster", "no_outline", "tricolor", "32x32"]
    )

    print("\n✓ Sprite extraction complete!")


if __name__ == "__main__":
    main()
