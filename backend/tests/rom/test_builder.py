import pytest
from unittest.mock import Mock

from core.rom.builder import RomBuilder
from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.rom.preamble import PreambleCodeBlock
from core.rom.rom import Rom
from core.rom.subroutines import LoadSceneSubroutine
from core.rom.zero_page import ZeroPageSource1, ZeroPageSource2


class TrackingRom(Rom):
    """
    Rom wrapper that tracks additions for testing.

    We can't patch Rom.add directly because Pydantic models don't allow
    attribute assignment. Instead, we subclass and track in a separate list.
    """

    def __init__(self, **data):
        super().__init__(**data)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'add_order', [])
        object.__setattr__(self, 'add_count', {})

    def add(self, code_block: CodeBlock) -> None:
        self.add_order.append(code_block.name)
        self.add_count[code_block.name] = self.add_count.get(code_block.name, 0) + 1
        super().add(code_block)


class MockCodeBlock(CodeBlock):
    """Mock code block for testing dependency resolution."""

    def __init__(self, name: str, dependencies: list[str] = None, block_type: CodeBlockType = CodeBlockType.SUBROUTINE):
        self._name = name
        self._dependencies = dependencies or []
        self._type = block_type

    @property
    def type(self) -> CodeBlockType:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return 10

    @property
    def dependencies(self) -> list[str]:
        return self._dependencies

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        return RenderedCodeBlock(code=b"\x00" * 10, exported_names={})


class TestRomBuilder:
    """Tests for the ROM builder dependency resolution."""

    def test_adds_code_block_with_no_dependencies(self):
        """Verify that a code block with no dependencies is added directly."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        block = MockCodeBlock("simple_block", dependencies=[])
        builder._add(rom, block)

        # Should be in the ROM
        assert "simple_block" in rom.code_blocks[CodeBlockType.SUBROUTINE]
        assert rom.code_blocks[CodeBlockType.SUBROUTINE]["simple_block"] is block

    def test_adds_dependencies_before_code_block(self):
        """Verify that dependencies are added before the code block itself."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Add a block that depends on zp__src1
        block = MockCodeBlock("dependent_block", dependencies=["zp__src1"])
        builder._add(rom, block)

        # zp__src1 should be added before dependent_block
        assert rom.add_order.index("zp__src1") < rom.add_order.index("dependent_block")

    def test_recursively_adds_transitive_dependencies(self):
        """Verify that transitive dependencies are resolved depth-first."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Create a chain: block_c -> block_b -> block_a
        block_a = MockCodeBlock("block_a", dependencies=[])
        block_b = MockCodeBlock("block_b", dependencies=["block_a"])
        block_c = MockCodeBlock("block_c", dependencies=["block_b"])

        # Add blocks to registry
        builder.registry["block_a"] = block_a
        builder.registry["block_b"] = block_b

        # Add block_c
        builder._add(rom, block_c)

        # Should add in order: block_a, block_b, block_c (depth-first)
        assert rom.add_order == ["block_a", "block_b", "block_c"]

    def test_adds_multiple_dependencies_in_order(self):
        """Verify that multiple dependencies are added in the order listed."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Add a block that depends on both zp__src1 and zp__src2
        block = MockCodeBlock("multi_dep_block", dependencies=["zp__src1", "zp__src2"])
        builder._add(rom, block)

        # Dependencies should be added in order, then the block itself
        assert rom.add_order == ["zp__src1", "zp__src2", "multi_dep_block"]

    def test_idempotent_add_does_not_duplicate(self):
        """Verify that adding the same block twice doesn't duplicate it in ROM."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Add zp__src1 dependency twice
        block_a = MockCodeBlock("block_a", dependencies=["zp__src1"])
        block_b = MockCodeBlock("block_b", dependencies=["zp__src1"])

        builder._add(rom, block_a)
        builder._add(rom, block_b)

        # zp__src1 should be added twice (once for each dependency)
        # but only one copy should exist in ROM
        assert rom.add_count["zp__src1"] == 2

        # Only one copy should be in ROM (dict overwrites)
        assert "zp__src1" in rom.code_blocks[CodeBlockType.ZEROPAGE]

        # Both blocks should be added
        assert "block_a" in rom.code_blocks[CodeBlockType.SUBROUTINE]
        assert "block_b" in rom.code_blocks[CodeBlockType.SUBROUTINE]

    def test_raises_on_unknown_dependency(self):
        """Verify that unknown dependencies raise a ValueError."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Create a block with an unknown dependency
        block = MockCodeBlock("bad_block", dependencies=["unknown_dep"])

        # Should raise ValueError
        with pytest.raises(ValueError, match="Unknown dependency: unknown_dep"):
            builder._add(rom, block)

    def test_preamble_adds_all_dependencies(self):
        """Integration test: verify preamble adds zp__src1 and load_scene."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Add mock scene data to registry (preamble depends on it)
        scene_data = MockCodeBlock("scene_data__main", dependencies=[], block_type=CodeBlockType.DATA)
        builder.registry["scene_data__main"] = scene_data

        # Add preamble
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"
        builder._add(rom, preamble)

        # Should add dependencies first (in depth-first order)
        # load_scene depends on zp__src1 and zp__src2
        assert "zp__src1" in rom.add_order
        assert "load_scene" in rom.add_order
        assert "scene_data__main" in rom.add_order
        assert "preamble" in rom.add_order

        # Dependencies should come before preamble
        assert rom.add_order.index("zp__src1") < rom.add_order.index("preamble")
        assert rom.add_order.index("load_scene") < rom.add_order.index("preamble")
        assert rom.add_order.index("scene_data__main") < rom.add_order.index("preamble")

        # load_scene's dependencies should come before load_scene
        if "zp__src2" in rom.add_order:
            assert rom.add_order.index("zp__src1") < rom.add_order.index("load_scene")
            assert rom.add_order.index("zp__src2") < rom.add_order.index("load_scene")

    def test_load_scene_subroutine_adds_zero_page_dependencies(self):
        """Verify load_scene subroutine adds its zero page dependencies first."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Add load_scene
        load_scene = LoadSceneSubroutine()
        builder._add(rom, load_scene)

        # Should add zp__src1 and zp__src2 before load_scene
        assert rom.add_order.index("zp__src1") < rom.add_order.index("load_scene")
        assert rom.add_order.index("zp__src2") < rom.add_order.index("load_scene")

    def test_diamond_dependency_only_adds_once_to_rom(self):
        """Verify diamond dependencies (A->B,C; B->D; C->D) only have one D in ROM."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Create diamond: top -> left, right; left -> bottom; right -> bottom
        bottom = MockCodeBlock("bottom", dependencies=[])
        left = MockCodeBlock("left", dependencies=["bottom"])
        right = MockCodeBlock("right", dependencies=["bottom"])
        top = MockCodeBlock("top", dependencies=["left", "right"])

        builder.registry["bottom"] = bottom
        builder.registry["left"] = left
        builder.registry["right"] = right

        # Add top
        builder._add(rom, top)

        # All blocks should be in ROM
        assert "bottom" in rom.code_blocks[CodeBlockType.SUBROUTINE]
        assert "left" in rom.code_blocks[CodeBlockType.SUBROUTINE]
        assert "right" in rom.code_blocks[CodeBlockType.SUBROUTINE]
        assert "top" in rom.code_blocks[CodeBlockType.SUBROUTINE]

        # bottom is added twice (once per path), but only one copy in ROM
        assert rom.add_count["bottom"] == 2

    def test_complex_dependency_tree_depth_first_order(self):
        """Verify complex dependency trees are traversed depth-first."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        # Create tree:
        #       root
        #      /    \
        #     A      B
        #    /      / \
        #   C      D   E

        c = MockCodeBlock("C", dependencies=[])
        a = MockCodeBlock("A", dependencies=["C"])
        d = MockCodeBlock("D", dependencies=[])
        e = MockCodeBlock("E", dependencies=[])
        b = MockCodeBlock("B", dependencies=["D", "E"])
        root = MockCodeBlock("root", dependencies=["A", "B"])

        builder.registry["C"] = c
        builder.registry["A"] = a
        builder.registry["D"] = d
        builder.registry["E"] = e
        builder.registry["B"] = b

        builder._add(rom, root)

        # Depth-first order: C, A, D, E, B, root
        assert rom.add_order == ["C", "A", "D", "E", "B", "root"]

    def test_adds_code_block_to_registry_after_adding(self):
        """Verify that code blocks are added to the registry after being added to ROM."""
        rom = TrackingRom()
        builder = RomBuilder(db=Mock(), rom=rom)

        block = MockCodeBlock("new_block", dependencies=[])

        # Should not be in registry yet
        assert "new_block" not in builder.registry

        # Add the block
        builder._add(rom, block)

        # Should now be in registry
        assert "new_block" in builder.registry
        assert builder.registry["new_block"] is block
