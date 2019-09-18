"""CPU functionality."""

import sys

PRN = 0b01000111 #PRN 
LDI = 0b10000010 #LDI
HLT = 0b00000001 #HLT
MUL = 0b10100010 #MUL
PUSH = 0b01000101 #PUSH
POP = 0b01000110 #POP
# Register 7 is 0xF4 hex
R7 = 244 # converted to decimal


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Add list properties to the `CPU` class to hold 256 bytes of memory
        self.ram = [0] * 256
        # Add 8 general-purpose registers.
        self.reg = [0] * 8
        # Also add properties for any internal registers you need, e.g. `PC`.
        # Program counter starts at 0, points to currently-executing instruction
        self.pc = 0
        # self.hlt = False
        # Stack stores information temporarily
        # Stack Pointer is at R7 (Register 7)
        # Acts as index 
        self.sp = R7
        # Set up a branch table
        self.branchtable = {}
        self.branchtable[PRN] = self.prn
        self.branchtable[LDI] = self.ldi
        self.branchtable[HLT] = self.hlt
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop

        self.running = True
        

    # PRN - PRN register pseudo-instruction
    def prn(self, a, b):
        # operand_a = self.ram[self.pc + 1] # targeted register
        # Print numeric value stored in the given register.
        # Print to the console the decimal integer value that is stored in the given register.
        print(self.reg[a])

    # LDI - register immediate
    def ldi(self, a, b):
        # operand_a = self.ram[self.pc + 1] # targeted register
        # operand_b = self.ram[self.pc + 2] # value to load
        # This instruction sets a specified register to a specified value. 
        self.reg[a] = b
    
    # HLT - Halt the CPU (and exit the emulator).
    def hlt(self, a, b):
        self.running = False

    # MUL registerA registerB
    def mul(self, a, b):
        # operand_a = self.ram[self.pc + 1] # targeted register
        # operand_b = self.ram[self.pc + 2] # value to load
        # Multiply the values in two registers together and store the result in registerA.
        self.alu("MUL", a, b)

    def push(self, a, b):
        reg_address = self.ram[self.pc + 1] # targeted register
        self.sp -= 1  # grows down as things are pushed on, decrement stack, update stack pointer
        value = self.reg[reg_address] 
        # Copy the value in the given register to the address pointed to by SP
        self.ram[self.sp] = value # Save value in portion of ram _that is allocated for the stack_
    
    def pop(self, a, b):
        reg_address = self.ram[self.pc + 1] # targeted register
        value = self.ram[self.sp] # get value from ram
        self.reg[reg_address] = value # set value from ram to register address
        self.sp += 1 # increment stack, update stack pointer
      
    
       
    # In `CPU`, add method `ram_read()` and `ram_write()` that access the RAM inside
    # the `CPU` object.

    # `ram_read()` should accept the address to read and return the value stored
    # there.
    def ram_read(self, memory_address_register):  # accept address to read
        value = self.ram[memory_address_register]  # get value stored at address
        return value

    # `raw_write()` should accept a value to write, and the address to write it to.
    def ram_write(self, memory_data_register, memory_address_register):  # accept value and address
        self.ram[memory_address_register] = memory_data_register

    def load(self):
        """Load a program into memory."""

        # # For now, we've just hardcoded a program:

        # address = 0

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        # print("arg0", sys.argv[0])
        # print("arg1", sys.argv[1])
        
        # Use those command line arguments to open a file
        try: 
            with open(sys.argv[1]) as f:
                address = 0
                # read in its contents line by line
                for line in f:
                    # search the instruction part before "#"
                    comment_split = line.split("#")
                    # remove empty space
                    num = comment_split[0].strip()
                    
                    try: 
                        # convert binary to int and save appropriate data into RAM.
                        self.ram[address] = int(num, 2)
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} Not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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

    def run(self):
        """Run the CPU."""
    
        while self.running: 
            # Read the memory address that's stored in register `PC`, 
            # Store that result in `IR`, the _Instruction Register_. This can just be a local variable in `run()`.
            ir = self.pc
            op = self.ram[ir]
            # dynamic instruction size
            instruction_size = ((op & 11000000) >> 6) + 1

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.branchtable[op](operand_a, operand_b)
            self.pc += instruction_size

            # Using `ram_read()`, read the bytes at `PC+1` and `PC+2` from RAM into variables `operand_a` and
            # `operand_b` in case the instruction needs them.
            # operand_a = self.ram_read(self.pc + 1)
            # operand_b = self.ram_read(self.pc + 2)

            # depending on the value of the opcode, perform the actions needed for the instruction per the LS-8 spec. 
            # if-else cascade

            ## instructions
            # HLT = 0b00000001  # Machine code: 00000001 
            # LDI = 0b10000010
            # PRN = 0b01000111
            # MUL = 0b10100010
            
            # HLT - Halt the CPU (and exit the emulator).
            # if op == HLT:
            #     running = False

            # LDI - register immediate
            # elif op == LDI:
            #     # This instruction sets a specified register to a specified value. 
            #     self.reg[operand_a] = operand_b
            #     # increment pc by 3, LDI stores 3 memory addresses
            #     self.pc += 3

            # PRN - PRN register pseudo-instruction
            # elif op == PRN: 
            # # Print numeric value stored in the given register.
            # # Print to the console the decimal integer value that is stored in the given register.
            #     print(self.reg[operand_a])
            #     # increment pc by 2, LDI stores 2 memory addresses
            #     self.pc += 2

            # MUL registerA registerB
            # Multiply the values in two registers together and store the result in registerA.
            # elif op == MUL:
            #     self.alu("MUL", operand_a, operand_b)
            #     # increment pc by 3, MUL stores 3 memory addresses
            #     self.pc += 3

            # PUSH
            # elif op == PUSH:
                # reg_num = memory[pc + 1]

                # # decremenet sp
                # reg[SP] -= 1

                # # copy value from register into RAM
                # val = registers[reg_num]
                # top_of_stack = registers[SP]
                # memory[top_of_stack] = val

                # pc += 2
            
            # POP
            # opposite of push 
            # elif op == POP:
                # reg_num = memory[pc + 1]

                # # copy value from the address pointed to SP by given register
                # # copy from stack to register
                # top_of_stack = registers[SP]
                # val = memory[top_of_stack]
                # registers[reg_num] = val

                # # increment SP
                # registers[SP] += 1
                
                # pc += 2



        
