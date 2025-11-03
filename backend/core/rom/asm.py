"""
6502 Assembly builder with fluent interface.

Provides a readable way to generate 6502 machine code without runtime assembly overhead.
"""


class Asm6502:
    """
    Fluent interface for building 6502 machine code.

    Usage:
        asm = Asm6502()
        asm.sei()  # Disable interrupts
        asm.cld()  # Clear decimal mode
        asm.ldx_imm(0xFF)  # LDX #$FF
        asm.txs()  # TXS
        code = asm.bytes()
    """

    def __init__(self):
        self._code = bytearray()

    def bytes(self) -> bytes:
        """Return the generated machine code as bytes."""
        return bytes(self._code)

    def __len__(self) -> int:
        """Return the current size of generated code."""
        return len(self._code)

    # ===== Status Register Operations =====

    def sei(self):
        """SEI - Set Interrupt Disable (0x78)"""
        self._code.append(0x78)
        return self

    def cli(self):
        """CLI - Clear Interrupt Disable (0x58)"""
        self._code.append(0x58)
        return self

    def sed(self):
        """SED - Set Decimal Flag (0xF8)"""
        self._code.append(0xF8)
        return self

    def cld(self):
        """CLD - Clear Decimal Flag (0xD8)"""
        self._code.append(0xD8)
        return self

    def sec(self):
        """SEC - Set Carry Flag (0x38)"""
        self._code.append(0x38)
        return self

    def clc(self):
        """CLC - Clear Carry Flag (0x18)"""
        self._code.append(0x18)
        return self

    def clv(self):
        """CLV - Clear Overflow Flag (0xB8)"""
        self._code.append(0xB8)
        return self

    # ===== Load/Store Operations =====

    def lda_imm(self, value: int):
        """LDA #immediate (0xA9)"""
        self._code.extend([0xA9, value & 0xFF])
        return self

    def lda_zp(self, addr: int):
        """LDA zero page (0xA5)"""
        self._code.extend([0xA5, addr & 0xFF])
        return self

    def lda_abs(self, addr: int):
        """LDA absolute (0xAD)"""
        self._code.extend([0xAD, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def lda_ind_y(self, zp_addr: int):
        """LDA (zero page),Y (0xB1)"""
        self._code.extend([0xB1, zp_addr & 0xFF])
        return self

    def lda_abs_x(self, addr: int):
        """LDA absolute,X (0xBD)"""
        self._code.extend([0xBD, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def ldx_imm(self, value: int):
        """LDX #immediate (0xA2)"""
        self._code.extend([0xA2, value & 0xFF])
        return self

    def ldx_zp(self, addr: int):
        """LDX zero page (0xA6)"""
        self._code.extend([0xA6, addr & 0xFF])
        return self

    def ldx_abs(self, addr: int):
        """LDX absolute (0xAE)"""
        self._code.extend([0xAE, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def ldy_imm(self, value: int):
        """LDY #immediate (0xA0)"""
        self._code.extend([0xA0, value & 0xFF])
        return self

    def ldy_zp(self, addr: int):
        """LDY zero page (0xA4)"""
        self._code.extend([0xA4, addr & 0xFF])
        return self

    def ldy_abs(self, addr: int):
        """LDY absolute (0xAC)"""
        self._code.extend([0xAC, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def sta_zp(self, addr: int):
        """STA zero page (0x85)"""
        self._code.extend([0x85, addr & 0xFF])
        return self

    def sta_abs(self, addr: int):
        """STA absolute (0x8D)"""
        self._code.extend([0x8D, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def sta_ind_y(self, zp_addr: int):
        """STA (zero page),Y (0x91)"""
        self._code.extend([0x91, zp_addr & 0xFF])
        return self

    def sta_abs_x(self, addr: int):
        """STA absolute,X (0x9D)"""
        self._code.extend([0x9D, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def sta_abs_y(self, addr: int):
        """STA absolute,Y (0x99)"""
        self._code.extend([0x99, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def stx_zp(self, addr: int):
        """STX zero page (0x86)"""
        self._code.extend([0x86, addr & 0xFF])
        return self

    def stx_abs(self, addr: int):
        """STX absolute (0x8E)"""
        self._code.extend([0x8E, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def sty_zp(self, addr: int):
        """STY zero page (0x84)"""
        self._code.extend([0x84, addr & 0xFF])
        return self

    def sty_abs(self, addr: int):
        """STY absolute (0x8C)"""
        self._code.extend([0x8C, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    # ===== Register Transfer =====

    def tax(self):
        """TAX - Transfer A to X (0xAA)"""
        self._code.append(0xAA)
        return self

    def tay(self):
        """TAY - Transfer A to Y (0xA8)"""
        self._code.append(0xA8)
        return self

    def txa(self):
        """TXA - Transfer X to A (0x8A)"""
        self._code.append(0x8A)
        return self

    def tya(self):
        """TYA - Transfer Y to A (0x98)"""
        self._code.append(0x98)
        return self

    def txs(self):
        """TXS - Transfer X to Stack Pointer (0x9A)"""
        self._code.append(0x9A)
        return self

    def tsx(self):
        """TSX - Transfer Stack Pointer to X (0xBA)"""
        self._code.append(0xBA)
        return self

    # ===== Stack Operations =====

    def pha(self):
        """PHA - Push Accumulator (0x48)"""
        self._code.append(0x48)
        return self

    def php(self):
        """PHP - Push Processor Status (0x08)"""
        self._code.append(0x08)
        return self

    def pla(self):
        """PLA - Pull Accumulator (0x68)"""
        self._code.append(0x68)
        return self

    def plp(self):
        """PLP - Pull Processor Status (0x28)"""
        self._code.append(0x28)
        return self

    # ===== Increment/Decrement =====

    def inc_zp(self, addr: int):
        """INC zero page (0xE6)"""
        self._code.extend([0xE6, addr & 0xFF])
        return self

    def inc_abs(self, addr: int):
        """INC absolute (0xEE)"""
        self._code.extend([0xEE, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def inx(self):
        """INX - Increment X (0xE8)"""
        self._code.append(0xE8)
        return self

    def iny(self):
        """INY - Increment Y (0xC8)"""
        self._code.append(0xC8)
        return self

    def dec_zp(self, addr: int):
        """DEC zero page (0xC6)"""
        self._code.extend([0xC6, addr & 0xFF])
        return self

    def dec_abs(self, addr: int):
        """DEC absolute (0xCE)"""
        self._code.extend([0xCE, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def dex(self):
        """DEX - Decrement X (0xCA)"""
        self._code.append(0xCA)
        return self

    def dey(self):
        """DEY - Decrement Y (0x88)"""
        self._code.append(0x88)
        return self

    # ===== Branching =====

    def bne(self, offset: int):
        """BNE - Branch if Not Equal (0xD0)"""
        self._code.extend([0xD0, offset & 0xFF])
        return self

    def beq(self, offset: int):
        """BEQ - Branch if Equal (0xF0)"""
        self._code.extend([0xF0, offset & 0xFF])
        return self

    def bpl(self, offset: int):
        """BPL - Branch if Plus (0x10)"""
        self._code.extend([0x10, offset & 0xFF])
        return self

    def bmi(self, offset: int):
        """BMI - Branch if Minus (0x30)"""
        self._code.extend([0x30, offset & 0xFF])
        return self

    def bcc(self, offset: int):
        """BCC - Branch if Carry Clear (0x90)"""
        self._code.extend([0x90, offset & 0xFF])
        return self

    def bcs(self, offset: int):
        """BCS - Branch if Carry Set (0xB0)"""
        self._code.extend([0xB0, offset & 0xFF])
        return self

    def bvc(self, offset: int):
        """BVC - Branch if Overflow Clear (0x50)"""
        self._code.extend([0x50, offset & 0xFF])
        return self

    def bvs(self, offset: int):
        """BVS - Branch if Overflow Set (0x70)"""
        self._code.extend([0x70, offset & 0xFF])
        return self

    # ===== Jumps and Calls =====

    def jmp_abs(self, addr: int):
        """JMP absolute (0x4C)"""
        self._code.extend([0x4C, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def jmp_ind(self, addr: int):
        """JMP indirect (0x6C)"""
        self._code.extend([0x6C, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def jsr(self, addr: int):
        """JSR - Jump to Subroutine (0x20)"""
        self._code.extend([0x20, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    def rts(self):
        """RTS - Return from Subroutine (0x60)"""
        self._code.append(0x60)
        return self

    def rti(self):
        """RTI - Return from Interrupt (0x40)"""
        self._code.append(0x40)
        return self

    # ===== Bitwise Operations =====

    def and_imm(self, value: int):
        """AND #immediate (0x29)"""
        self._code.extend([0x29, value & 0xFF])
        return self

    def ora_imm(self, value: int):
        """ORA #immediate (0x09)"""
        self._code.extend([0x09, value & 0xFF])
        return self

    def ora_zp(self, addr: int):
        """ORA zero page (0x05)"""
        self._code.extend([0x05, addr & 0xFF])
        return self

    def eor_imm(self, value: int):
        """EOR #immediate (0x49)"""
        self._code.extend([0x49, value & 0xFF])
        return self

    def bit_zp(self, addr: int):
        """BIT zero page (0x24)"""
        self._code.extend([0x24, addr & 0xFF])
        return self

    def bit_abs(self, addr: int):
        """BIT absolute (0x2C)"""
        self._code.extend([0x2C, addr & 0xFF, (addr >> 8) & 0xFF])
        return self

    # ===== Arithmetic =====

    def adc_imm(self, value: int):
        """ADC #immediate (0x69)"""
        self._code.extend([0x69, value & 0xFF])
        return self

    # ===== Comparison =====

    def cmp_imm(self, value: int):
        """CMP #immediate (0xC9)"""
        self._code.extend([0xC9, value & 0xFF])
        return self

    def cpx_imm(self, value: int):
        """CPX #immediate (0xE0)"""
        self._code.extend([0xE0, value & 0xFF])
        return self

    def cpy_imm(self, value: int):
        """CPY #immediate (0xC0)"""
        self._code.extend([0xC0, value & 0xFF])
        return self

    # ===== Miscellaneous =====

    def nop(self):
        """NOP - No Operation (0xEA)"""
        self._code.append(0xEA)
        return self

    def brk(self):
        """BRK - Break (0x00)"""
        self._code.append(0x00)
        return self

    # ===== Helper: Infinite Loop =====

    def loop_forever(self):
        """Generate an infinite loop: JMP to current address"""
        # We need to know the current offset to jump to it
        # This will be a relative jump to itself: JMP current_addr
        # The caller needs to provide the actual address
        # For now, emit a placeholder that needs to be fixed up
        return self
