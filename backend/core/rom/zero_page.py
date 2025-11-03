from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock


class ZeroPageVariable(CodeBlock):
    """
    The built-in zero page variable code block.

    - allocates a zero page variable for use by the ROM
    """
    type: CodeBlockType = CodeBlockType.ZEROPAGE

    @property
    def dependencies(self) -> list[str]:
        return []

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = b""  # Zero page variables do not generate code
        return RenderedCodeBlock(code=code, exported_labels={self.label: start_offset})


class ZeroPageWord(ZeroPageVariable):
    """
    A zero page variable that is a word (2 bytes).
    """

    @property
    def size(self) -> int:
        return 2


class ZeroPageSource1(ZeroPageWord):
    """
    A generic source vector for indirect loading via the zero page.
    """
    label: str = "zp__src1"


class ZeroPageSource2(ZeroPageWord):
    """
    A generic source vector for indirect loading via the zero page.
    """
    label: str = "zp__src2"


class ZeroPageByte(ZeroPageVariable):
    """
    A zero page variable that is a single byte.
    """

    @property
    def size(self) -> int:
        return 1


class ZeroPageEntityRAM(ZeroPageByte):
    """
    Pointer to the RAM page ($0200-$02FF) where entity data is loaded.
    This is the high byte of the address; the low byte is the entity index * ENTITY_SIZE_BYTES.
    """
    label: str = "zp__entity_ram_page"


class ZeroPageSpriteRAM(ZeroPageByte):
    """
    Pointer to the RAM page ($0300-$03FF) where sprite data (OAM) is assembled.
    This is the high byte of the address used for DMA transfer to PPU OAM.
    """
    label: str = "zp__sprite_ram_page"
