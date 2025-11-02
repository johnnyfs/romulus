import uuid
from unittest.mock import Mock

import pytest

from core.rom.data import AddressData, PaletteData, SceneData
from core.rom.label_registry import LabelRegistry
from core.schemas import NESColor, NESPalette, NESPaletteAssetData, NESScene


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

    def test_scene_data_size_is_5_bytes(self):
        """Verify scene is 1 byte (bg color) + 2 bytes (bg pal ptr) + 2 bytes (sprite pal ptr)."""
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

        assert scene_data.size == 5

    def test_scene_data_renders_with_null_palettes(self):
        """Verify scene renders with null (0x0000) palette pointers."""
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
        rendered = scene_data.render(start_offset=0x9000, names={})

        # 0F (bg color) + 00 00 (null bg pal) + 00 00 (null sprite pal)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00])
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

        # 21 (bg color) + 00 91 (bg pal @ 0x9100) + 00 92 (sprite pal @ 0x9200)
        assert rendered.code == bytes([0x21, 0x00, 0x91, 0x00, 0x92])
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
        )
        registry._add_scenes([mock_scene])

        scene_data = SceneData.from_model(scene=mock_scene, registry=registry)

        # Missing palette should result in 0x0000
        rendered = scene_data.render(start_offset=0x9000, names={})

        # 0F (bg color) + 00 00 (missing -> null) + 00 00 (null sprite pal)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00])
