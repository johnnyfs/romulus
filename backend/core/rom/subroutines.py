from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.schemas import NESRef


class LoadSceneSubroutine(CodeBlock):
    """
    The built-in load scene subroutine code block.

    - loads a scene into memory
    """

    @property
    def type(self) -> CodeBlockType:
        return CodeBlockType.SUBROUTINE

    @property
    def name(self) -> str:
        return "load_scene"

    @property
    def size(self) -> int:
        raise NotImplementedError("TODO: implement size calculation")

    @property
    def dependencies(self) -> list[str]:
        return ["zp__src"]

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        code = b""
        return RenderedCodeBlock(code=code, exported_names={self.name: start_offset})