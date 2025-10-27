from core.rom.asm import Asm6502
from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock


class PreambleCodeBlock(CodeBlock):
    """
    The built-in preamble code block that runs at the start of the ROM.

    Initialization sequence:
    1. Disable interrupts (SEI)
    2. Clear decimal mode (CLD)
    3. Disable NMI by writing to PPU control register
    4. Initialize stack pointer to 0xFF
    5. Zero out all CPU registers (A, X, Y)
    6. Load initial scene address into zero page
    7. Call load_scene subroutine
    8. Loop forever (main game loop will be in NMI handler)
    """

    _main_scene_name: str = "main"

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.PREAMBLE

    @property
    def name(self) -> str:
        return "preamble"

    @property
    def size(self) -> int:
        # Pre-calculate by building the code once
        # This is called during layout, so we use dummy addresses
        asm = self._build_code(
            start_offset=0x8000,
            names={
                "zp__src1": 0x00,
                f"scene_data__{self._main_scene_name}": 0x8000,
                "load_scene": 0x8000,
            },
        )
        return len(asm)

    @property
    def dependencies(self) -> list[str]:
        return ["zp__src1", f"scene_data__{self._main_scene_name}", "load_scene"]

    def _build_code(self, start_offset: int, names: dict[str, int]) -> bytes:
        """Build the preamble assembly code."""
        asm = Asm6502()

        # === NES Initialization ===
        # Disable interrupts during setup
        asm.sei()

        # Clear decimal mode (not used on NES, but good practice)
        asm.cld()

        # Disable NMI by writing 0 to PPU control register ($2000)
        asm.lda_imm(0x00)
        asm.sta_abs(0x2000)  # PPUCTRL

        # Initialize stack pointer to 0xFF (top of stack)
        asm.ldx_imm(0xFF)
        asm.txs()

        # Zero out all CPU registers
        asm.lda_imm(0x00)
        asm.tax()  # X = 0
        asm.tay()  # Y = 0
        # A is already 0

        # === Load Initial Scene ===
        # Load the address of the initial scene data into zero page variable zp__src1
        scene_data_addr = names[f"scene_data__{self._main_scene_name}"]
        zp_src_addr = names["zp__src1"]

        # Load low byte of scene data address
        asm.lda_imm(scene_data_addr & 0xFF)
        asm.sta_zp(zp_src_addr)

        # Load high byte of scene data address
        asm.lda_imm((scene_data_addr >> 8) & 0xFF)
        asm.sta_zp(zp_src_addr + 1)

        # Call the load_scene subroutine
        load_scene_addr = names["load_scene"]
        asm.jsr(load_scene_addr)

        # === Draw test tile to screen ===
        # Draw tile 0 (our test pattern) at nametable position (0, 0)
        # Nametable 0 starts at $2000

        # Wait for PPU to be ready
        asm.bit_abs(0x2002)  # Read PPUSTATUS to clear address latch

        # Set PPU address to nametable 0 position (0,0) = $2000
        asm.lda_imm(0x20)
        asm.sta_abs(0x2006)  # PPUADDR high byte
        asm.lda_imm(0x00)
        asm.sta_abs(0x2006)  # PPUADDR low byte

        # Fill more of the screen with the test tile for visibility
        # Draw an 8x8 grid of the test tile (64 tiles total)
        asm.ldx_imm(64)  # Counter for 64 tiles
        # Loop starts here
        loop_start = start_offset + len(asm)
        asm.lda_imm(0x00)  # Tile 0 (our test pattern)
        asm.sta_abs(0x2007)  # PPUDATA
        asm.dex()
        # Calculate relative offset for BNE
        # BNE branches to loop_start, and the branch is relative to PC after BNE instruction
        # We need to emit the BNE instruction first to know its position
        current_pos = len(asm)
        # BNE takes 2 bytes, so PC after BNE will be at current_pos + 2
        # Relative offset = target - (current_pos + 2)
        relative_offset = loop_start - (start_offset + current_pos + 2)
        asm.bne(relative_offset)

        # === Main Loop ===
        # Infinite loop (actual game logic runs in NMI handler)
        # Jump to current address (infinite loop)
        loop_addr = start_offset + len(asm)
        asm.jmp_abs(loop_addr)

        return asm.bytes()

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = self._build_code(start_offset, names)
        return RenderedCodeBlock(code=code, exported_names={})
