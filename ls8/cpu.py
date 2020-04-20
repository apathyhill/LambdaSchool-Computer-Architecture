"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    # Set Instruction Constants
    INST_LDI = 0b10000010
    INST_HLT = 0b00000001
    INST_PRN = 0b01000111

    def __init__(self):
        """Construct a new CPU."""

        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8
        self.pc = 0

    def load(self, fname):
        """Load a program into memory."""

        address = 0

        with open(fname, "r") as f:
            lines = f.readlines() # Read all lines
            # Find all lines that start with a 0 or 1, 
            # get the first 8 characters,
            # and convert to binary number
            # (might change to some regex later)
            program = [int(i[:8], 2) for i in lines if i[0] in "01"]
            f.close()

        for instruction in program:
            self.ram_write(address, instruction)
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

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

    def run(self):
        """Run the CPU."""

        is_running = True

        while is_running:
            try:
                inst = self.ram_read(self.pc)
                a = self.ram_read(self.pc+1)
                b = self.ram_read(self.pc+2)
                if inst == CPU.INST_LDI: # LDI
                    self.reg[a] = b
                    self.pc += 3
                elif inst == CPU.INST_PRN: # PRN
                    print(self.reg[a])
                    self.pc += 2
                elif inst == CPU.INST_HLT: # HLT
                    is_running = False
            except:
                is_running = False
                pass
    