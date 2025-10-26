import pytest

from core.rom.subroutines import LoadSceneSubroutine
from tests.rom.helpers import (
    MemoryObserver,
    create_test_cpu,
    run_subroutine,
)


class TestLoadSceneSubroutine:
    """Tests for the load_scene subroutine."""

    def test_loads_background_color_to_palette_index_0(self):
        """Verify that background color (byte 0) is written to palette index 0."""
        # Create the subroutine
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        # Set up PPU register observer
        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={range(0x2000, 0x2008): ppu_observer}
        )

        # Create scene data at 0x9000
        scene_data = [
            0x0F,  # Background color (palette index 0x0F - black)
            0x00, 0x00,  # BG palette pointer (null)
            0x00, 0x00,  # Sprite palette pointer (null)
        ]
        memory.write(0x9000, scene_data)

        # Set zp__src1 to point to scene data
        memory[0x10] = 0x00  # Low byte of 0x9000
        memory[0x11] = 0x90  # High byte of 0x9000

        # Run the subroutine
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify PPU writes
        writes = ppu_observer.get_writes()

        # Should have: BIT 0x2002, then set address to $3F00, then write bg color
        # Find the palette writes (after address setup)
        ppu_addr_writes = ppu_observer.get_writes_to(0x2006)
        ppu_data_writes = ppu_observer.get_writes_to(0x2007)

        # Should set PPU address to $3F00 (palette RAM)
        assert 0x3F in ppu_addr_writes  # High byte
        assert 0x00 in ppu_addr_writes  # Low byte

        # Should write background color 0x0F to PPU_DATA
        assert 0x0F in ppu_data_writes

    def test_loads_background_palette_when_pointer_is_not_null(self):
        """Verify that 12 bytes of BG palette data are loaded when pointer is non-null."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={range(0x2000, 0x2008): ppu_observer}
        )

        # Create BG palette data at 0x9100
        bg_palette = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C]
        memory.write(0x9100, bg_palette)

        # Create scene data pointing to BG palette
        scene_data = [
            0x0F,  # Background color
            0x00, 0x91,  # BG palette pointer -> 0x9100
            0x00, 0x00,  # Sprite palette pointer (null)
        ]
        memory.write(0x9000, scene_data)

        # Set zp__src1 to point to scene data
        memory[0x10] = 0x00
        memory[0x11] = 0x90

        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify BG palette was written to PPU_DATA
        ppu_data_writes = ppu_observer.get_writes_to(0x2007)

        # Should have: bg_color + 12 palette bytes
        # The writes should include all our palette values
        for palette_value in bg_palette:
            assert palette_value in ppu_data_writes

    def test_skips_background_palette_when_pointer_is_null(self):
        """Verify that BG palette is skipped when pointer is 0x0000."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={range(0x2000, 0x2008): ppu_observer}
        )

        # Scene data with null BG palette pointer
        scene_data = [
            0x0F,  # Background color
            0x00, 0x00,  # BG palette pointer (null)
            0x00, 0x00,  # Sprite palette pointer (null)
        ]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # With null pointers, should only write: bg_color
        ppu_data_writes = ppu_observer.get_writes_to(0x2007)

        # Should only have 1 write (background color)
        assert len(ppu_data_writes) == 1
        assert ppu_data_writes[0] == 0x0F

    def test_loads_sprite_palette_when_pointer_is_not_null(self):
        """Verify that 12 bytes of sprite palette data are loaded when pointer is non-null."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={range(0x2000, 0x2008): ppu_observer}
        )

        # Create sprite palette data at 0x9200
        sprite_palette = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C]
        memory.write(0x9200, sprite_palette)

        # Scene data with sprite palette pointer
        scene_data = [
            0x0F,  # Background color
            0x00, 0x00,  # BG palette pointer (null)
            0x00, 0x92,  # Sprite palette pointer -> 0x9200
        ]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        run_subroutine(cpu, memory, subroutine_address=0x8000)

        ppu_data_writes = ppu_observer.get_writes_to(0x2007)

        # Should have all sprite palette values
        for palette_value in sprite_palette:
            assert palette_value in ppu_data_writes

    def test_loads_both_palettes_when_both_pointers_are_not_null(self):
        """Verify both BG and sprite palettes are loaded when both pointers are non-null."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={range(0x2000, 0x2008): ppu_observer}
        )

        # Create both palettes
        bg_palette = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C]
        sprite_palette = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C]
        memory.write(0x9100, bg_palette)
        memory.write(0x9200, sprite_palette)

        # Scene data with both pointers
        scene_data = [
            0x0F,  # Background color
            0x00, 0x91,  # BG palette pointer -> 0x9100
            0x00, 0x92,  # Sprite palette pointer -> 0x9200
        ]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        run_subroutine(cpu, memory, subroutine_address=0x8000)

        ppu_data_writes = ppu_observer.get_writes_to(0x2007)

        # Should have: bg_color + 12 BG palette bytes + 12 sprite palette bytes = 25 total
        assert len(ppu_data_writes) == 25

        # Verify all palette values are present
        for palette_value in bg_palette + sprite_palette:
            assert palette_value in ppu_data_writes

    def test_enables_ppu_and_nmi_at_end(self):
        """Verify that PPU and NMI are enabled at the end of the subroutine."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={range(0x2000, 0x2008): ppu_observer}
        )

        # Minimal scene data
        scene_data = [0x0F, 0x00, 0x00, 0x00, 0x00]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Check PPUCTRL (0x2000) - should have 0x80 written (NMI enabled)
        ppuctrl_writes = ppu_observer.get_writes_to(0x2000)
        assert 0x80 in ppuctrl_writes

        # Check PPUMASK (0x2001) - should have 0x1E written (show bg, show sprites)
        ppumask_writes = ppu_observer.get_writes_to(0x2001)
        assert 0x1E in ppumask_writes

    def test_returns_via_rts(self):
        """Verify that the subroutine properly returns via RTS."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Minimal scene data
        scene_data = [0x0F, 0x00, 0x00, 0x00, 0x00]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        # run_subroutine will fail if RTS doesn't work properly
        # (it expects to return to 0xFFFF)
        cycles = run_subroutine(cpu, memory, subroutine_address=0x8000)

        # If we got here, RTS worked correctly
        assert cpu.pc == 0xFFFF
        assert cycles > 0  # Verify we executed some instructions
