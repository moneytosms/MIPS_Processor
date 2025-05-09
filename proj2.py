# Simple Python MIPS Simulator with Stack and JR $ra Support
# Supports R-type (add, sub, sll, slt, xor, or, nor, and, jr),
# I-type (addi, lw, sw, beq, bne), and J-type (j, jal) instructions.

class RegisterFile:
    """
    Simulates 32 general-purpose MIPS registers.
    Register 0 is hardwired to zero.
    We also include a special register 32 to simulate lo register.
    
    Common MIPS registers:
    $0 ($zero) - Always contains 0
    $1 ($at) - Assembler temporary
    $2-$3 ($v0-$v1) - Function return values
    $4-$7 ($a0-$a3) - Function arguments
    $8-$15 ($t0-$t7) - Temporary registers
    $16-$23 ($s0-$s7) - Saved registers
    $24-$25 ($t8-$t9) - More temporary registers
    $26-$27 ($k0-$k1) - Kernel registers
    $28 ($gp) - Global pointer
    $29 ($sp) - Stack pointer
    $30 ($fp) - Frame pointer
    $31 ($ra) - Return address
    """
    def __init__(self):
        self.registers = [0] * 33  # 32 general registers + 1 for lo register

    def read(self, index):
        """Read value from register at given index"""
        return self.registers[index]

    def write(self, index, value):
        """Write value to register at given index, except register 0 which is read-only"""
        if index == 0:
            return  # Register 0 is read-only and always zero
        self.registers[index] = value & 0xFFFFFFFF  # Simulate 32-bit overflow


class Memory:
    """
    Simulates byte-addressable memory.
    Provides methods to load/store words.
    
    Memory Layout in MIPS:
    0x00000000 - Reserved
    0x00400000 - Text segment (instructions)
    0x10000000 - Data segment (global variables)
    0x7fffffff - Stack segment (grows downward)
    """
    def __init__(self, size_bytes=2*1024*1024):  # 2MB of memory
        self.data = bytearray(size_bytes)
        self.base_address = 0  # Physical base address in the simulation
        
    def _translate_address(self, address):
        """
        Translate MIPS address to internal memory array index.
        
        Args:
            address: The MIPS memory address to translate
            
        Returns:
            The corresponding internal memory array index
        """
        # For simplicity, we'll just mask off the upper bits to handle MIPS addresses
        # MIPS addresses like 0x00400000 (text segment) need to be mapped to our memory array
        return address & 0x001FFFFF  # Keep only lower 21 bits to map 0x00400000->0x00000000, etc.

    def load_word(self, address):
        """
        Load a 32-bit word from memory at the specified address.
        
        Args:
            address: The memory address to load from
            
        Returns:
            The 32-bit word value at that address
        """
        internal_addr = self._translate_address(address)
        if internal_addr < 0 or internal_addr + 3 >= len(self.data):
            raise IndexError(f"Memory access out of bounds: {address} -> {internal_addr}")
            
        value = 0
        for i in range(4):
            value = (value << 8) | self.data[internal_addr + i]
        return value

    def store_word(self, address, value):
        """
        Store a 32-bit word to memory at the specified address.
        
        Args:
            address: The memory address to store at
            value: The 32-bit word value to store
        """
        internal_addr = self._translate_address(address)
        if internal_addr < 0 or internal_addr + 3 >= len(self.data):
            raise IndexError(f"Memory access out of bounds: {address} -> {internal_addr}")
            
        # Extract each byte from the 32-bit value and store in memory
        for i in range(4):
            byte_val = (value >> (24 - (i * 8))) & 0xFF
            self.data[internal_addr + i] = byte_val


class CPU:
    """
    Main CPU class: fetches, decodes, and executes instructions.
    Includes support for jr $ra and stack operations.
    
    The basic fetch-decode-execute cycle:
    1. Fetch - Get the next instruction from memory
    2. Decode - Determine what operation to perform
    3. Execute - Perform the operation
    """
    def __init__(self, memory):
        self.memory = memory
        self.registers = RegisterFile()
        self.program_counter = 0x00400000  # MIPS text segment start
        # Initialize stack pointer ($sp = register 29)
        self.registers.write(29, 0x100000)
        # Initialize lo register for mult/div operations
        self.registers.write(32, 0)

    def fetch(self):
        """
        Fetch the instruction at the current program counter.
        
        Returns:
            The 32-bit instruction word
        """
        instr = self.memory.load_word(self.program_counter)
        self.program_counter += 4  # Move to next instruction
        return instr

    def decode(self, instr):
        """
        Decode a 32-bit MIPS instruction.
        
        Args:
            instr: The 32-bit instruction word
            
        Returns:
            A tuple representing the decoded instruction:
            R-type: ('R', rs, rt, rd, shift, function)
            I-type: ('I', opcode, rs, rt, immediate)
            J-type: ('J', opcode, address)
        """
        opcode = (instr >> 26) & 0x3F
        if opcode == 0:
            # R-type format: opcode(6) rs(5) rt(5) rd(5) shamt(5) funct(6)
            rs = (instr >> 21) & 0x1F
            rt = (instr >> 16) & 0x1F
            rd = (instr >> 11) & 0x1F
            sh = (instr >> 6) & 0x1F
            fn = instr & 0x3F
            return ('R', rs, rt, rd, sh, fn)
        elif opcode in (2, 3):
            # J-type format: opcode(6) address(26)
            addr = instr & 0x03FFFFFF
            return ('J', opcode, addr)
        else:
            # I-type format: opcode(6) rs(5) rt(5) immediate(16)
            rs = (instr >> 21) & 0x1F
            rt = (instr >> 16) & 0x1F
            imm = instr & 0xFFFF
            # Sign extend the immediate value
            if imm & 0x8000:  # If the MSB is 1
                imm = imm - 0x10000
            return ('I', opcode, rs, rt, imm)

    def execute(self, decoded):
        """
        Execute a decoded MIPS instruction.
        
        Args:
            decoded: The decoded instruction tuple from decode()
        """
        t = decoded[0]

        # R-type instructions
        if t == 'R':
            _, rs, rt, rd, sh, fn = decoded
            v1, v2 = self.registers.read(rs), self.registers.read(rt)
            if fn == 0x20:  # add
                self.registers.write(rd, v1 + v2)
            elif fn == 0x22:  # sub
                self.registers.write(rd, v1 - v2)
            elif fn == 0x00:  # sll
                self.registers.write(rd, v2 << sh)
            elif fn == 0x2A:  # slt
                self.registers.write(rd, 1 if v1 < v2 else 0)
            elif fn == 0x26:  # xor
                self.registers.write(rd, v1 ^ v2)
            elif fn == 0x25:  # or
                self.registers.write(rd, v1 | v2)
            elif fn == 0x27:  # nor
                self.registers.write(rd, ~(v1 | v2))
            elif fn == 0x24:  # and
                self.registers.write(rd, v1 & v2)
            elif fn == 0x08:  # jr
                self.program_counter = self.registers.read(rs)
            elif fn == 0x18:  # mult
                # In a real MIPS, this would set both hi and lo registers
                product = v1 * v2
                # For simplicity, we'll just set a pseudo lo register at index 32
                self.registers.write(32, product & 0xFFFFFFFF)
            elif fn == 0x1A:  # div
                # In a real MIPS, this would set both hi and lo registers
                if v2 != 0:  # Avoid division by zero
                    quotient = v1 // v2
                    self.registers.write(32, quotient & 0xFFFFFFFF)
            elif fn == 0x12:  # mflo - move from lo
                # For simplicity, we're using register 32 as the lo register
                lo_val = self.registers.read(32)
                self.registers.write(rd, lo_val)

        # I-type instructions
        elif t == 'I':
            _, op, rs, rt, imm = decoded
            # Get source register value
            rs_val = self.registers.read(rs)
            
            if op == 0x08:  # addi
                self.registers.write(rt, rs_val + imm)
                
            elif op == 0x23:  # lw
                addr = rs_val + imm
                self.registers.write(rt, self.memory.load_word(addr))
                
            elif op == 0x2B:  # sw
                addr = rs_val + imm
                rt_val = self.registers.read(rt)
                self.memory.store_word(addr, rt_val)
                
            elif op == 0x04:  # beq
                if self.registers.read(rs) == self.registers.read(rt):
                    # Branch targets are relative to the next instruction
                    # So we need to multiply by 4 to get byte offset
                    self.program_counter = self.program_counter + (imm * 4)
                    
            elif op == 0x05:  # bne
                if self.registers.read(rs) != self.registers.read(rt):
                    # Branch targets are relative to the next instruction
                    # So we need to multiply by 4 to get byte offset
                    self.program_counter = self.program_counter + (imm * 4)

        # J-type instructions
        elif t == 'J':
            _, op, addr = decoded
            # Jump target calculation: PC[31:28] || target << 2
            target = (self.program_counter & 0xF0000000) | (addr << 2)
            
            if op == 0x02:  # j
                self.program_counter = target
                
            elif op == 0x03:  # jal
                # Save return address in $ra (r31)
                self.registers.write(31, self.program_counter)
                # Jump to target address
                self.program_counter = target

    def run(self, cycles=1):
        """
        Run the CPU for the specified number of cycles.
        
        Args:
            cycles: Number of fetch-decode-execute cycles to run
        """
        for _ in range(cycles):
            instr = self.fetch()
            dec = self.decode(instr)
            self.execute(dec)


def print_registers(reg_file):
    """
    Print the contents of all registers.
    
    Args:
        reg_file: RegisterFile object to print
    """
    print("\n==== Register State ====")
    # Define register names for better readability
    reg_names = [
        "$zero", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3",
        "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
        "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
        "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra"
    ]
    for i, val in enumerate(reg_file.registers[:32]):
        print(f"{reg_names[i]} (${i:02}): {val:#010x}")
    print(f"lo: {reg_file.registers[32]:#010x}")
    print("======================\n")


def print_help():
    """
    Print help information about MIPS and how to use this simulator.
    """
    print("\n=== MIPS Simulator Help ===")
    print("\n--- MIPS Architecture Overview ---")
    print("MIPS is a RISC (Reduced Instruction Set Computer) architecture.")
    print("It has 32 general-purpose registers, a program counter, and a simple instruction set.")
    
    print("\n--- Register Overview ---")
    print("$0  ($zero): Always contains the value 0")
    print("$1  ($at)  : Assembler temporary")
    print("$2-$3  ($v0-$v1): Function return values")
    print("$4-$7  ($a0-$a3): Function arguments")
    print("$8-$15 ($t0-$t7): Temporary registers")
    print("$16-$23 ($s0-$s7): Saved registers")
    print("$24-$25 ($t8-$t9): More temporary registers")
    print("$26-$27 ($k0-$k1): Reserved for OS kernel")
    print("$28 ($gp): Global pointer")
    print("$29 ($sp): Stack pointer")
    print("$30 ($fp): Frame pointer")
    print("$31 ($ra): Return address")
    
    print("\n--- Instruction Types ---")
    print("1. R-type: Operations on registers")
    print("   Format: opcode(6) rs(5) rt(5) rd(5) shamt(5) funct(6)")
    print("   Example: add $3, $1, $2  =>  rd = rs + rt")
    
    print("\n2. I-type: Immediate operations, loads, stores, branches")
    print("   Format: opcode(6) rs(5) rt(5) immediate(16)")
    print("   Examples:")
    print("     addi $2, $1, 5  =>  rt = rs + immediate")
    print("     lw $3, 4($1)    =>  rt = Memory[rs + immediate]")
    print("     beq $1, $2, 10  =>  if(rs == rt) PC += (immediate * 4)")
    
    print("\n3. J-type: Jumps")
    print("   Format: opcode(6) address(26)")
    print("   Examples:")
    print("     j 0x100000  =>  PC = PC[31:28] | (address << 2)")
    print("     jal 0x100000  =>  $ra = PC + 4; PC = PC[31:28] | (address << 2)")
    
    print("\n--- Memory Layout ---")
    print("0x00400000: Text segment (Code)")
    print("0x10000000: Data segment (Global variables)")
    print("0x7fffffff: Stack segment (grows downward)")
    
    print("\n--- How to Use This Simulator ---")
    print("1. Load instructions: Enter MIPS instructions as hex words")
    print("   For example, addi $8, $0, 5 is 0x20080005")
    print("2. Execute: Run the simulator for a specified number of cycles")
    print("3. View registers: Display the contents of all registers")
    
    print("\n--- Factorial Example ---")
    print("To calculate factorial of 5, enter these instructions:")
    print("0x20080005 0x20090001 0x11000004 0x01280018 0x00004812 0x2108FFFF 0x08100002")
    
    print("\n--- Learn More about MIPS ---")
    print("1. MIPS Reference Sheet: https://inst.eecs.berkeley.edu/~cs61c/resources/MIPS_Green_Sheet.pdf")
    print("2. MIPS Assembly Programming Tutorial: https://chortle.ccsu.edu/AssemblyTutorial/index.html")
    print("3. Book: 'See MIPS Run' by Dominic Sweetman")
    print("4. Book: 'Computer Organization and Design' by Patterson and Hennessy")
    print("===========================\n")


def main_menu():
    """
    Main menu for the MIPS simulator.
    Allows the user to load instructions, execute the program, and view register state.
    """
    mem = Memory()
    cpu = CPU(mem)
    while True:
        print("\n--- MIPS Simulator Menu ---")
        print("1) Load instructions (hex words)")
        print("2) Execute cycles")
        print("3) Show all registers")
        print("4) Help - Learn about MIPS")
        print("5) Exit")
        choice = input("Select an option: ")
        if choice == '1':
            data = input("Enter hex words separated by spaces: ")
            addr = 0x00400000  # reset load address each time
            for w in data.split():
                mem.store_word(addr, int(w, 16))
                addr += 4
            print("Instructions loaded.")
        elif choice == '2':
            n = int(input("Number of cycles to execute: "))
            cpu.run(n)
            print(f"Executed {n} cycles.")
        elif choice == '3':
            print_registers(cpu.registers)
        elif choice == '4':
            print_help()
        elif choice == '5':
            print("Exiting simulator.")
            break
        else:
            print("Invalid choice — please try again.")

if __name__ == '__main__':
    main_menu()



