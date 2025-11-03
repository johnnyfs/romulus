"""Tests for VBlankHandler and UpdateHandler conditional code assembly."""

from core.rom.code_block_registry import CodeBlockRegistry
from core.rom.label_registry import LabelRegistry
from core.rom.rom import Rom
from core.rom.subroutines import UpdateHandler, VBlankHandler


class TestVBlankHandler:
    """Tests for the VBlankHandler code block."""

    def test_vblank_handler_has_render_sprites_as_optional_dependency(self):
        """Verify that VBlankHandler lists render_sprites as an optional dependency."""
        handler = VBlankHandler()
        assert handler.optional_dependencies == ["render_sprites"]
        assert handler.dependencies == []

    def test_vblank_handler_renders_without_render_sprites(self):
        """Verify that VBlankHandler can render when render_sprites is not available."""
        handler = VBlankHandler()
        # Render with empty names (no render_sprites available)
        rendered = handler.render(start_offset=0x8000, names={})
        assert isinstance(rendered.code, bytes)
        # Should be empty or minimal since render_sprites is inline code
        assert len(rendered.code) == 0

    def test_vblank_handler_renders_with_render_sprites(self):
        """Verify that VBlankHandler renders when render_sprites is available."""
        handler = VBlankHandler()
        # Render with render_sprites in names
        rendered = handler.render(start_offset=0x8000, names={"render_sprites": 0x9000})
        assert isinstance(rendered.code, bytes)
        # Still empty since render_sprites is assembled inline, not called
        assert len(rendered.code) == 0


class TestUpdateHandler:
    """Tests for the UpdateHandler code block."""

    def test_update_handler_has_render_entities_as_optional_dependency(self):
        """Verify that UpdateHandler lists render_entities as an optional dependency."""
        handler = UpdateHandler()
        assert handler.optional_dependencies == ["render_entities"]
        assert handler.dependencies == []

    def test_update_handler_renders_without_render_entities(self):
        """Verify that UpdateHandler can render when render_entities is not available."""
        handler = UpdateHandler()
        # Render with empty names (no render_entities available)
        rendered = handler.render(start_offset=0x8000, names={})
        assert isinstance(rendered.code, bytes)
        # Should be empty since no JSR is emitted
        assert len(rendered.code) == 0

    def test_update_handler_renders_with_render_entities(self):
        """Verify that UpdateHandler emits JSR when render_entities is available."""
        handler = UpdateHandler()
        # Render with render_entities in names
        rendered = handler.render(start_offset=0x8000, names={"render_entities": 0x9000})
        assert isinstance(rendered.code, bytes)
        # Should contain JSR instruction (0x20) + 2-byte address
        assert len(rendered.code) == 3
        assert rendered.code[0] == 0x20  # JSR opcode
        assert rendered.code[1] == 0x00  # Low byte of 0x9000
        assert rendered.code[2] == 0x90  # High byte of 0x9000


class TestOptionalDependencies:
    """Tests for the optional dependencies system."""

    def test_rom_builder_adds_optional_dependencies_if_present(self):
        """Verify that ROM builder adds optional dependencies when they exist."""
        label_registry = LabelRegistry()
        registry = CodeBlockRegistry(label_registry=label_registry)
        rom = Rom()

        # Get update handler which has render_entities as optional dependency
        update_handler = registry["update_handler"]

        # Add it to ROM - should also add render_entities since it's in registry
        from core.rom.builder import RomBuilder

        builder = RomBuilder(db=None, rom=rom, label_registry=label_registry, code_block_registry=registry)
        builder._add(rom, update_handler)

        # Both update_handler and render_entities should be in ROM
        # (render_entities will be in PRG_ROM, update_handler in NMI_POST_VBLANK)
        from core.rom.rom import RomCodeArea

        assert "update_handler" in rom.code_blocks[RomCodeArea.NMI_POST_VBLANK]
        assert "render_entities" in rom.code_blocks[RomCodeArea.PRG_ROM]

    def test_rom_builder_skips_optional_dependencies_if_missing(self):
        """Verify that ROM builder skips optional dependencies when they don't exist."""
        label_registry = LabelRegistry()
        # Create registry without render_entities
        from core.rom.zero_page import ZeroPageEntityRAM, ZeroPageSpriteRAM

        registry = CodeBlockRegistry(label_registry=label_registry)
        # Remove render_entities from registry
        registry._code_blocks_by_label.pop("render_entities", None)

        rom = Rom()

        # Get update handler which has render_entities as optional dependency
        update_handler = registry["update_handler"]

        # Add it to ROM - should NOT fail even though render_entities is missing
        from core.rom.builder import RomBuilder

        builder = RomBuilder(db=None, rom=rom, label_registry=label_registry, code_block_registry=registry)
        builder._add(rom, update_handler)

        # Only update_handler should be in ROM, not render_entities
        from core.rom.rom import RomCodeArea

        assert "update_handler" in rom.code_blocks[RomCodeArea.NMI_POST_VBLANK]
        assert "render_entities" not in rom.code_blocks[RomCodeArea.PRG_ROM]
