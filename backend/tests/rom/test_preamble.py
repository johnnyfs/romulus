from core.rom.preamble import PreambleCodeBlock
from tests.rom.helpers import (
    MemoryObserver,
    create_test_cpu,
)


class TestPreambleCodeBlock:
    """Tests for the NES preamble initialization code."""

    def test_disables_interrupts_and_decimal_mode(self):
        """Verify that SEI and CLD are executed at the start."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": 0x10,
                "scene_data__main": 0x9000,
                "load_scene": 0xA000,
            },
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Execute first few instructions
        cpu.step()  # SEI
        assert cpu.p & cpu.INTERRUPT != 0  # Interrupt flag should be set

        cpu.step()  # CLD
        assert cpu.p & cpu.DECIMAL == 0  # Decimal flag should be clear

    def test_disables_nmi_via_ppuctrl(self):
        """Verify that NMI is disabled by writing 0x00 to PPUCTRL."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": 0x10,
                "scene_data__main": 0x9000,
                "load_scene": 0xA000,
            },
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={0x2000: ppu_observer})

        # Run until we've initialized the stack
        # (after PPUCTRL write but before JSR)
        for _ in range(10):
            cpu.step()

        # Verify PPUCTRL was written with 0x00
        ppuctrl_writes = ppu_observer.get_writes_to(0x2000)
        assert 0x00 in ppuctrl_writes

    def test_initializes_stack_pointer(self):
        """Verify that stack pointer is set to 0xFF."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": 0x10,
                "scene_data__main": 0x9000,
                "load_scene": 0xA000,
            },
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Initial SP should be 0xFF after reset
        initial_sp = cpu.sp

        # Run until after TXS instruction
        for _ in range(6):
            cpu.step()

        # SP should now be 0xFF
        assert cpu.sp == 0xFF

    def test_zeros_cpu_registers(self):
        """Verify that A, X, Y registers are zeroed."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": 0x10,
                "scene_data__main": 0x9000,
                "load_scene": 0xA000,
            },
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Set registers to non-zero values
        cpu.a = 0xFF
        cpu.x = 0xFF
        cpu.y = 0xFF

        # Run initialization sequence (before JSR)
        for _ in range(10):
            cpu.step()

        # Registers should all be zero now
        assert cpu.a == 0x00
        assert cpu.x == 0x00
        assert cpu.y == 0x00

    def test_loads_scene_address_to_zero_page(self):
        """Verify that scene data address is loaded into zp__src1."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        scene_data_addr = 0x9000
        zp_src_addr = 0x10

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": zp_src_addr,
                "scene_data__main": scene_data_addr,
                "load_scene": 0xA000,
            },
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Run until just before JSR
        # We need to run past the zero page setup
        for _ in range(15):
            cpu.step()

        # Check that zp__src1 contains the scene data address
        low_byte = memory[zp_src_addr]
        high_byte = memory[zp_src_addr + 1]
        stored_address = (high_byte << 8) | low_byte

        assert stored_address == scene_data_addr

    def test_calls_load_scene_subroutine(self):
        """Verify that JSR to load_scene is executed."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        load_scene_addr = 0xA000

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": 0x10,
                "scene_data__main": 0x9000,
                "load_scene": load_scene_addr,
            },
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Put an RTS instruction at the load_scene address so it returns immediately
        memory[load_scene_addr] = 0x60  # RTS opcode

        # Run until we hit the JSR or a bit after
        for _ in range(20):
            if cpu.pc == load_scene_addr:
                # We successfully jumped to load_scene!
                break
            cpu.step()

        # Verify we reached load_scene
        assert cpu.pc == load_scene_addr

    def test_enters_infinite_loop_after_load_scene(self):
        """Verify that code enters an infinite JMP loop after load_scene returns."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        load_scene_addr = 0xA000

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": 0x10,
                "scene_data__main": 0x9000,
                "load_scene": load_scene_addr,
            },
        )

        cpu, memory = create_test_cpu(code.code, code_address=0x8000)

        # Put an RTS at load_scene so it returns immediately
        memory[load_scene_addr] = 0x60  # RTS

        # Run until we return from load_scene
        for _ in range(25):
            cpu.step()

        # After returning from JSR, we should hit a JMP instruction
        # that jumps to itself (infinite loop)
        loop_pc = cpu.pc

        # Step one instruction (should be the JMP)
        cpu.step()

        # PC should be back to the same address (infinite loop)
        assert cpu.pc == loop_pc

    def test_full_initialization_sequence(self):
        """Integration test: verify the full initialization sequence."""
        preamble = PreambleCodeBlock()
        preamble._main_scene_name = "main"

        scene_data_addr = 0x9000
        load_scene_addr = 0xA000
        zp_src_addr = 0x10

        code = preamble.render(
            start_offset=0x8000,
            names={
                "zp__src1": zp_src_addr,
                "scene_data__main": scene_data_addr,
                "load_scene": load_scene_addr,
            },
        )

        ppu_observer = MemoryObserver()
        cpu, memory = create_test_cpu(code.code, code_address=0x8000, observers={range(0x2000, 0x2008): ppu_observer})

        # Put RTS at load_scene
        memory[load_scene_addr] = 0x60

        # Run until we hit the infinite loop
        prev_pc = 0
        for _ in range(100):
            prev_pc = cpu.pc
            cpu.step()
            if cpu.pc == prev_pc:
                # Hit infinite loop
                break

        # Verify all initialization happened correctly:

        # 1. Interrupts disabled
        assert cpu.p & cpu.INTERRUPT != 0

        # 2. Decimal mode cleared
        assert cpu.p & cpu.DECIMAL == 0

        # 3. PPUCTRL written with 0x00
        assert 0x00 in ppu_observer.get_writes_to(0x2000)

        # 4. Stack pointer at 0xFF
        assert cpu.sp == 0xFF

        # 5. Scene address loaded to zero page
        stored_addr = memory[zp_src_addr] | (memory[zp_src_addr + 1] << 8)
        assert stored_addr == scene_data_addr

        # 6. In infinite loop
        assert cpu.pc == prev_pc
