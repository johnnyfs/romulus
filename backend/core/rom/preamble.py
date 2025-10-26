
from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock


class PreambleCodeBlock(CodeBlock):
    """
    The built-in preamble code block that runs at the start of the ROM.

    - initializes the stack pointer
    - loads the first scene
    """

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.PREAMBLE

    @property
    def name(self) -> str:
        return "preamble"

    @property
    def size(self) -> int:
        raise NotImplementedError("TODO: implement size calculation")

    @property
    def dependencies(self) -> list[str]:
        return []

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = b""
        return RenderedCodeBlock(code=code, exported_names={})