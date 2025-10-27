import uuid

from core.rom.code_block import CodeBlock
from core.rom.data import PaletteData
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource1, ZeroPageSource2
from core.schemas import ComponentType
from game.component.models import Component

DEFAULT_REGISTRY = {
    # Zero page
    "zp__src1": ZeroPageSource1(),
    "zp__src2": ZeroPageSource2(),
    # Subroutines
    "load_scene": LoadSceneSubroutine(),
}


def _to_code_blocks(component: Component) -> list[CodeBlock]:
    if component.component_data.type == ComponentType.PALETTE:
        return [PaletteData(_name=component.name, _palette_data=component.component_data)]
    else:
        raise ValueError(f"Unsupported component type: {component.component_data.type}")


class CodeBlockRegistry:
    def add_components(self, components: list[Component]):
        for component in components:
            code_blocks = _to_code_blocks(component)
            self._code_blocks_by_component_id[component.id] = code_blocks
            for code_block in code_blocks:
                self.add_code_block(code_block)

    def add_code_block(self, code_block: CodeBlock):
        self._code_blocks_by_name[code_block.name] = code_block

    def get_code_blocks(self, component: Component) -> list[CodeBlock]:
        return self._code_blocks_by_component_id.get(component.id, [])

    def __init__(self):
        self._code_blocks_by_component_id: dict[uuid.UUID, list[CodeBlock]] = {}
        self._code_blocks_by_name = DEFAULT_REGISTRY.copy()

    def __contains__(self, name: str) -> bool:
        return name in self._code_blocks_by_name

    def __getitem__(self, name: str) -> CodeBlock:
        if name not in self._code_blocks_by_name:
            raise KeyError(f"Code block '{name}' not found in registry.")
        return self._code_blocks_by_name[name]


def get_new_registry() -> CodeBlockRegistry:
    return CodeBlockRegistry()
