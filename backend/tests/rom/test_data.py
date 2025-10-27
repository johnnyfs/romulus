import pytest

from core.rom.data import AddressData, PaletteData, SceneData
from core.schemas import ComponentType, NESColor, NESPalette, NESPaletteData, NESScene


class TestPaletteData:
    """Tests for PaletteData code block."""

    def test_palette_data_name(self):
        """Verify palette data name is prefixed correctly."""
        palette_data = PaletteData(
            _name="test_pal",
            _palette_data=NESPaletteData(
                type=ComponentType.PALETTE,
                palettes=[
                    NESPalette(
                        colors=(
                            NESColor(index=1),
                            NESColor(index=2),
                            NESColor(index=3),
                        )
                    )
                ],
            ),
        )

        assert palette_data.name == "palette_data__test_pal"

    def test_palette_data_has_no_dependencies(self):
        """Verify palette data has no dependencies."""
        palette_data = PaletteData(
            _name="test",
            _palette_data=NESPaletteData(
                type=ComponentType.PALETTE,
                palettes=[NESPalette(colors=(NESColor(index=1), NESColor(index=2), NESColor(index=3)))],
            ),
        )

        assert palette_data.dependencies == []

    def test_palette_data_size_is_multiples_of_3(self):
        """Verify palette data size equals 3 bytes per palette."""
        # 1 palette = 3 colors = 3 bytes
        palette_data_1 = PaletteData(
            _name="pal1",
            _palette_data=NESPaletteData(
                type=ComponentType.PALETTE,
                palettes=[NESPalette(colors=(NESColor(index=1), NESColor(index=2), NESColor(index=3)))],
            ),
        )
        assert palette_data_1.size == 3

        # 2 palettes = 6 colors = 6 bytes
        palette_data_2 = PaletteData(
            _name="pal2",
            _palette_data=NESPaletteData(
                type=ComponentType.PALETTE,
                palettes=[
                    NESPalette(colors=(NESColor(index=1), NESColor(index=2), NESColor(index=3))),
                    NESPalette(colors=(NESColor(index=4), NESColor(index=5), NESColor(index=6))),
                ],
            ),
        )
        assert palette_data_2.size == 6

    def test_palette_data_renders_color_indices(self):
        """Verify palette renders as sequence of color indices."""
        palette_data = PaletteData(
            _name="test",
            _palette_data=NESPaletteData(
                type=ComponentType.PALETTE,
                palettes=[
                    NESPalette(colors=(NESColor(index=0x01), NESColor(index=0x02), NESColor(index=0x03))),
                    NESPalette(colors=(NESColor(index=0x14), NESColor(index=0x25), NESColor(index=0x36))),
                ],
            ),
        )

        rendered = palette_data.render(start_offset=0x8000, names={})

        # Should be 6 bytes: 01 02 03 14 25 36
        assert rendered.code == bytes([0x01, 0x02, 0x03, 0x14, 0x25, 0x36])
        assert rendered.exported_names == {"palette_data__test": 0x8000}


class TestAddressData:
    """Tests for AddressData code block (2-byte word references)."""

    def test_address_data_name(self):
        """Verify address data name is prefixed correctly."""
        addr_data = AddressData(_name="initial_scene", _referenced_value_name="scene_data__main")
        assert addr_data.name == "data__initial_scene"

    def test_address_data_has_dependency(self):
        """Verify address data depends on referenced value."""
        addr_data = AddressData(_name="test", _referenced_value_name="target_value")
        assert addr_data.dependencies == ["target_value"]

    def test_address_data_size_is_2_bytes(self):
        """Verify address data is always 2 bytes (word)."""
        addr_data = AddressData(_name="test", _referenced_value_name="target")
        assert addr_data.size == 2

    def test_address_data_renders_little_endian_word(self):
        """Verify address data renders as little-endian 16-bit word."""
        addr_data = AddressData(_name="ptr", _referenced_value_name="target")

        # Target is at address 0x9ABC
        rendered = addr_data.render(start_offset=0x8000, names={"target": 0x9ABC})

        # Little endian: BC 9A
        assert rendered.code == bytes([0xBC, 0x9A])
        assert rendered.exported_names == {"data__ptr": 0x8000}

    def test_address_data_raises_if_referenced_value_missing(self):
        """Verify error if referenced value not in names dict."""
        addr_data = AddressData(_name="ptr", _referenced_value_name="missing_target")

        with pytest.raises(ValueError, match="Referenced value name 'missing_target' not found"):
            addr_data.render(start_offset=0x8000, names={})


class TestSceneData:
    """Tests for SceneData code block."""

    def test_scene_data_name(self):
        """Verify scene data name is prefixed correctly."""
        scene = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
        )
        scene_data = SceneData(_name="main", _scene=scene)

        assert scene_data.name == "scene_data__main"

    def test_scene_data_with_no_palettes_has_no_dependencies(self):
        """Verify scene with no palettes has no dependencies."""
        scene = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
        )
        scene_data = SceneData(_name="main", _scene=scene)

        assert scene_data.dependencies == []

    def test_scene_data_depends_on_palette_references(self):
        """Verify scene depends on referenced palettes."""
        scene = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes="bg_palette",
            sprite_palettes="sprite_palette",
        )
        scene_data = SceneData(_name="main", _scene=scene)

        assert "bg_palette" in scene_data.dependencies
        assert "sprite_palette" in scene_data.dependencies

    def test_scene_data_size_is_5_bytes(self):
        """Verify scene is 1 byte (bg color) + 2 bytes (bg pal ptr) + 2 bytes (sprite pal ptr)."""
        scene = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
        )
        scene_data = SceneData(_name="main", _scene=scene)

        assert scene_data.size == 5

    def test_scene_data_renders_with_null_palettes(self):
        """Verify scene renders with null (0x0000) palette pointers."""
        scene = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes=None,
            sprite_palettes=None,
        )
        scene_data = SceneData(_name="main", _scene=scene)

        rendered = scene_data.render(start_offset=0x9000, names={})

        # 0F (bg color) + 00 00 (null bg pal) + 00 00 (null sprite pal)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00])
        assert rendered.exported_names == {"scene_data__main": 0x9000}

    def test_scene_data_renders_with_palette_references(self):
        """Verify scene renders with palette pointer addresses."""
        scene = NESScene(
            background_color=NESColor(index=0x21),
            background_palettes="bg_pal",
            sprite_palettes="sprite_pal",
        )
        scene_data = SceneData(_name="main", _scene=scene)

        rendered = scene_data.render(
            start_offset=0x9000,
            names={
                "bg_pal": 0x9100,
                "sprite_pal": 0x9200,
            },
        )

        # 21 (bg color) + 00 91 (bg pal @ 0x9100) + 00 92 (sprite pal @ 0x9200)
        assert rendered.code == bytes([0x21, 0x00, 0x91, 0x00, 0x92])
        assert rendered.exported_names == {"scene_data__main": 0x9000}

    def test_scene_data_with_missing_palette_uses_null(self):
        """Verify scene uses null pointer if palette ref not in names."""
        scene = NESScene(
            background_color=NESColor(index=0x0F),
            background_palettes="missing_palette",
            sprite_palettes=None,
        )
        scene_data = SceneData(_name="main", _scene=scene)

        # Missing palette should result in 0x0000
        rendered = scene_data.render(start_offset=0x9000, names={})

        # 0F (bg color) + 00 00 (missing -> null) + 00 00 (null sprite pal)
        assert rendered.code == bytes([0x0F, 0x00, 0x00, 0x00, 0x00])
