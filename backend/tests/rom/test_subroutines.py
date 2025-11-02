from core.rom.subroutines import LoadSceneSubroutine
from core.schemas import ENTITY_SIZE_BYTES
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
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        # Set up PPU register observer
        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Create scene data at 0x9000
        scene_data = [
            0x0F,  # Background color (palette index 0x0F - black)
            0x00,
            0x00,  # BG palette pointer (null)
            0x00,
            0x00,  # Sprite palette pointer (null)
            0x00,
            0x00,  # Entity list null terminator
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
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Create BG palette data at 0x9100
        bg_palette = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C]
        memory.write(0x9100, bg_palette)

        # Create scene data pointing to BG palette
        scene_data = [
            0x0F,  # Background color
            0x00,
            0x91,  # BG palette pointer -> 0x9100
            0x00,
            0x00,  # Sprite palette pointer (null)
            0x00,
            0x00,  # Entity list null terminator
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
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Scene data with null BG palette pointer
        scene_data = [
            0x0F,  # Background color
            0x00,
            0x00,  # BG palette pointer (null)
            0x00,
            0x00,  # Sprite palette pointer (null)
            0x00,
            0x00,  # Entity list null terminator
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
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Create sprite palette data at 0x9200
        sprite_palette = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C]
        memory.write(0x9200, sprite_palette)

        # Scene data with sprite palette pointer
        scene_data = [
            0x0F,  # Background color
            0x00,
            0x00,  # BG palette pointer (null)
            0x00,
            0x92,  # Sprite palette pointer -> 0x9200
            0x00,
            0x00,  # Entity list null terminator
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
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Create both palettes
        bg_palette = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C]
        sprite_palette = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C]
        memory.write(0x9100, bg_palette)
        memory.write(0x9200, sprite_palette)

        # Scene data with both pointers
        scene_data = [
            0x0F,  # Background color
            0x00,
            0x91,  # BG palette pointer -> 0x9100
            0x00,
            0x92,  # Sprite palette pointer -> 0x9200
            0x00,
            0x00,  # Entity list null terminator
        ]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        run_subroutine(cpu, memory, subroutine_address=0x8000)

        ppu_data_writes = ppu_observer.get_writes_to(0x2007)

        # Should have: 16 BG palette bytes (1 backdrop + 15 with mirrors) + 16 sprite palette bytes = 32 total
        assert len(ppu_data_writes) == 32

        # Verify all palette values are present
        for palette_value in bg_palette + sprite_palette:
            assert palette_value in ppu_data_writes

    def test_enables_ppu_and_nmi_at_end(self):
        """Verify that PPU and NMI are enabled at the end of the subroutine."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Minimal scene data
        scene_data = [0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Added entity list null terminator
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
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Minimal scene data
        scene_data = [0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Added entity list null terminator
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        # run_subroutine will fail if RTS doesn't work properly
        # (it expects to return to 0xFFFF)
        cycles = run_subroutine(cpu, memory, subroutine_address=0x8000)

        # If we got here, RTS worked correctly
        assert cpu.pc == 0xFFFF
        assert cycles > 0  # Verify we executed some instructions

    def test_ppu_writes_exact_sequence_with_component_palette(self):
        """
        INTEGRATION TEST: Verify exact sequence of PPU writes when scene references a component palette.

        This is the critical test that verifies the complete PPU write sequence:
        1. PPU_ADDR = 0x3F (high byte)
        2. PPU_ADDR = 0x00 (low byte)
        3. PPU_DATA = background_color
        4. PPU_DATA = palette[0]
        5. PPU_DATA = palette[1]
        ... (all 12 palette bytes in sequence)

        This test simulates the real scenario where a scene has a background_palettes
        component reference (like "Classic Mario Set").
        """
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(start_offset=0x8000, names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14})

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Create the "Classic Mario Set" palette data (4 sub-palettes × 3 colors = 12 bytes)
        classic_mario_palette = [
            22, 39, 24,  # Palette 0
            26, 42, 25,  # Palette 1
            17, 33, 49,  # Palette 2
            40, 56, 22,  # Palette 3
        ]
        memory.write(0x8200, classic_mario_palette)

        # Create scene data referencing the palette
        scene_data = [
            0x02,  # Background color (index 2)
            0x00,
            0x82,  # BG palette pointer -> 0x8200 (little-endian)
            0x00,
            0x00,  # Sprite palette pointer (null)
            0x00,
            0x00,  # Entity list null terminator
        ]
        memory.write(0x9000, scene_data)

        # Set zp__src1 to point to scene data
        memory[0x10] = 0x00  # Low byte of 0x9000
        memory[0x11] = 0x90  # High byte of 0x9000

        # Run the subroutine
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Get all writes in chronological order
        all_writes = ppu_observer.get_writes()

        # Extract PPU_ADDR and PPU_DATA writes in order
        ppu_addr_writes = [(addr, value) for addr, value in all_writes if addr == 0x2006]
        ppu_data_writes = [(addr, value) for addr, value in all_writes if addr == 0x2007]

        # Verify PPU_ADDR sequence: should set address to $3F00 (palette RAM)
        # First two PPU_ADDR writes should be 0x3F, 0x00
        assert len(ppu_addr_writes) >= 2, f"Expected at least 2 PPU_ADDR writes, got {len(ppu_addr_writes)}"
        assert ppu_addr_writes[0][1] == 0x3F, f"First PPU_ADDR write should be 0x3F (high byte), got {ppu_addr_writes[0][1]:02X}"
        assert ppu_addr_writes[1][1] == 0x00, f"Second PPU_ADDR write should be 0x00 (low byte), got {ppu_addr_writes[1][1]:02X}"

        # Verify PPU_DATA sequence: bg_color followed by palette data
        # NES palette layout: backdrop at $3F00, then 4 palettes of 4 bytes each
        # But our palette data has 3 colors per palette (12 bytes), and backdrop is repeated at $3F04, $3F08, $3F0C
        # So we need: bg_color, pal0[0-2], bg_color, pal1[0-2], bg_color, pal2[0-2], bg_color, pal3[0-2]
        expected_data_writes = []
        expected_data_writes.append(0x02)  # $3F00: backdrop
        for i in range(4):  # 4 palettes
            # Add 3 colors from this palette
            expected_data_writes.extend(classic_mario_palette[i*3:(i+1)*3])
            # Add backdrop color at $3F04, $3F08, $3F0C (but not after last palette)
            if i < 3:
                expected_data_writes.append(0x02)
        assert len(ppu_data_writes) >= len(expected_data_writes), (
            f"Expected at least {len(expected_data_writes)} PPU_DATA writes, got {len(ppu_data_writes)}"
        )

        # Check exact sequence of the first 13 PPU_DATA writes
        actual_data_sequence = [value for addr, value in ppu_data_writes[:len(expected_data_writes)]]
        assert actual_data_sequence == expected_data_writes, (
            f"PPU_DATA write sequence mismatch.\n"
            f"Expected: {[f'{b:02X}' for b in expected_data_writes]}\n"
            f"Actual:   {[f'{b:02X}' for b in actual_data_sequence]}"
        )

    def test_loads_entity_data_into_ram(self):
        """Verify that entity data is loaded into RAM page $0200."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Create entity data at different addresses
        # Entity 1: x=100, y=150, spriteset_idx=1, palette_idx=2
        entity1_data = [100, 150, 1, 2]
        memory.write(0xA000, entity1_data)

        # Entity 2: x=50, y=75, spriteset_idx=3, palette_idx=1
        entity2_data = [50, 75, 3, 1]
        memory.write(0xA100, entity2_data)

        # Create scene data with entity list (null-terminated)
        scene_data = [
            0x0F,  # Background color
            0x00, 0x00,  # BG palette pointer (null)
            0x00, 0x00,  # Sprite palette pointer (null)
            # Entity addresses (little-endian)
            0x00, 0xA0,  # Entity 1 @ 0xA000
            0x00, 0xA1,  # Entity 2 @ 0xA100
            0x00, 0x00,  # Null terminator
        ]
        memory.write(0x9000, scene_data)

        # Set zp__src1 to point to scene data
        memory[0x10] = 0x00
        memory[0x11] = 0x90

        # Run the subroutine
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify entity data was copied to RAM page $0200
        # Entity 1 should be at $0200-$0203
        assert memory[0x0200] == 100, f"Entity 1 X: expected 100, got {memory[0x0200]}"
        assert memory[0x0201] == 150, f"Entity 1 Y: expected 150, got {memory[0x0201]}"
        assert memory[0x0202] == 1, f"Entity 1 spriteset: expected 1, got {memory[0x0202]}"
        assert memory[0x0203] == 2, f"Entity 1 palette: expected 2, got {memory[0x0203]}"

        # Entity 2 should be at $0204-$0207
        assert memory[0x0204] == 50, f"Entity 2 X: expected 50, got {memory[0x0204]}"
        assert memory[0x0205] == 75, f"Entity 2 Y: expected 75, got {memory[0x0205]}"
        assert memory[0x0206] == 3, f"Entity 2 spriteset: expected 3, got {memory[0x0206]}"
        assert memory[0x0207] == 1, f"Entity 2 palette: expected 1, got {memory[0x0207]}"

        # Verify zp__entity_ram_page was set to 0x02
        assert memory[0x14] == 0x02, f"Entity RAM page: expected 0x02, got {memory[0x14]:02X}"

    def test_handles_empty_entity_list(self):
        """Verify that empty entity list (immediate null terminator) works correctly."""
        subroutine = LoadSceneSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__src1": 0x10, "zp__src2": 0x12, "zp__entity_ram_page": 0x14}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Scene data with empty entity list
        scene_data = [
            0x0F,  # Background color
            0x00, 0x00,  # BG palette pointer (null)
            0x00, 0x00,  # Sprite palette pointer (null)
            0x00, 0x00,  # Null terminator (empty entity list)
        ]
        memory.write(0x9000, scene_data)

        memory[0x10] = 0x00
        memory[0x11] = 0x90

        # Run the subroutine - should not crash
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify zp__entity_ram_page was still set
        assert memory[0x14] == 0x02

        # Entity RAM should be zero (no entities loaded)
        # Just check a few bytes to confirm nothing was written
        assert memory[0x0200] == 0
        assert memory[0x0201] == 0
