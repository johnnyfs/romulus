from core.rom.subroutines import RenderEntitiesSubroutine, RenderSpritesBlock
from core.schemas import ENTITY_SIZE_BYTES, MAX_N_SCENE_ENTITIES
from tests.rom.helpers import (
    MemoryObserver,
    create_test_cpu,
    run_subroutine,
)


class TestRenderEntitiesSubroutine:
    """Tests for the render_entities subroutine."""

    def test_converts_single_entity_to_sprite_format(self):
        """Verify that a single entity is converted to NES sprite format."""
        subroutine = RenderEntitiesSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__entity_ram_page": 0x10, "zp__sprite_ram_page": 0x11}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Set up entity RAM with one entity: x=100, y=80, spriteset=5, palette=2
        memory[0x0200] = 100  # X position
        memory[0x0201] = 80   # Y position
        memory[0x0202] = 5    # Spriteset CHR index
        memory[0x0203] = 2    # Palette index

        # Run the subroutine
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify sprite data in RAM at $0300
        # NES sprite format: Y, tile, attributes, X
        assert memory[0x0300] == 80, f"Sprite Y: expected 80, got {memory[0x0300]}"
        assert memory[0x0301] == 5, f"Sprite tile: expected 5, got {memory[0x0301]}"
        assert memory[0x0302] == 2, f"Sprite attributes: expected 2, got {memory[0x0302]}"
        assert memory[0x0303] == 100, f"Sprite X: expected 100, got {memory[0x0303]}"

        # Verify zp__sprite_ram_page was set to 0x03
        assert memory[0x11] == 0x03, f"Sprite RAM page: expected 0x03, got {memory[0x11]:02X}"

    def test_converts_multiple_entities_to_sprites(self):
        """Verify that multiple entities are converted sequentially."""
        subroutine = RenderEntitiesSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__entity_ram_page": 0x10, "zp__sprite_ram_page": 0x11}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Set up three entities
        entities = [
            (100, 80, 5, 2),   # Entity 0
            (50, 120, 7, 1),   # Entity 1
            (200, 60, 3, 3),   # Entity 2
        ]

        for i, (x, y, tile, pal) in enumerate(entities):
            base = 0x0200 + (i * ENTITY_SIZE_BYTES)
            memory[base] = x
            memory[base + 1] = y
            memory[base + 2] = tile
            memory[base + 3] = pal

        # Run the subroutine
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify all sprites were created
        for i, (x, y, tile, pal) in enumerate(entities):
            sprite_base = 0x0300 + (i * 4)
            assert memory[sprite_base] == y, f"Sprite {i} Y: expected {y}, got {memory[sprite_base]}"
            assert memory[sprite_base + 1] == tile, f"Sprite {i} tile: expected {tile}, got {memory[sprite_base + 1]}"
            assert memory[sprite_base + 2] == pal, f"Sprite {i} attr: expected {pal}, got {memory[sprite_base + 2]}"
            assert memory[sprite_base + 3] == x, f"Sprite {i} X: expected {x}, got {memory[sprite_base + 3]}"

    def test_processes_all_entity_slots(self):
        """Verify that all MAX_N_SCENE_ENTITIES entity slots are processed."""
        subroutine = RenderEntitiesSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__entity_ram_page": 0x10, "zp__sprite_ram_page": 0x11}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Fill all entity slots with test data
        for i in range(MAX_N_SCENE_ENTITIES):
            base = 0x0200 + (i * ENTITY_SIZE_BYTES)
            memory[base] = i & 0xFF          # X = entity index
            memory[base + 1] = (i + 1) & 0xFF  # Y = entity index + 1
            memory[base + 2] = (i + 2) & 0xFF  # Tile = entity index + 2
            memory[base + 3] = i % 4          # Palette = entity index mod 4

        # Run the subroutine
        run_subroutine(cpu, memory, subroutine_address=0x8000)

        # Verify all sprites were created correctly
        for i in range(MAX_N_SCENE_ENTITIES):
            sprite_base = 0x0300 + (i * 4)
            expected_y = (i + 1) & 0xFF
            expected_tile = (i + 2) & 0xFF
            expected_pal = i % 4
            expected_x = i & 0xFF

            assert memory[sprite_base] == expected_y, f"Sprite {i} Y mismatch"
            assert memory[sprite_base + 1] == expected_tile, f"Sprite {i} tile mismatch"
            assert memory[sprite_base + 2] == expected_pal, f"Sprite {i} attr mismatch"
            assert memory[sprite_base + 3] == expected_x, f"Sprite {i} X mismatch"

    def test_returns_via_rts(self):
        """Verify that the subroutine properly returns via RTS."""
        subroutine = RenderEntitiesSubroutine()
        code = subroutine.render(
            start_offset=0x8000,
            names={"zp__entity_ram_page": 0x10, "zp__sprite_ram_page": 0x11}
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # run_subroutine will fail if RTS doesn't work properly
        cycles = run_subroutine(cpu, memory, subroutine_address=0x8000)
        assert cycles > 0


class TestRenderSpritesBlock:
    """Tests for the render_sprites VBlank code block."""

    def test_triggers_oam_dma_transfer(self):
        """Verify that writing to OAMDMA register triggers sprite transfer."""
        block = RenderSpritesBlock()
        code = block.render(
            start_offset=0x8000,
            names={"zp__sprite_ram_page": 0x10}
        )

        # Set up observer for OAMDMA register
        oam_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={0x4014: oam_observer}
        )

        # Set zp__sprite_ram_page to 0x03 (sprite RAM at $0300)
        memory[0x10] = 0x03

        # Execute the code (not a subroutine, so just step through)
        max_cycles = 10
        for _ in range(max_cycles):
            if cpu.pc >= 0x8000 + len(code.code):
                break
            cpu.step()

        # Verify OAMDMA was written with the sprite RAM page
        oamdma_writes = oam_observer.get_writes_to(0x4014)
        assert len(oamdma_writes) == 1, f"Expected 1 OAMDMA write, got {len(oamdma_writes)}"
        assert oamdma_writes[0] == 0x03, f"Expected OAMDMA=0x03, got 0x{oamdma_writes[0]:02X}"

    def test_uses_sprite_ram_page_from_zero_page(self):
        """Verify that the sprite RAM page is read from zero page variable."""
        block = RenderSpritesBlock()
        code = block.render(
            start_offset=0x8000,
            names={"zp__sprite_ram_page": 0x10}
        )

        oam_observer = MemoryObserver()
        cpu, memory = create_test_cpu(
            code.code,
            code_address=0x8000,
            observers={0x4014: oam_observer}
        )

        # Test with different sprite RAM page
        memory[0x10] = 0x05

        # Execute the code
        max_cycles = 10
        for _ in range(max_cycles):
            if cpu.pc >= 0x8000 + len(code.code):
                break
            cpu.step()

        # Verify OAMDMA was written with the value from zero page
        oamdma_writes = oam_observer.get_writes_to(0x4014)
        assert oamdma_writes[0] == 0x05, f"Expected OAMDMA=0x05, got 0x{oamdma_writes[0]:02X}"
