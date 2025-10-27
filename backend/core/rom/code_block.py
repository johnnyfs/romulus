import enum
from abc import abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel


class CodeBlockType(enum.Enum):
    """
    zeropage: a reserved zero page variable
    preamble: code that runs at the start of the ROM
    vblank: code that must run during the vertical blanking interval
    update: code that runs every frame
    subroutine: a callable subroutine
    data: raw data to be included in the ROM
    """

    ZEROPAGE = "ZEROPAGE"
    PREAMBLE = "PREAMBLE"
    VBLANK = "VBLANK"
    UPDATE = "UPDATE"
    SUBROUTINE = "SUBROUTINE"
    DATA = "DATA"


@dataclass
class RenderedCodeBlock:
    """
    Given a fixed start offset, the literal code plus a mapping of exported names to absolute addresses.
    """

    code: bytes
    exported_names: dict[str, int]


class CodeBlock(BaseModel):
    @property
    @abstractmethod
    def type(self) -> CodeBlockType:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @property
    @abstractmethod
    def dependencies(self) -> list[str]:
        pass

    @abstractmethod
    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        pass
