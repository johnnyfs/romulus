import enum

from pydantic import BaseModel, Field

from core.rom.code_block import CodeBlock, CodeBlockType


class RomCodeArea(enum.Enum):
    """Code areas are different than code block types; they represent different sections of the ROM where code blocks can be placed."""

    ZEROPAGE = "ZEROPAGE"
    RESET = "RESET"
    NMI_VBLANK = "NMI_VBLANK"
    NMI_POST_VBLANK = "NMI_POST_VBLANK"
    PRG_ROM = "PRG_ROM"

    @classmethod
    def from_code_block_type(cls, code_block_type: CodeBlockType) -> "RomCodeArea":
        if code_block_type == CodeBlockType.ZEROPAGE:
            return RomCodeArea.ZEROPAGE
        elif code_block_type == CodeBlockType.PREAMBLE:
            return RomCodeArea.RESET
        elif code_block_type == CodeBlockType.VBLANK:
            return RomCodeArea.NMI_VBLANK
        elif code_block_type == CodeBlockType.UPDATE:
            return RomCodeArea.NMI_POST_VBLANK
        elif code_block_type in (CodeBlockType.SUBROUTINE, CodeBlockType.DATA):
            return RomCodeArea.PRG_ROM
        else:
            raise ValueError(f"Unsupported code block type: {code_block_type}")


def _empty_code_blocks_factory() -> dict[RomCodeArea, dict[str, CodeBlock]]:
    return {
        RomCodeArea.ZEROPAGE: {},
        RomCodeArea.RESET: {},
        RomCodeArea.NMI_VBLANK: {},
        RomCodeArea.NMI_POST_VBLANK: {},
        RomCodeArea.PRG_ROM: {},
    }


class Rom(BaseModel):
    code_blocks: dict[RomCodeArea, dict[str, CodeBlock]] = Field(default_factory=_empty_code_blocks_factory)

    def add(self, code_block: CodeBlock) -> None:
        self.code_blocks[RomCodeArea.from_code_block_type(code_block.type)][code_block.name] = code_block

    def render(self) -> bytes:
        """
        Renders the ROM by assembling all code blocks into a valid NES ROM.

        Algorithm:
        1. Zero page allocation: Add all ZEROPAGE blocks, building name table
        2. PRG ROM block: Add all PRG_ROM blocks in reverse order (leaf dependencies first)
        3. NMI routine: Assemble NMI_POST_VBLANK then NMI_VBLANK, cache NMI offset
        4. Reset routine: Add RESET blocks
        5. Final assembly: Combine all sections with vector table and CHR ROM
        """
        names: dict[str, int] = {}

        # Step 1: Zero page allocation
        zp_offset = 0x00
        zp_code = bytearray()

        for block in self.code_blocks[RomCodeArea.ZEROPAGE].values():
            rendered = block.render(start_offset=zp_offset, names=names)
            zp_code.extend(rendered.code)
            names.update(rendered.exported_names)
            zp_offset += block.size

        if zp_offset > 256:
            raise ValueError(f"Zero page allocation exceeds 256 bytes: {zp_offset} bytes used")

        # Step 2: PRG ROM block - add in reverse order
        # Start at beginning of 16KB PRG ROM ($C000 in second bank)
        prg_rom_start = 0xC000

        # Collect all PRG_ROM blocks
        prg_blocks = list(self.code_blocks[RomCodeArea.PRG_ROM].values())

        # Reverse the order to add leaf dependencies first
        prg_blocks.reverse()

        # Start PRG ROM at beginning of PRG ROM area
        prg_offset = prg_rom_start
        prg_code = bytearray()

        for block in prg_blocks:
            rendered = block.render(start_offset=prg_offset, names=names)
            prg_code.extend(rendered.code)
            names.update(rendered.exported_names)
            prg_offset += block.size

        # Step 3: NMI routine - post vblank first, then vblank
        nmi_code = bytearray()
        nmi_offset = prg_offset
        nmi_start_offset = nmi_offset

        # Add post vblank blocks
        for block in self.code_blocks[RomCodeArea.NMI_POST_VBLANK].values():
            rendered = block.render(start_offset=nmi_offset, names=names)
            nmi_code.extend(rendered.code)
            names.update(rendered.exported_names)
            nmi_offset += block.size

        # Add vblank blocks
        for block in self.code_blocks[RomCodeArea.NMI_VBLANK].values():
            rendered = block.render(start_offset=nmi_offset, names=names)
            nmi_code.extend(rendered.code)
            names.update(rendered.exported_names)
            nmi_offset += block.size

        # Add RTI to end NMI
        nmi_code.append(0x40)  # RTI opcode
        nmi_offset += 1

        # Step 4: Reset routine
        reset_code = bytearray()
        reset_offset = nmi_offset
        reset_start_offset = reset_offset

        for block in self.code_blocks[RomCodeArea.RESET].values():
            rendered = block.render(start_offset=reset_offset, names=names)
            reset_code.extend(rendered.code)
            names.update(rendered.exported_names)
            reset_offset += block.size

        # Step 5: Final assembly
        # Combine PRG ROM sections
        full_prg = prg_code + nmi_code + reset_code

        # Add vector table at end of PRG ROM ($FFFA-$FFFF)
        # Pad to reach vector table location
        vectors_offset = 0xFFFA
        padding_needed = (vectors_offset - prg_rom_start) - len(full_prg)

        if padding_needed < 0:
            raise ValueError(f"PRG ROM overflow: code is {-padding_needed} bytes too large")

        full_prg.extend(b"\x00" * padding_needed)

        # Add vectors: NMI, RESET, IRQ
        # NMI vector
        full_prg.extend(nmi_start_offset.to_bytes(2, "little"))
        # RESET vector
        full_prg.extend(reset_start_offset.to_bytes(2, "little"))
        # IRQ vector (unused, point to RTI)
        full_prg.extend(nmi_start_offset.to_bytes(2, "little"))

        # NES ROM header (iNES format)
        # See: https://www.nesdev.org/wiki/INES
        header = bytearray(
            [
                0x4E,
                0x45,
                0x53,
                0x1A,  # "NES" + MS-DOS EOF
                0x01,  # 1x 16KB PRG ROM
                0x01,  # 1x 8KB CHR ROM
                0x00,  # Mapper 0, horizontal mirroring
                0x00,  # Mapper 0 (continued)
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,  # Padding
            ]
        )

        # Blank CHR ROM (8KB of pattern tables)
        chr_rom = bytes(8192)

        # Final ROM: header + PRG ROM + CHR ROM
        return bytes(header + full_prg + chr_rom)


def get_empty_rom() -> Rom:
    return Rom()
