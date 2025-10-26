

from core.rom.code_block import CodeBlock, CodeBlockType
from pydantic import BaseModel, Field


def _empty_code_blocks_factory() -> dict[CodeBlockType, dict[str, CodeBlock]]:
    return {
        CodeBlockType.ZEROPAGE: {},
        CodeBlockType.PREAMBLE: {},
        CodeBlockType.VBLANK: {},
        CodeBlockType.UPDATE: {},
        CodeBlockType.SUBROUTINE: {},
        CodeBlockType.DATA: {},
    }

class Rom(BaseModel):
    code_blocks: dict[CodeBlockType, dict[str, CodeBlock]] = Field(default_factory=_empty_code_blocks_factory)

    def add(self, code_block: CodeBlock) -> None:
        self.code_blocks[code_block.type][code_block.name] = code_block

    def render(self) -> bytes:
        return b""  # TODO: implement ROM rendering logic