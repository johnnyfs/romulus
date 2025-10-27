# ROM Assembly - End-to-End Logic

This document explains how Romulus assembles NES ROMs from game data, code blocks, and dependencies.

## Overview

Romulus builds NES ROMs in iNES format by:
1. Collecting code blocks (data, subroutines, preamble) from game components
2. Resolving dependencies to ensure correct ordering
3. Rendering code blocks to 6502 machine code
4. Assembling into a valid NES ROM with proper memory layout

## Architecture Components

### Code Block Types (`CodeBlockType`)
Represents the **kind** of code:
- `ZEROPAGE` - Zero page RAM variables ($00-$FF)
- `PREAMBLE` - Reset/initialization code
- `VBLANK` - Code executed during VBlank
- `UPDATE` - Code executed after VBlank (post-vblank)
- `SUBROUTINE` - Callable subroutines
- `DATA` - Read-only data (palettes, scenes, etc.)

### ROM Code Areas (`RomCodeArea`)
Represents **where** code is placed in the ROM:
- `ZEROPAGE` - RAM at $00-$FF (not in ROM, but addresses tracked)
- `RESET` - Reset vector code
- `NMI_VBLANK` - VBlank NMI handler
- `NMI_POST_VBLANK` - Post-VBlank code (runs before VBlank handler)
- `PRG_ROM` - General program code and data ($C000-$FFF9)

**Key insight:** Both `DATA` and `SUBROUTINE` types map to `PRG_ROM` area. This allows data and code to be interleaved based on dependency order.

### Code Blocks
Base class: `CodeBlock` (in [core/rom/code_block.py](../../backend/core/rom/code_block.py))

Each code block provides:
- `name` - Unique identifier
- `type` - CodeBlockType
- `size` - Size in bytes
- `dependencies` - List of other block names this depends on
- `render(start_offset, names)` - Generates machine code

Examples:
- `PaletteData` - Palette color indices ([core/rom/data.py](../../backend/core/rom/data.py:43))
- `SceneData` - Scene configuration (bg color, palette pointers) ([core/rom/data.py](../../backend/core/rom/data.py:81))
- `AddressData` - 2-byte pointer to another block ([core/rom/data.py](../../backend/core/rom/data.py:6))
- `LoadSceneSubroutine` - Loads scene into PPU ([core/rom/subroutines.py](../../backend/core/rom/subroutines.py))
- `PreambleCodeBlock` - CPU/PPU initialization ([core/rom/preamble.py](../../backend/core/rom/preamble.py))

## Build Process

### 1. Component Registration ([core/rom/registry.py](../../backend/core/rom/registry.py))

```python
registry = CodeBlockRegistry()
registry.add_components(game.components)
```

The registry:
- Pre-generates all code blocks from components
- Caches by component ID and by block name
- Enables forward references (scenes can reference palettes not yet added)

**Default registry includes:**
- Zero page variables (`zp__src1`, `zp__src2`)
- Core subroutines (`load_scene`)

### 2. Dependency Resolution ([core/rom/builder.py](../../backend/core/rom/builder.py))

```python
def _add(rom: Rom, code_block: CodeBlock):
    # Depth-first traversal
    for dependency_name in code_block.dependencies:
        dependency = registry[dependency_name]
        _add(rom, dependency)  # Recursive
    rom.add(code_block)
```

**Algorithm:** Depth-first dependency resolution
- Visit each dependency before adding the block itself
- Ensures leaf dependencies are added first
- Example: `preamble` depends on `load_scene` depends on `zp__src1`
  - Order: `zp__src1`, `zp__src2`, `load_scene`, `preamble`

**Key feature:** Idempotent - adding the same block twice does nothing

### 3. ROM Rendering ([core/rom/rom.py](../../backend/core/rom/rom.py:47))

The `Rom.render()` method assembles the final ROM:

#### Step 1: Zero Page Allocation
```python
zp_offset = 0x00
for block in code_blocks[ZEROPAGE].values():
    rendered = block.render(start_offset=zp_offset, names=names)
    names.update(rendered.exported_names)  # Track addresses
    zp_offset += block.size

if zp_offset > 256:
    raise ValueError("Zero page overflow")
```

- Allocates zero page RAM variables ($00-$FF)
- Validates total size ≤ 256 bytes
- Tracks variable addresses in `names` dict
- Zero page code is **not** included in ROM (it's RAM)

#### Step 2: PRG ROM Block Assembly
```python
prg_rom_start = 0xC000
prg_blocks = list(code_blocks[PRG_ROM].values())
prg_blocks.reverse()  # Leaf dependencies first

prg_offset = prg_rom_start
for block in prg_blocks:
    rendered = block.render(start_offset=prg_offset, names=names)
    prg_code.extend(rendered.code)
    names.update(rendered.exported_names)
    prg_offset += block.size
```

- PRG ROM starts at $C000 (mapper 0, second 16KB bank)
- **Reverses block order** to place leaf dependencies first
- Concatenates all `DATA` and `SUBROUTINE` blocks
- Each block renders with knowledge of previously rendered names

**Why reverse?** Dependencies were added in dependency order (roots last). Reversing puts leaves (no dependencies) first, roots last.

#### Step 3: NMI Routine Assembly
```python
nmi_offset = prg_offset
nmi_start_offset = nmi_offset

# Post-VBlank code first
for block in code_blocks[NMI_POST_VBLANK].values():
    rendered = block.render(start_offset=nmi_offset, names=names)
    nmi_code.extend(rendered.code)
    nmi_offset += block.size

# VBlank code second
for block in code_blocks[NMI_VBLANK].values():
    rendered = block.render(start_offset=nmi_offset, names=names)
    nmi_code.extend(rendered.code)
    nmi_offset += block.size

# RTI at end
nmi_code.append(0x40)  # RTI opcode
```

- NMI handler starts after PRG ROM blocks
- **Order matters:** Post-VBlank runs before VBlank handler
- Ends with RTI (Return from Interrupt) opcode
- `nmi_start_offset` cached for vector table

#### Step 4: Reset Routine
```python
reset_offset = nmi_offset
reset_start_offset = reset_offset

for block in code_blocks[RESET].values():
    rendered = block.render(start_offset=reset_offset, names=names)
    reset_code.extend(rendered.code)
    reset_offset += block.size
```

- Reset handler starts after NMI
- Contains preamble (initialization code)
- `reset_start_offset` cached for vector table

#### Step 5: Final ROM Assembly
```python
# Combine all PRG sections
full_prg = prg_code + nmi_code + reset_code

# Pad to vector table ($FFFA)
vectors_offset = 0xFFFA
padding_needed = (vectors_offset - prg_rom_start) - len(full_prg)
full_prg.extend(b'\x00' * padding_needed)

# Add interrupt vectors (little-endian)
full_prg.extend(nmi_start_offset.to_bytes(2, "little"))    # $FFFA: NMI
full_prg.extend(reset_start_offset.to_bytes(2, "little"))  # $FFFC: RESET
full_prg.extend(nmi_start_offset.to_bytes(2, "little"))    # $FFFE: IRQ (unused)

# iNES header
header = bytearray([
    0x4E, 0x45, 0x53, 0x1A,  # "NES" + EOF
    0x01,  # 1x 16KB PRG ROM
    0x01,  # 1x 8KB CHR ROM
    0x00,  # Mapper 0, horizontal mirroring
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

# Blank CHR ROM (8KB pattern tables)
chr_rom = bytes(8192)

# Final ROM
return bytes(header + full_prg + chr_rom)
```

**Memory Layout:**
```
ROM File:
├─ Header (16 bytes)
├─ PRG ROM (16KB = 16384 bytes)
│  ├─ $C000: PRG code/data blocks
│  ├─ ????: NMI handler
│  ├─ ????: RESET handler
│  ├─ $C000-$FFF9: Padding (zeros)
│  ├─ $FFFA-$FFFB: NMI vector
│  ├─ $FFFC-$FFFD: RESET vector
│  └─ $FFFE-$FFFF: IRQ vector
└─ CHR ROM (8KB = 8192 bytes)
   └─ All zeros (no graphics yet)
```

## Example: Building a ROM with Scene and Palette

### Input
Game with:
- 1 scene: "main" with background color $0F
- 1 palette: "bg_palette" with colors [$01, $02, $03]

### Code Blocks Generated

1. **PaletteData** (`palette_data__bg_palette`)
   - Type: DATA → PRG_ROM
   - Size: 3 bytes
   - Dependencies: []
   - Code: `01 02 03`

2. **SceneData** (`scene_data__main`)
   - Type: DATA → PRG_ROM
   - Size: 5 bytes
   - Dependencies: [`data__initial_scene`, `palette_data__bg_palette`]
   - Code: `0F XX XX 00 00` (bg color, bg pal ptr, sprite pal ptr)

3. **AddressData** (`data__initial_scene`)
   - Type: DATA → PRG_ROM
   - Size: 2 bytes
   - Dependencies: [`scene_data__main`]
   - Code: `XX XX` (pointer to scene_data__main)

4. **PreambleCodeBlock** (`preamble`)
   - Type: PREAMBLE → RESET
   - Dependencies: [`zp__src1`, `zp__src2`, `load_scene`, `data__initial_scene`]

5. **LoadSceneSubroutine** (`load_scene`)
   - Type: SUBROUTINE → PRG_ROM
   - Dependencies: [`zp__src1`, `zp__src2`]

6. **ZeroPageSource1** (`zp__src1`)
   - Type: ZEROPAGE
   - Size: 2 bytes
   - Dependencies: []

7. **ZeroPageSource2** (`zp__src2`)
   - Type: ZEROPAGE
   - Size: 2 bytes
   - Dependencies: []

### Dependency Resolution Order

Starting from `preamble`:
1. `zp__src1` (no deps)
2. `zp__src2` (no deps)
3. `load_scene` (deps: zp__src1, zp__src2 - already added)
4. `data__initial_scene` (deps: scene_data__main)
   - 5. `scene_data__main` (deps: data__initial_scene - creates cycle? No! See below)
      - 6. `palette_data__bg_palette` (no deps)
5. `data__initial_scene` (continues after scene_data__main)
4. `preamble` (all deps satisfied)

**Note:** `scene_data__main` depends on `data__initial_scene` for pointer resolution, but `data__initial_scene` depends on `scene_data__main` for the address. This is resolved by:
1. Adding `scene_data__main` first (address known)
2. Then adding `data__initial_scene` (can now render with scene address)

### Final ROM Structure

**Zero Page ($00-$FF):**
- $00-$01: zp__src1
- $02-$03: zp__src2

**PRG ROM ($C000+):**
```
$C000: palette_data__bg_palette (3 bytes): 01 02 03
$C003: scene_data__main (5 bytes): 0F 00 C0 00 00
       └─ BG color $0F
       └─ BG palette pointer $C000 (little-endian)
       └─ Sprite palette pointer $0000 (null)
$C008: data__initial_scene (2 bytes): 03 C0
       └─ Pointer to scene_data__main at $C003 (little-endian)
$C00A: load_scene subroutine (~100 bytes)
$C06E: NMI handler (RTI): 40
$C06F: preamble (~50 bytes)
...
$FFFA: NMI vector → $C06E
$FFFC: RESET vector → $C06F
$FFFE: IRQ vector → $C06E
```

## Testing

Comprehensive tests in [tests/rom/test_rom.py](../../backend/tests/rom/test_rom.py):

- ✅ iNES header format
- ✅ Total ROM size (16-byte header + 16KB PRG + 8KB CHR)
- ✅ Vector table placement ($FFFA-$FFFF)
- ✅ Zero page allocation and overflow detection
- ✅ PRG ROM block placement at $C000
- ✅ DATA blocks go to PRG_ROM
- ✅ NMI routine ends with RTI
- ✅ RESET vector points to preamble
- ✅ NMI_POST_VBLANK before NMI_VBLANK
- ✅ PRG overflow detection
- ✅ CHR ROM is blank 8KB
- ✅ Multiple PRG blocks concatenated in reverse order
- ✅ Empty ROM renders successfully

All 57 ROM tests passing as of this writing.

## Key Insights

1. **Separation of Concerns:** CodeBlockType (what) vs RomCodeArea (where)
2. **Dependency Resolution:** Depth-first ensures correct ordering
3. **Name Table:** `render()` uses `names` dict to resolve references
4. **Reversing PRG Blocks:** Counteracts dependency-first addition
5. **Forward References:** Registry pre-population enables scenes to reference palettes
6. **Idempotent Adds:** Same block can be added multiple times safely
7. **Little-Endian:** All 16-bit addresses are little-endian (6502 convention)
8. **Vector Table:** Must be at $FFFA-$FFFF for NES to boot

## Future Enhancements

- Support for more mappers (currently hardcoded to mapper 0)
- CHR ROM data (pattern tables for graphics)
- Multiple PRG banks (32KB+ ROMs)
- Nametable/attribute table data
- Sound/music code blocks
- Sprite OAM data
