import uuid
from unittest.mock import Mock

import pytest

from core.rom.data import AddressData, PaletteData, SceneData, EntityData
from core.rom.label_registry import LabelRegistry
from core.schemas import NESColor, NESPalette, NESPaletteAssetData, NESScene, NESEntity, ENTITY_SIZE_BYTES


class TestPaletteData:
    """Tests for PaletteData code block."""

    def test_palette_data_from_model_uses_registry_label(self):
        """Verify palette data uses label from registry."""
        asset_id = uuid.uuid4()
        registry = LabelRegistry()

        # Create a mock asset and add to registry
        mock_asset = Mock()
        mock_asset.id = asset_id
        mock_asset.type = "palette"
        mock_asset.name = "test_palette"
        registry._add_assets([mock_asset])

        palette_data_obj = NESPaletteAssetData(
            palettes=[
                NESPalette(
                    colors=(
                        NESColor(index=1),
                        NESColor(index=2),
                        NESColor(index=3),
                    )
                )
            ],
        )

        palette_data = PaletteData.from_model(
            id=asset_id,
            palette_data=palette_data_obj,
            registry=registry
        )

        assert palette_data.label == f"asset__palette__test_palette"

    def test_palette_data_has_no_dependencies(self):
        """Verify palette data has no dependencies."""
        asset_id = uuid.uuid4()
        registry = LabelRegistry()
        mock_asset = Mock()
        mock_asset.id = asset_id
        mock_asset.type = "palette"
        mock_asset.name = "test"
        registry._add_assets([mock_asset])

        palette_data = PaletteData.from_model(
            id=asset_id,
            palette_data=NESPaletteAssetData(
                palettes=[NESPalette(colors=(NESColor(index=1), NESColor(index=2), NESColor(index=3)))],
            ),
            registry=registry
        )

        assert palette_data.dependencies == []

    def test_palette_data_size_is_multiples_of_3(self):
        """Verify palette data size equals 3 bytes per palette."""
        asset_id = uuid.uuid4()
        registry = LabelRegistry()
        mock_asset = Mock()
        mock_asset.id = asset_id
        mock_asset.type = "palette"
        mock_asset.name = "test"
        registry._add_assets([mock_asset])

        # 1 palette = 3 colors = 3 bytes
        palette_data_1 = PaletteData.from_model(
            id=asset_id,
            palette_data=NESPaletteAssetData(
                palettes=[NESPalette(colors=(NESColor(index=1), NESColor(index=2), NESColor(index=3)))],
            ),
            registry=registry
        )
        assert palette_data_1.size == 3

        # 2 palettes = 6 colors = 6 bytes
        palette_data_2 = PaletteData.from_model(
            id=asset_id,
            palette_data=NESPaletteAssetData(
                palettes=[
                    NESPalette(colors=(NESColor(index=1), NESColor(index=2), NESColor(index=3))),
                    NESPalette(colors=(NESColor(index=4), NESColor(index=5), NESColor(index=6))),
                ],
            ),
            registry=registry
        )
        assert palette_data_2.size == 6

    def test_palette_data_renders_color_indices(self):
        """Verify palette renders as sequence of color indices."""
        asset_id = uuid.uuid4()
        registry = LabelRegistry()
        mock_asset = Mock()
        mock_asset.id = asset_id
        mock_asset.type = "palette"
        mock_asset.name = "test"
        registry._add_assets([mock_asset])

        palette_data = PaletteData.from_model(
            id=asset_id,
            palette_data=NESPaletteAssetData(
                palettes=[
                    NESPalette(colors=(NESColor(index=0x01), NESColor(index=0x02), NESColor(index=0x03))),
                    NESPalette(colors=(NESColor(index=0x14), NESColor(index=0x25), NESColor(index=0x36))),
                ],
            ),
            registry=registry
        )

        rendered = palette_data.render(start_offset=0x8000, names={})

        # Should be 6 bytes: 01 02 03 14 25 36
        assert rendered.code == bytes([0x01, 0x02, 0x03, 0x14, 0x25, 0x36])
        assert rendered.exported_labels == {f"asset__palette__test": 0x8000}


class TestAddressData:
    """Tests for AddressData code block (2-byte word references)."""

    def test_address_data_name(self):
        """Verify address data name is prefixed correctly."""
        registry = LabelRegistry()
        addr_data = AddressData.from_name(name="initial_scene", referenced_value_name="scene_data__main", registry=registry)
        assert addr_data.label == "data__initial_scene"

    def test_address_data_has_dependency(self):
        """Verify address data depends on referenced value."""
        registry = LabelRegistry()
        addr_data = AddressData.from_name(name="test", referenced_value_name="target_value", registry=registry)
        assert addr_data.dependencies == ["target_value"]

    def test_address_data_size_is_2_bytes(self):
        """Verify address data is always 2 bytes (word)."""
        registry = LabelRegistry()
        addr_data = AddressData.from_name(name="test", referenced_value_name="target", registry=registry)
        assert addr_data.size == 2

    def test_address_data_renders_little_endian_word(self):
        """Verify address data renders as little-endian 16-bit word."""
        registry = LabelRegistry()
        addr_data = AddressData.from_name(name="ptr", referenced_value_name="target", registry=registry)

        # Target is at address 0x9ABC
        rendered = addr_data.render(start_offset=0x8000, names={"target": 0x9ABC})

        # Little endian: BC 9A
        assert rendered.code == bytes([0xBC, 0x9A])
        assert rendered.exported_labels == {"data__ptr": 0x8000}

    def test_address_data_raises_if_referenced_value_missing(self):
        """Verify error if referenced value not in names dict."""
        registry = LabelRegistry()
        addr_data = AddressData.from_name(name="ptr", referenced_value_name="missing_target", registry=registry)

        with pytest.raises(ValueError, match="Referenced value name 'missing_target' not found"):
            addr_data.render(start_offset=0x8000, names={})


class TestSceneData:
    """Tests for SceneData code block."""

    def test_scene_data_from_model_uses_registry_label(self):
        """Verify scene data uses label from registry."""
        scene_id = uuid.uuid4()
        registry = LabelRegistry()

        # Create a mock scene and add to registry
        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        assert scene_data.label == "scene__main"

    def test_scene_data_with_no_palettes_has_no_dependencies(self):
        """Verify scene with no palettes has no dependencies."""
        scene_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        assert scene_data.dependencies == []

    def test_scene_data_depends_on_palette_references(self):
        """Verify scene depends on referenced palettes with correct asset__ prefix."""
        scene_id = uuid.uuid4()
        bg_palette_id = uuid.uuid4()
        sprite_palette_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add palette assets to registry
        mock_bg_asset = Mock()
        mock_bg_asset.id = bg_palette_id
        mock_bg_asset.type = "palette"
        mock_bg_asset.name = "bg_palette"

        mock_sprite_asset = Mock()
        mock_sprite_asset.id = sprite_palette_id
        mock_sprite_asset.type = "palette"
        mock_sprite_asset.name = "sprite_palette"

        registry._add_assets([mock_bg_asset, mock_sprite_asset])

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=bg_palette_id,
            sprite_palettes=sprite_palette_id,
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        assert "asset__palette__bg_palette" in scene_data.dependencies
        assert "asset__palette__sprite_palette" in scene_data.dependencies

    def test_scene_data_size_with_no_entities(self):
        """Verify scene with no entities is 1 byte (bg color) + 2 bytes (bg pal) + 2 bytes (sprite pal) + 2 bytes (null terminator)."""
        scene_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
            entities=[],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        # 1 (bg color) + 2 (bg pal) + 2 (sprite pal) + 2 (null terminator) = 7 bytes
        assert scene_data.size == 7

    def test_scene_data_size_with_entities(self):
        """Verify scene size includes 2 bytes per entity plus null terminator."""
        scene_id = uuid.uuid4()
        entity1_id = uuid.uuid4()
        entity2_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add entities to registry
        mock_entity1 = Mock()
        mock_entity1.id = entity1_id
        mock_entity1.name = "player"
        mock_entity1.components = []
        mock_entity2 = Mock()
        mock_entity2.id = entity2_id
        mock_entity2.name = "enemy"
        mock_entity2.components = []
        registry._add_entities([mock_entity1, mock_entity2])

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
            entities=[entity1_id, entity2_id],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        # 1 (bg color) + 2 (bg pal) + 2 (sprite pal) + 2 (entity1) + 2 (entity2) + 2 (null) = 11 bytes
        assert scene_data.size == 11

    def test_scene_data_renders_with_null_palettes(self):
        """Verify scene renders with null (0x0000) palette pointers and null-terminated entity list."""
        scene_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
            entities=[],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)
        rendered = scene_data.render(start_offset=0x9000, names={})

        # 0F (bg color) + 00 00 (null bg pal) + 00 00 (null sprite pal) + 00 00 (null terminator)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        assert rendered.exported_labels == {"scene__main": 0x9000}

    def test_scene_data_renders_with_palette_references(self):
        """Verify scene renders with palette pointer addresses using correct asset__ prefix."""
        scene_id = uuid.uuid4()
        bg_palette_id = uuid.uuid4()
        sprite_palette_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add palette assets to registry
        mock_bg_asset = Mock()
        mock_bg_asset.id = bg_palette_id
        mock_bg_asset.type = "palette"
        mock_bg_asset.name = "bg_palette"

        mock_sprite_asset = Mock()
        mock_sprite_asset.id = sprite_palette_id
        mock_sprite_asset.type = "palette"
        mock_sprite_asset.name = "sprite_palette"

        registry._add_assets([mock_bg_asset, mock_sprite_asset])

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x21),
            background_palettes=bg_palette_id,
            sprite_palettes=sprite_palette_id,
            entities=[],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        rendered = scene_data.render(
            start_offset=0x9000,
            names={
                "asset__palette__bg_palette": 0x9100,
                "asset__palette__sprite_palette": 0x9200,
            },
        )

        # 21 (bg color) + 00 91 (bg pal @ 0x9100) + 00 92 (sprite pal @ 0x9200) + 00 00 (null terminator)
        assert rendered.code == bytes([0x21, 0x00, 0x91, 0x00, 0x92, 0x00, 0x00])
        assert rendered.exported_labels == {"scene__main": 0x9000}

    def test_scene_data_with_missing_palette_uses_null(self):
        """Verify scene uses null pointer if palette ref not in names."""
        scene_id = uuid.uuid4()
        missing_palette_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add the missing palette to registry so labels work
        mock_asset = Mock()
        mock_asset.id = missing_palette_id
        mock_asset.type = "palette"
        mock_asset.name = "missing"
        registry._add_assets([mock_asset])

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=missing_palette_id,
            sprite_palettes=None,
            entities=[],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        # Missing palette should result in 0x0000
        rendered = scene_data.render(start_offset=0x9000, names={})

        # 0F (bg color) + 00 00 (missing -> null) + 00 00 (null sprite pal) + 00 00 (null terminator)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def test_scene_data_renders_with_entity_addresses(self):
        """Verify scene renders entity addresses correctly with null terminator."""
        scene_id = uuid.uuid4()
        entity1_id = uuid.uuid4()
        entity2_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add entities to registry
        mock_entity1 = Mock()
        mock_entity1.id = entity1_id
        mock_entity1.name = "player"
        mock_entity1.components = []
        mock_entity2 = Mock()
        mock_entity2.id = entity2_id
        mock_entity2.name = "enemy"
        mock_entity2.components = []
        registry._add_entities([mock_entity1, mock_entity2])

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
            entities=[entity1_id, entity2_id],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        rendered = scene_data.render(
            start_offset=0x9000,
            names={
                "entity__player": 0x9100,
                "entity__enemy": 0x9150,
            },
        )

        # 0F (bg color) + 00 00 (null bg pal) + 00 00 (null sprite pal) + 00 91 (player @ 0x9100) + 50 91 (enemy @ 0x9150) + 00 00 (null terminator)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x91, 0x50, 0x91, 0x00, 0x00])
        assert rendered.exported_labels == {"scene__main": 0x9000}

    def test_scene_data_depends_on_entities(self):
        """Verify scene depends on its entity labels."""
        scene_id = uuid.uuid4()
        entity1_id = uuid.uuid4()
        entity2_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add entities to registry
        mock_entity1 = Mock()
        mock_entity1.id = entity1_id
        mock_entity1.name = "player"
        mock_entity1.components = []
        mock_entity2 = Mock()
        mock_entity2.id = entity2_id
        mock_entity2.name = "enemy"
        mock_entity2.components = []
        registry._add_entities([mock_entity1, mock_entity2])

        mock_scene = Mock()
        mock_scene.id = scene_id
        mock_scene.name = "main"
        mock_scene.scene_data = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
            entities=[entity1_id, entity2_id],
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        assert "entity__player" in scene_data.dependencies
        assert "entity__enemy" in scene_data.dependencies


class TestEntityData:
    """Tests for EntityData code block."""

    def test_entity_data_from_model_uses_registry_label(self):
        """Verify entity data uses label from registry."""
        entity_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.name = "player"
        mock_entity.entity_data = NESEntity(x=10, y=20, spriteset=None, palette_index=0)
        mock_entity.components = []
        registry._add_entities([mock_entity])

        entity_data = EntityData.from_model(entity=mock_entity, registry=registry)

        assert entity_data.label == "entity__player"

    def test_entity_data_without_spriteset_has_no_dependencies(self):
        """Verify entity without spriteset has no dependencies."""
        entity_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.name = "player"
        mock_entity.entity_data = NESEntity(x=10, y=20, spriteset=None, palette_index=0)
        mock_entity.components = []
        registry._add_entities([mock_entity])

        entity_data = EntityData.from_model(entity=mock_entity, registry=registry)

        assert entity_data.dependencies == []

    def test_entity_data_with_spriteset_depends_on_asset(self):
        """Verify entity with spriteset depends on the sprite set asset."""
        entity_id = uuid.uuid4()
        spriteset_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add sprite set asset to registry
        mock_spriteset = Mock()
        mock_spriteset.id = spriteset_id
        mock_spriteset.type = "sprite_set"
        mock_spriteset.name = "hero_sprites"
        registry._add_assets([mock_spriteset])

        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.name = "player"
        mock_entity.entity_data = NESEntity(x=10, y=20, spriteset=spriteset_id, palette_index=2)
        mock_entity.components = []
        registry._add_entities([mock_entity])

        entity_data = EntityData.from_model(entity=mock_entity, registry=registry)

        assert "asset__sprite_set__hero_sprites" in entity_data.dependencies

    def test_entity_data_size_is_4_bytes(self):
        """Verify entity data is always 4 bytes (x, y, spriteset_idx, palette_idx)."""
        entity_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.name = "player"
        mock_entity.entity_data = NESEntity(x=10, y=20, spriteset=None, palette_index=0)
        mock_entity.components = []
        registry._add_entities([mock_entity])

        entity_data = EntityData.from_model(entity=mock_entity, registry=registry)

        assert entity_data.size == 4

    def test_entity_data_renders_position_and_sprite_info(self):
        """Verify entity renders x, y, spriteset index, and palette index."""
        entity_id = uuid.uuid4()
        spriteset_id = uuid.uuid4()
        registry = LabelRegistry()

        # Add sprite set asset
        mock_spriteset = Mock()
        mock_spriteset.id = spriteset_id
        mock_spriteset.type = "sprite_set"
        mock_spriteset.name = "hero_sprites"
        registry._add_assets([mock_spriteset])

        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.name = "player"
        mock_entity.entity_data = NESEntity(x=100, y=150, spriteset=spriteset_id, palette_index=2)
        mock_entity.components = []
        registry._add_entities([mock_entity])

        entity_data = EntityData.from_model(entity=mock_entity, registry=registry)

        # Spriteset at CHR tile index 5 (background is at 0, so entity sprites start at 1+)
        rendered = entity_data.render(
            start_offset=0x8000,
            names={"asset__sprite_set__hero_sprites": 5}
        )

        # 64 (x=100) + 96 (y=150) + 05 (spriteset tile idx=5) + 02 (palette idx=2)
        assert rendered.code == bytes([100, 150, 5, 2])
        assert rendered.exported_labels == {"entity__player": 0x8000}

    def test_entity_data_renders_without_spriteset(self):
        """Verify entity without spriteset renders with 0 for spriteset index."""
        entity_id = uuid.uuid4()
        registry = LabelRegistry()

        mock_entity = Mock()
        mock_entity.id = entity_id
        mock_entity.name = "invisible"
        mock_entity.entity_data = NESEntity(x=50, y=60, spriteset=None, palette_index=1)
        mock_entity.components = []
        registry._add_entities([mock_entity])

        entity_data = EntityData.from_model(entity=mock_entity, registry=registry)

        rendered = entity_data.render(start_offset=0x8000, names={})

        # 32 (x=50) + 3C (y=60) + 00 (no spriteset) + 01 (palette idx=1)
        assert rendered.code == bytes([50, 60, 0, 1])
        assert rendered.exported_labels == {"entity__invisible": 0x8000}

    def test_entity_data_size_matches_constant(self):
        """Verify that EntityData.size always equals ENTITY_SIZE_BYTES constant."""
        entity_id = uuid.uuid4()
        registry = LabelRegistry()

        # Test with spriteset
        mock_spriteset = Mock()
        mock_spriteset.id = uuid.uuid4()
        mock_spriteset.type = "sprite_set"
        mock_spriteset.name = "test_sprite"
        registry._add_assets([mock_spriteset])

        mock_entity1 = Mock()
        mock_entity1.id = entity_id
        mock_entity1.name = "with_sprite"
        mock_entity1.entity_data = NESEntity(x=10, y=20, spriteset=mock_spriteset.id, palette_index=1)
        mock_entity1.components = []
        registry._add_entities([mock_entity1])

        entity_data1 = EntityData.from_model(entity=mock_entity1, registry=registry)
        assert entity_data1.size == ENTITY_SIZE_BYTES

        # Test without spriteset
        mock_entity2 = Mock()
        mock_entity2.id = uuid.uuid4()
        mock_entity2.name = "without_sprite"
        mock_entity2.entity_data = NESEntity(x=30, y=40, spriteset=None, palette_index=0)
        mock_entity2.components = []
        registry._add_entities([mock_entity2])

        entity_data2 = EntityData.from_model(entity=mock_entity2, registry=registry)
        assert entity_data2.size == ENTITY_SIZE_BYTES

        # Verify constant matches actual implementation
        assert ENTITY_SIZE_BYTES == 4
