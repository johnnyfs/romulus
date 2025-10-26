from dataclasses import dataclass
from core.rom.code_block import CodeBlock
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource1, ZeroPageSource2
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_REGISTRY = {
    # Zero page
    "zp__src1": ZeroPageSource1(),
    "zp__src2": ZeroPageSource2(),

    # Subroutines
    "load_scene": LoadSceneSubroutine(),
}

class CodeBlockRegistry(BaseModel):
    code_blocks: dict[str, CodeBlock] = Field(default_factory=lambda: DEFAULT_REGISTRY.copy())

    _session: AsyncSession
    
