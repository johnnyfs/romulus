from core.rom.asm import Asm6502
from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock


class LoadSceneSubroutine(CodeBlock):
    """
    The built-in load scene subroutine code block.

    Loads a scene's palette data into PPU memory:
    1. Load background color (byte 0) into palette index 0
    2. Load background palette data (12 bytes) if pointer is non-null
    3. Load sprite palette data (12 bytes) if pointer is non-null
    4. Enable PPU rendering and NMI

    Scene data format (pointed to by zp__src1):
      Offset 0: Background color index (1 byte)
      Offset 1-2: Background palette data pointer (2 bytes, little-endian, 0 = null)
      Offset 3-4: Sprite palette data pointer (2 bytes, little-endian, 0 = null)
    """

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.SUBROUTINE

    @property
    def name(self) -> str:
        return "load_scene"

    @property
    def size(self) -> int:
        # Pre-calculate by building the code once
        asm = self._build_code(
            start_offset=0x8000,
            names={
                "zp__src1": 0x00,
                "zp__src2": 0x02,
            },
        )
        return len(asm)

    @property
    def dependencies(self) -> list[str]:
        return ["zp__src1", "zp__src2"]

    def _build_code(self, start_offset: int, names: dict[str, int]) -> bytes:
        """Build the load_scene subroutine assembly code."""
        asm = Asm6502()

        zp_src1 = names["zp__src1"]
        zp_src2 = names["zp__src2"]

        PPU_ADDR = 0x2006
        PPU_DATA = 0x2007
        PPU_CTRL = 0x2000
        PPU_MASK = 0x2001
        PALETTE_BASE = 0x3F00

        # === Wait for PPU to be ready ===
        # Read PPU status to clear address latch
        asm.bit_abs(0x2002)  # PPUSTATUS

        # === Set PPU address to palette RAM ($3F00) ===
        asm.lda_imm(0x3F)
        asm.sta_abs(PPU_ADDR)
        asm.lda_imm(0x00)
        asm.sta_abs(PPU_ADDR)

        # === Load background color (byte 0 of scene data) ===
        # Load Y=0 for indexed addressing
        asm.ldy_imm(0)
        # Load background color via (zp__src1),Y
        asm.lda_ind_y(zp_src1)
        # Write to PPU_DATA (palette index 0)
        asm.sta_abs(PPU_DATA)

        # === Load background palette pointer (bytes 1-2) ===
        asm.ldy_imm(1)
        asm.lda_ind_y(zp_src1)  # Low byte
        asm.sta_zp(zp_src2)
        asm.iny()
        asm.lda_ind_y(zp_src1)  # High byte
        asm.sta_zp(zp_src2 + 1)

        # Check if background palette pointer is null (both bytes == 0)
        asm.ora_imm(0)  # Set Z flag if A == 0
        skip_bg_offset = len(asm) + 2  # BNE takes 2 bytes
        # We'll calculate the actual offset after writing the BG palette code
        bg_palette_start = len(asm)

        # Placeholder for BEQ (skip if null) - we'll fix this up
        asm.beq(0)  # Will be patched
        beq_fixup_pos = len(asm) - 1

        # === Load 12 bytes of background palette data ===
        # Y is already at the right index after loading pointer
        asm.ldy_imm(0)
        # Loop 12 times
        for i in range(12):
            asm.lda_ind_y(zp_src2)
            asm.sta_abs(PPU_DATA)
            if i < 11:  # Don't increment on last iteration
                asm.iny()

        # Calculate skip offset for BEQ
        # BEQ offset is relative to the PC of the instruction AFTER the BEQ
        # beq_fixup_pos points to the offset byte, so PC after BEQ = beq_fixup_pos + 1
        bg_palette_end = len(asm)
        skip_bg_bytes = bg_palette_end - beq_fixup_pos - 1
        # Fix up the BEQ instruction
        asm._code[beq_fixup_pos] = skip_bg_bytes & 0xFF

        # === Load sprite palette pointer (bytes 3-4) ===
        asm.ldy_imm(3)
        asm.lda_ind_y(zp_src1)  # Low byte
        asm.sta_zp(zp_src2)
        asm.iny()
        asm.lda_ind_y(zp_src1)  # High byte
        asm.sta_zp(zp_src2 + 1)

        # Check if sprite palette pointer is null
        asm.ora_imm(0)
        sprite_palette_start = len(asm)

        # Placeholder for BEQ (skip if null)
        asm.beq(0)  # Will be patched
        beq_sprite_fixup_pos = len(asm) - 1

        # === Load 12 bytes of sprite palette data ===
        asm.ldy_imm(0)
        for i in range(12):
            asm.lda_ind_y(zp_src2)
            asm.sta_abs(PPU_DATA)
            if i < 11:
                asm.iny()

        # Fix up sprite palette BEQ
        # Same calculation as BG palette above
        sprite_palette_end = len(asm)
        skip_sprite_bytes = sprite_palette_end - beq_sprite_fixup_pos - 1
        asm._code[beq_sprite_fixup_pos] = skip_sprite_bytes & 0xFF

        # === Enable PPU and NMI ===
        # PPUCTRL: Enable NMI, background pattern table at $0000, sprites at $1000
        asm.lda_imm(0x80)  # %10000000 = NMI enabled
        asm.sta_abs(PPU_CTRL)

        # PPUMASK: Enable background and sprite rendering
        asm.lda_imm(0x1E)  # %00011110 = show bg, show sprites, show leftmost 8px
        asm.sta_abs(PPU_MASK)

        # === Return from subroutine ===
        asm.rts()

        return asm.bytes()

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = self._build_code(start_offset, names)
        return RenderedCodeBlock(code=code, exported_names={self.name: start_offset})
