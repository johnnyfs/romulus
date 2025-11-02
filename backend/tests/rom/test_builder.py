from unittest.mock import Mock

import pytest

from core.rom.builder import RomBuilder
from core.rom.code_block import CodeBlock, CodeBlockType, RenderedCodeBlock
from core.rom.preamble import PreambleCodeBlock
from core.rom.code_block_registry import CodeBlockRegistry
from core.rom.rom import Rom, RomCodeArea
from core.rom.subroutines import LoadSceneSubroutine


class TrackingRom(Rom):
    """
    Rom wrapper that tracks additions for testing.

    We can't patch Rom.add directly because Pydantic models don't allow
    attribute assignment. Instead, we subclass and track in a separate list.
    """

    def __init__(self, **data):
        super().__init__(**data)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, "add_order", [])
        object.__setattr__(self, "add_count", {})

    def add(self, code_block: CodeBlock) -> None:
        self.add_order.append(code_block.label)
        self.add_count[code_block.label] = self.add_count.get(code_block.label, 0) + 1
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
    def label(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return 10

    @property
    def dependencies(self) -> list[str]:
        return self._dependencies

    def render(self, start_offset: int, names: dict[str, int]) -> RenderedCodeBlock:
        return RenderedCodeBlock(code=b"\x00" * 10, exported_labels={})


class TestRomBuilder:
    """Tests for the ROM builder dependency resolution with new registry pattern."""

    def test_adds_code_block_with_no_dependencies(self):
        """Verify that a code block with no dependencies is added directly."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        block = MockCodeBlock("simple_block", dependencies=[])
        builder._add(rom, block)

        # Should be in the ROM (SUBROUTINE type maps to PRG_ROM area)
        assert "simple_block" in rom.code_blocks[RomCodeArea.PRG_ROM]
        assert rom.code_blocks[RomCodeArea.PRG_ROM]["simple_block"] is block

        # Should be in the registry
        assert "simple_block" in registry

    def test_adds_dependencies_before_code_block(self):
        """Verify that dependencies are added before the code block itself."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Add a block that depends on zp__src1 (which is in DEFAULT_REGISTRY)
        block = MockCodeBlock("dependent_block", dependencies=["zp__src1"])
        builder._add(rom, block)

        # zp__src1 should be added before dependent_block
        assert rom.add_order.index("zp__src1") < rom.add_order.index("dependent_block")

    def test_recursively_adds_transitive_dependencies(self):
        """Verify that transitive dependencies are resolved depth-first."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Create a chain: block_c -> block_b -> block_a
        block_a = MockCodeBlock("block_a", dependencies=[])
        block_b = MockCodeBlock("block_b", dependencies=["block_a"])
        block_c = MockCodeBlock("block_c", dependencies=["block_b"])

        # Add blocks to registry
        registry.add_code_block(block_a)
        registry.add_code_block(block_b)

        # Add block_c
        builder._add(rom, block_c)

        # Should add in order: block_a, block_b, block_c (depth-first)
        assert rom.add_order == ["block_a", "block_b", "block_c"]

    def test_adds_multiple_dependencies_in_order(self):
        """Verify that multiple dependencies are added in the order listed."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Add a block that depends on both zp__src1 and zp__src2
        block = MockCodeBlock("multi_dep_block", dependencies=["zp__src1", "zp__src2"])
        builder._add(rom, block)

        # Dependencies should be added in order, then the block itself
        assert rom.add_order == ["zp__src1", "zp__src2", "multi_dep_block"]

    def test_raises_on_unknown_dependency(self):
        """Verify that unknown dependencies raise a KeyError."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Create a block with an unknown dependency
        block = MockCodeBlock("bad_block", dependencies=["unknown_dep"])

        # Should raise KeyError from registry
        with pytest.raises(KeyError, match="Code block 'unknown_dep' not found"):
            builder._add(rom, block)

    def test_registry_adds_code_block_directly(self):
        """Verify that registry can add code blocks directly and look them up."""
        registry = CodeBlockRegistry()

        # Add a mock code block directly (not via component)
        block = MockCodeBlock("test_block", dependencies=[])
        registry.add_code_block(block)

        # Should be able to look up by name
        assert "test_block" in registry
        retrieved_block = registry["test_block"]
        assert retrieved_block.label == "test_block"
        assert retrieved_block is block

    def test_registry_has_default_blocks(self):
        """Verify that registry comes with default blocks (zp vars, subroutines)."""
        registry = CodeBlockRegistry()

        # Should have default zero page variables
        assert "zp__src1" in registry
        assert "zp__src2" in registry

        # Should have default subroutines
        assert "load_scene" in registry

        # Can retrieve them
        zp_src1 = registry["zp__src1"]
        assert zp_src1.label == "zp__src1"

    def test_scene_with_palette_reference_added_before_palette(self):
        """
        CRITICAL TEST: Verify that a scene referencing a palette can be added
        before the palette itself, because the registry pre-populates all components.

        This tests the key feature of the registry: pre-generating all component
        code blocks so dependencies can be resolved regardless of add order.
        """
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Create a palette code block and add to registry directly
        # (simulating what would happen when registry.add_components() is called)
        palette_block = MockCodeBlock("bg_palette", dependencies=[], block_type=CodeBlockType.DATA)
        registry.add_code_block(palette_block)

        # Create a scene block that references the palette
        # In the real SceneData implementation, this would have "bg_palette" in its dependencies
        scene_block = MockCodeBlock(
            "scene_data__main",
            dependencies=["bg_palette"],  # Scene references palette by name
            block_type=CodeBlockType.DATA,
        )

        # Add scene BEFORE we would iterate over components in build()
        # This should work because registry already has "bg_palette"
        builder._add(rom, scene_block)

        # Verify the palette was added first (dependency resolution)
        assert rom.add_order.index("bg_palette") < rom.add_order.index("scene_data__main")

        # Verify both are in ROM (DATA type maps to PRG_ROM area)
        assert "bg_palette" in rom.code_blocks[RomCodeArea.PRG_ROM]
        assert "scene_data__main" in rom.code_blocks[RomCodeArea.PRG_ROM]

    def test_preamble_adds_all_dependencies(self):
        """Integration test: verify preamble adds zp__src1, scene_data, and load_scene."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Add mock scene data to registry (preamble depends on it)
        scene_data = MockCodeBlock("scene_data__main", dependencies=[], block_type=CodeBlockType.DATA)
        registry.add_code_block(scene_data)

        # Add preamble
        preamble = PreambleCodeBlock()
        preamble.main_scene_name = "main"
        builder._add(rom, preamble)

        # Should add dependencies first (in depth-first order)
        assert "zp__src1" in rom.add_order
        assert "load_scene" in rom.add_order
        assert "scene_data__main" in rom.add_order
        assert "preamble" in rom.add_order

        # Dependencies should come before preamble
        assert rom.add_order.index("zp__src1") < rom.add_order.index("preamble")
        assert rom.add_order.index("load_scene") < rom.add_order.index("preamble")
        assert rom.add_order.index("scene_data__main") < rom.add_order.index("preamble")

    def test_load_scene_subroutine_adds_zero_page_dependencies(self):
        """Verify load_scene subroutine adds its zero page dependencies first."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

        # Add load_scene
        load_scene = LoadSceneSubroutine()
        builder._add(rom, load_scene)

        # Should add zp__src1 and zp__src2 before load_scene
        assert rom.add_order.index("zp__src1") < rom.add_order.index("load_scene")
        assert rom.add_order.index("zp__src2") < rom.add_order.index("load_scene")

    def test_complex_dependency_tree_depth_first_order(self):
        """Verify complex dependency trees are traversed depth-first."""
        rom = TrackingRom()
        registry = CodeBlockRegistry()
        builder = RomBuilder(db=Mock(), rom=rom, code_block_registry=registry)

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

        registry.add_code_block(c)
        registry.add_code_block(a)
        registry.add_code_block(d)
        registry.add_code_block(e)
        registry.add_code_block(b)

        builder._add(rom, root)

        # Depth-first order: C, A, D, E, B, root
        assert rom.add_order == ["C", "A", "D", "E", "B", "root"]
