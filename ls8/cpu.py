"""CPU functionality."""

from datetime import datetime
import msvcrt
import sys

class CPU:
    """Main CPU class."""

    # Set Instruction Constants
    INST_LDI  = 0b10000010
    INST_HLT  = 0b00000001
    INST_PRN  = 0b01000111
    INST_ADD  = 0b10100000
    INST_SUB  = 0b10100001
    INST_MUL  = 0b10100010
    INST_DIV  = 0b10100011
    INST_AND  = 0b10101000
    INST_OR   = 0b10101010
    INST_XOR  = 0b10101011
    INST_NOT  = 0b01101001
    INST_SHL  = 0b10101100
    INST_SHR  = 0b10101101
    INST_CALL = 0b01010000
    INST_RET  = 0b00010001
    INST_PUSH = 0b01000101
    INST_POP  = 0b01000110
    INST_CMP  = 0b10100111
    INST_INC  = 0b01100101
    INST_DEC  = 0b01100110
    INST_PRA  = 0b01001000
    INST_JEQ  = 0b01010101
    INST_LD   = 0b10000011
    INST_JMP  = 0b01010100
    INST_ST   = 0b10000100
    INST_IRET = 0b00010011
    INST_JNE  = 0b01010110

    def __init__(self):
        """Construct a new CPU."""

        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8
        self.reg[7] = 0x74
        self.pc = 0
        self.flag = 0b00000000
        self.time = datetime.now().second
        self.time_prev = self.time

    def load(self, fname):
        """Load a program into memory."""

        with open(fname, "r") as f:
            lines = f.readlines() # Read all lines
            # Find all lines that start with a 0 or 1, 
            # get the first 8 characters,
            # and convert to binary number
            # (might change to some regex later)
            program = [int(i[:8], 2) for i in lines if i[0] in "01"]
            f.close()

        for address, instruction in enumerate(program):
            self.ram_write(address, instruction)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == CPU.INST_ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == CPU.INST_SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == CPU.INST_MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CPU.INST_DIV:
            self.reg[reg_a] //= self.reg[reg_b]
        elif op == CPU.INST_AND:
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == CPU.INST_OR:
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == CPU.INST_XOR:
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == CPU.INST_NOT:
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == CPU.INST_SHL:
            self.reg[reg_a] = self.reg[reg_a] << reg_b
        elif op == CPU.INST_SHR:
            self.reg[reg_a] = self.reg[reg_a] >> reg_b
        elif op == CPU.INST_INC:
            self.reg[reg_a] += 1
        elif op == CPU.INST_DEC:
            self.reg[reg_a] -= 1
        elif op == CPU.INST_CMP:
            self.flag = ((self.reg[reg_a] < self.reg[reg_b]) << 2) | \
                        ((self.reg[reg_a] > self.reg[reg_b]) << 1) | \
                        ((self.reg[reg_a] == self.reg[reg_b]) << 0)
        else:
            raise Exception("Unsupported ALU operation.")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        """Return an address in RAM."""

        return self.ram[address]

    def ram_write(self, address, value):
        """Set an address in RAM to a certain value."""

        self.ram[address] = value

    def handle_interrupts(self):
        self.time = datetime.now().second # Time interrupt
        if not self.time == self.time_prev:
            self.reg[6] |= 0b00000001
            self.time_prev = self.time
        if msvcrt.kbhit(): # Keyboard interrupt
            self.ram_write(0xF4, ord(msvcrt.getch()))
            self.reg[6] |= 0b00000010
        maskedInterrupts = self.reg[5] & self.reg[6]
        for i in range(8):
            if ((maskedInterrupts >> i) & 1): # Check for interrupt flags
                self.reg[6] &= ~(1 << i) # Turn bit off
                self.reg[7] -= 1 # Push PC
                self.ram_write(self.reg[7], self.pc)
                self.reg[7] -= 1 # Push Flag
                self.ram_write(self.reg[7], self.flag)
                for j in range(7): # Push Reg0-6
                    self.reg[7] -= 1
                    self.ram_write(self.reg[7], self.reg[j])
                self.pc = self.ram_read(0xF8 + i) # Set PC to interrupt handler
                break

    def run(self):
        """Run the CPU."""

        is_running = True

        while is_running:
            try:
                self.handle_interrupts() # Check for interrupts

                inst = self.ram_read(self.pc)
                a = self.ram_read(self.pc+1)
                b = self.ram_read(self.pc+2)
                # print(f"{inst:08b} {a:08b} {b:08b} {self.pc}")
                if inst & 0b00100000:
                    self.alu(inst, a, b)
                elif inst == CPU.INST_LDI: # LDI
                    self.reg[a] = b
                elif inst == CPU.INST_PRN: # PRN
                    print(self.reg[a])
                elif inst == CPU.INST_PRA: # PRA
                    print(chr(self.reg[a]), end="", flush=True)
                elif inst == CPU.INST_PUSH: # PUSH
                    self.reg[7] -= 1
                    self.ram_write(self.reg[7], self.reg[a])
                elif inst == CPU.INST_POP: # POP
                    self.reg[a] = self.ram_read(self.reg[7])
                    self.reg[7] += 1
                elif inst == CPU.INST_CALL: # CALL
                    self.reg[7] -= 1
                    self.ram_write(self.reg[7], self.pc+2)
                    self.pc = self.reg[a]
                elif inst == CPU.INST_RET: # RET
                    self.pc = self.ram_read(self.reg[7])
                    self.reg[7] += 1
                elif inst == CPU.INST_JEQ: # JEQ
                    if self.flag & 1:
                        self.pc = self.reg[a]
                    else:
                        inst &= ~0b00010000
                elif inst == CPU.INST_JNE: # JNE
                    if ~(self.flag & 1):
                        self.pc = self.reg[a]
                    else:
                        inst &= ~0b00010000
                elif inst == CPU.INST_ST: # ST
                    self.ram_write(self.reg[a], self.reg[b])
                elif inst == CPU.INST_LD: # LD
                    self.reg[a] = self.ram_read(self.reg[b])
                elif inst == CPU.INST_IRET: # IRET
                    for i in range(7):
                        self.reg[6-i] = self.ram_read(self.reg[7]) # Pop Reg6-0
                        self.reg[7] += 1
                    self.flag = self.ram_read(self.reg[7]) # Pop Flag
                    self.reg[7] += 1
                    self.pc = self.ram_read(self.reg[7]) # Pop PC
                    self.reg[7] += 1
                elif inst == CPU.INST_JMP: # JMP
                    self.pc = self.reg[a]
                elif inst == CPU.INST_HLT: # HLT
                    is_running = False
                else:
                    raise Exception("Unsupported instruction.")
                if not inst & 0b00010000:
                    self.pc += ((inst & 0b11000000) >> 6) + 1
            except Exception as e:
                print(e)
                self.trace()
                is_running = False
                pass
    