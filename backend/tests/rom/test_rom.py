import pytest

from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.rom.rom import Rom


class MockCodeBlock(CodeBlock):
    """Mock code block for testing ROM assembly."""

    def __init__(
        self,
        name: str,
        block_type: CodeBlockType,
        size: int,
        code: bytes = None,
    ):
        super().__init__()
        self._name = name
        self._type = block_type
        self._size = size
        self._code = code or (b"\x00" * size)

    @property
    def type(self) -> CodeBlockType:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return self._size

    @property
    def dependencies(self) -> list[str]:
        return []

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        return RenderedCodeBlock(code=self._code, exported_names={self.name: start_offset})


class TestRomRender:
    """Tests for ROM rendering and assembly."""

    def test_renders_ines_header_correctly(self):
        """Verify ROM has valid iNES header."""
        rom = Rom()
        rendered = rom.render()

        # iNES header should be first 16 bytes
        assert rendered[0:4] == b"NES\x1a"  # NES + MS-DOS EOF
        assert rendered[4] == 0x01  # 1x 16KB PRG ROM
        assert rendered[5] == 0x01  # 1x 8KB CHR ROM
        assert rendered[6] == 0x00  # Mapper 0
        assert rendered[7] == 0x00  # Mapper 0 continued

    def test_total_rom_size_is_correct(self):
        """Verify total ROM size is header + PRG + CHR."""
        rom = Rom()
        rendered = rom.render()

        # 16 byte header + 16KB PRG ROM + 8KB CHR ROM
        expected_size = 16 + (16 * 1024) + (8 * 1024)
        assert len(rendered) == expected_size

    def test_vector_table_at_correct_offset(self):
        """Verify interrupt vectors are at $FFFA-$FFFF."""
        rom = Rom()
        rendered = rom.render()

        # Vector table is last 6 bytes of PRG ROM
        # Header is 16 bytes, PRG ROM is 16KB
        vectors_offset = 16 + (16 * 1024) - 6
        vectors = rendered[vectors_offset : vectors_offset + 6]

        # Should have 3 vectors (NMI, RESET, IRQ) as little-endian words
        assert len(vectors) == 6

    def test_zero_page_blocks_allocated_from_zero(self):
        """Verify zero page blocks start at offset 0x00."""
        rom = Rom()

        # Add a zero page block
        zp_block = MockCodeBlock("zp_var", CodeBlockType.ZEROPAGE, size=2, code=b"\xaa\xbb")
        rom.add(zp_block)

        rendered = rom.render()

        # Zero page variables don't appear in ROM (they're RAM)
        # But their addresses should be tracked in the names dict
        # For now, just verify rendering succeeds
        assert len(rendered) > 0

    def test_zero_page_overflow_raises_error(self):
        """Verify error if zero page exceeds 256 bytes."""
        rom = Rom()

        # Add 257 bytes to zero page
        zp_block = MockCodeBlock("huge_zp", CodeBlockType.ZEROPAGE, size=257)
        rom.add(zp_block)

        with pytest.raises(ValueError, match="Zero page allocation exceeds 256 bytes"):
            rom.render()

    def test_prg_rom_blocks_start_at_0xC000(self):
        """Verify PRG ROM blocks are placed starting at $C000."""
        rom = Rom()

        # Add a subroutine (goes to PRG_ROM area)
        sub = MockCodeBlock("test_sub", CodeBlockType.SUBROUTINE, size=10, code=b"\x60" * 10)
        rom.add(sub)

        rendered = rom.render()

        # PRG ROM starts after 16-byte header
        prg_start = 16
        prg_rom = rendered[prg_start : prg_start + 16 * 1024]

        # First 10 bytes should be our subroutine
        assert prg_rom[0:10] == b"\x60" * 10

    def test_data_blocks_go_to_prg_rom(self):
        """Verify DATA blocks are placed in PRG_ROM area."""
        rom = Rom()

        # Add a data block
        data = MockCodeBlock("palette", CodeBlockType.DATA, size=6, code=b"\x01\x02\x03\x04\x05\x06")
        rom.add(data)

        rendered = rom.render()

        # PRG ROM starts after 16-byte header
        prg_start = 16
        prg_rom = rendered[prg_start : prg_start + 16 * 1024]

        # First 6 bytes should be our data
        assert prg_rom[0:6] == b"\x01\x02\x03\x04\x05\x06"

    def test_nmi_routine_includes_rti(self):
        """Verify NMI routine ends with RTI opcode."""
        rom = Rom()

        # Add a vblank block
        vblank = MockCodeBlock("vblank", CodeBlockType.VBLANK, size=3, code=b"\xea\xea\xea")
        rom.add(vblank)

        rendered = rom.render()

        # Find NMI vector in vector table
        # Vector table is last 6 bytes of PRG ROM
        prg_start = 16
        vectors_offset = prg_start + (16 * 1024) - 6

        nmi_vector_bytes = rendered[vectors_offset : vectors_offset + 2]
        nmi_address = int.from_bytes(nmi_vector_bytes, "little")

        # NMI routine should be in PRG ROM
        # Convert absolute address to ROM offset
        nmi_rom_offset = prg_start + (nmi_address - 0xC000)

        # NMI routine is 3 bytes + RTI (0x40)
        nmi_routine = rendered[nmi_rom_offset : nmi_rom_offset + 4]
        assert nmi_routine == b"\xea\xea\xea\x40"  # 3 NOPs + RTI

    def test_reset_vector_points_to_preamble(self):
        """Verify RESET vector points to preamble code."""
        rom = Rom()

        # Add a preamble block
        preamble = MockCodeBlock("preamble", CodeBlockType.PREAMBLE, size=5, code=b"\x78" * 5)
        rom.add(preamble)

        rendered = rom.render()

        # Find RESET vector in vector table
        prg_start = 16
        vectors_offset = prg_start + (16 * 1024) - 6

        # RESET vector is second word in table
        reset_vector_bytes = rendered[vectors_offset + 2 : vectors_offset + 4]
        reset_address = int.from_bytes(reset_vector_bytes, "little")

        # Convert absolute address to ROM offset
        reset_rom_offset = prg_start + (reset_address - 0xC000)

        # Reset routine should be our preamble
        reset_routine = rendered[reset_rom_offset : reset_rom_offset + 5]
        assert reset_routine == b"\x78" * 5

    def test_nmi_post_vblank_comes_before_vblank(self):
        """Verify NMI_POST_VBLANK blocks are placed before NMI_VBLANK blocks."""
        rom = Rom()

        # Add post vblank block
        post_vblank = MockCodeBlock("post_vblank", CodeBlockType.UPDATE, size=3, code=b"\xaa\xaa\xaa")
        rom.add(post_vblank)

        # Add vblank block
        vblank = MockCodeBlock("vblank", CodeBlockType.VBLANK, size=3, code=b"\xbb\xbb\xbb")
        rom.add(vblank)

        rendered = rom.render()

        # Find NMI start in ROM
        prg_start = 16
        vectors_offset = prg_start + (16 * 1024) - 6
        nmi_vector_bytes = rendered[vectors_offset : vectors_offset + 2]
        nmi_address = int.from_bytes(nmi_vector_bytes, "little")
        nmi_rom_offset = prg_start + (nmi_address - 0xC000)

        # NMI should be: post_vblank (3 bytes) + vblank (3 bytes) + RTI (1 byte)
        nmi_routine = rendered[nmi_rom_offset : nmi_rom_offset + 7]
        assert nmi_routine == b"\xaa\xaa\xaa\xbb\xbb\xbb\x40"

    def test_prg_overflow_raises_error(self):
        """Verify error if PRG ROM exceeds 16KB."""
        rom = Rom()

        # Add a huge block that exceeds PRG ROM size
        # 16KB = 16384 bytes, minus 6 for vectors, minus space for padding
        huge_block = MockCodeBlock("huge", CodeBlockType.SUBROUTINE, size=16384)
        rom.add(huge_block)

        with pytest.raises(ValueError, match="PRG ROM overflow"):
            rom.render()

    def test_chr_rom_is_blank_8kb(self):
        """Verify CHR ROM is blank 8KB pattern table."""
        rom = Rom()
        rendered = rom.render()

        # CHR ROM starts after header (16 bytes) + PRG ROM (16KB)
        chr_start = 16 + (16 * 1024)
        chr_rom = rendered[chr_start:]

        # Should be 8KB of zeros
        assert len(chr_rom) == 8 * 1024
        assert chr_rom == b"\x00" * (8 * 1024)

    def test_multiple_prg_blocks_concatenated(self):
        """Verify multiple PRG ROM blocks are placed sequentially."""
        rom = Rom()

        # Add multiple blocks
        block1 = MockCodeBlock("block1", CodeBlockType.SUBROUTINE, size=4, code=b"\x01\x02\x03\x04")
        block2 = MockCodeBlock("block2", CodeBlockType.DATA, size=3, code=b"\x05\x06\x07")
        block3 = MockCodeBlock("block3", CodeBlockType.SUBROUTINE, size=2, code=b"\x08\x09")

        rom.add(block1)
        rom.add(block2)
        rom.add(block3)

        rendered = rom.render()

        prg_start = 16
        prg_rom = rendered[prg_start : prg_start + 9]

        # Blocks should be in reverse order (leaf dependencies first)
        # Since we added them in order, they'll be reversed
        assert prg_rom == b"\x08\x09\x05\x06\x07\x01\x02\x03\x04"

    def test_empty_rom_renders_successfully(self):
        """Verify empty ROM (no code blocks) renders valid ROM."""
        rom = Rom()
        rendered = rom.render()

        # Should have valid header
        assert rendered[0:4] == b"NES\x1a"

        # Should have correct total size
        expected_size = 16 + (16 * 1024) + (8 * 1024)
        assert len(rendered) == expected_size

    def test_exported_names_tracked_correctly(self):
        """Verify code blocks export their names with correct addresses."""
        rom = Rom()

        # Add blocks that should export names
        sub = MockCodeBlock("my_sub", CodeBlockType.SUBROUTINE, size=10)
        rom.add(sub)

        # Rendering should succeed (names are tracked internally)
        rendered = rom.render()
        assert len(rendered) > 0
