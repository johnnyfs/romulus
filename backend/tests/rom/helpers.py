from collections import defaultdict
from typing import Callable

from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory


class MemoryObserver:
    """
    Observer for memory reads and writes in py65.

    Tracks all reads and writes to specified address ranges,
    allowing assertions on I/O patterns (e.g., PPU register writes).
    """

    def __init__(self):
        self.reads: list[tuple[int, int]] = []  # [(address, value), ...]
        self.writes: list[tuple[int, int]] = []  # [(address, value), ...]

    def on_read(self, address: int) -> None:
        """Callback for memory reads. Returns None to use actual memory value."""
        value = None  # Use actual memory value
        self.reads.append((address, value))
        return value

    def on_write(self, address: int, value: int) -> int:
        """Callback for memory writes. Returns the value to actually write."""
        self.writes.append((address, value))
        return value

    def get_writes(self) -> list[tuple[int, int]]:
        """Get all recorded writes as (address, value) tuples."""
        return self.writes

    def get_reads(self) -> list[tuple[int, int]]:
        """Get all recorded reads as (address, value) tuples."""
        return self.reads

    def get_writes_to(self, address: int) -> list[int]:
        """Get all values written to a specific address."""
        return [value for addr, value in self.writes if addr == address]

    def clear(self):
        """Clear all recorded reads and writes."""
        self.reads.clear()
        self.writes.clear()


def create_test_cpu(
    code: bytes,
    code_address: int = 0x8000,
    observers: dict[int | range, MemoryObserver] | None = None
) -> tuple[MPU, ObservableMemory]:
    """
    Create a test CPU with code loaded and optional memory observers.

    Args:
        code: The machine code to load
        code_address: Where to load the code in memory (default: 0x8000)
        observers: Dict mapping addresses/ranges to MemoryObserver instances
                  Example: {0x2006: ppu_observer, range(0x2000, 0x2008): ppu_observer}

    Returns:
        Tuple of (MPU instance, ObservableMemory instance)
    """
    memory = ObservableMemory()
    cpu = MPU(memory=memory)

    # Load code into memory
    memory.write(code_address, list(code))

    # Set up observers if provided
    if observers:
        for addr_or_range, observer in observers.items():
            if isinstance(addr_or_range, range):
                addresses = addr_or_range
            else:
                addresses = range(addr_or_range, addr_or_range + 1)

            # Subscribe to reads and writes
            memory.subscribe_to_read(addresses, observer.on_read)
            memory.subscribe_to_write(addresses, observer.on_write)

    # Set PC to code address
    cpu.pc = code_address

    return cpu, memory


def run_until(
    cpu: MPU,
    condition: Callable[[], bool],
    max_cycles: int = 10000
) -> int:
    """
    Run the CPU until a condition is met or max cycles reached.

    Args:
        cpu: The MPU instance
        condition: A callable that returns True when execution should stop
        max_cycles: Maximum number of instructions to execute

    Returns:
        Number of cycles executed

    Raises:
        RuntimeError: If max_cycles is reached before condition is met
    """
    cycles = 0
    while cycles < max_cycles:
        if condition():
            return cycles
        cpu.step()
        cycles += 1

    raise RuntimeError(
        f"CPU did not reach stop condition after {max_cycles} cycles. "
        f"PC: ${cpu.pc:04X}, A: ${cpu.a:02X}, X: ${cpu.x:02X}, Y: ${cpu.y:02X}"
    )


def run_subroutine(
    cpu: MPU,
    memory: ObservableMemory,
    subroutine_address: int,
    return_address: int = 0xFFFF,
    max_cycles: int = 10000
) -> int:
    """
    Run a subroutine via JSR and return when RTS is executed.

    Sets up a return address on the stack and runs until PC reaches that address.

    Args:
        cpu: The MPU instance
        memory: The memory instance
        subroutine_address: Address of the subroutine to call
        return_address: Address to return to (default: 0xFFFF)
        max_cycles: Maximum cycles to execute

    Returns:
        Number of cycles executed
    """
    # Set up return address on stack (JSR pushes PC + 2)
    # We want to return to return_address, so push return_address - 1
    ret_addr_minus_one = (return_address - 1) & 0xFFFF
    cpu.stPushWord(ret_addr_minus_one)

    # Jump to subroutine
    cpu.pc = subroutine_address

    # Run until we return
    return run_until(cpu, lambda: cpu.pc == return_address, max_cycles)
