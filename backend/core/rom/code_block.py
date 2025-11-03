import enum
from abc import abstractmethod
from dataclasses import dataclass
import uuid

from pydantic import BaseModel


class CodeBlockType(enum.Enum):
    """
    zeropage: a reserved zero page variable
    preamble: code that runs at the start of the ROM
    vblank: code that must run during the vertical blanking interval
    update: code that runs every frame
    subroutine: a callable subroutine
    data: raw data to be included in the ROM
    chr: CHR-ROM tile data (sprite/background graphics)
    """

    ZEROPAGE = "ZEROPAGE"
    PREAMBLE = "PREAMBLE"
    VBLANK = "VBLANK"
    UPDATE = "UPDATE"
    SUBROUTINE = "SUBROUTINE"
    DATA = "DATA"
    CHR = "CHR"


@dataclass
class RenderedCodeBlock:
    """
    Given a fixed start offset, the literal code plus a mapping of exported names to absolute addresses.
    """

    code: bytes
    exported_labels: dict[str, int]


class CodeBlock(BaseModel):
    label: str
    type: CodeBlockType

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @property
    @abstractmethod
    def dependencies(self) -> list[str]:
        pass

    @property
    def optional_dependencies(self) -> list[str]:
        """Optional dependencies that are added if available but don't cause failure if missing."""
        return []

    @abstractmethod
    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        pass
