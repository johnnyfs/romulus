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
