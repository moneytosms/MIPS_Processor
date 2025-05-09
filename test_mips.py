"""
MIPS Simulator Test Suite
This file contains comprehensive tests for the MIPS simulator
"""

from proj2 import RegisterFile, Memory, CPU

def test_register_file():
    """Test RegisterFile functionality"""
    print("\n=== Testing RegisterFile ===")
    reg = RegisterFile()
    reg.write(0, 100)  # Should not change $zero
    reg.write(8, 42)   # Write to $t0
    
    # Check if register $zero is still 0
    print(f"Register $zero = {reg.read(0)}")
    assert reg.read(0) == 0, "Register $zero should always be 0"
    # Check if register $t0 has the value 42
    print(f"Register $t0 = {reg.read(8)}")
    assert reg.read(8) == 42, "Register $t0 should be 42"
    
    print("RegisterFile tests passed!")

def test_memory():
    """Test Memory functionality"""
    print("\n=== Testing Memory ===")
    mem = Memory()
    test_addr = 0x10000000  # Data segment
    mem.store_word(test_addr, 0x12345678)
    
    # Check if the value can be correctly loaded
    value = mem.load_word(test_addr)
    print(f"Memory at 0x{test_addr:08x} = 0x{value:08x}")
    assert value == 0x12345678, "Memory load/store failed"
    
    print("Memory tests passed!")

def test_basic_instructions():
    """Test basic R-type and I-type arithmetic instructions"""
    print("\n=== Testing Basic Instructions ===")
    mem = Memory()
    cpu = CPU(mem)
    
    # Test addi instruction: addi $t0, $zero, 5 (0x20080005)
    mem.store_word(0x00400000, 0x20080005)
    cpu.run(1)
    print(f"After addi: $t0 = {cpu.registers.read(8)}")
    assert cpu.registers.read(8) == 5, "addi instruction failed"
    print("addi instruction test passed!")
    
    # Test add instruction: add $t1, $t0, $t0 (0x01084820)
    mem.store_word(0x00400004, 0x01084820)
    cpu.run(1)
    print(f"After add: $t1 = {cpu.registers.read(9)}")
    assert cpu.registers.read(9) == 10, "add instruction failed"
    print("add instruction test passed!")

def test_load_store_instructions():
    """Test lw and sw instructions"""
    print("\n=== Testing Load/Store Instructions ===")
    mem = Memory()
    cpu = CPU(mem)
    
    # Test program:
    # 1. addi $t0, $zero, 0x1000  -> Set base address (offset from 0x10000000)
    # 2. addi $t1, $zero, 0x42    -> Set value to store
    # 3. sw $t1, 0($t0)           -> Store 0x42 at address 0x10001000
    # 4. addi $t2, $zero, 0       -> Clear $t2
    # 5. lw $t2, 0($t0)           -> Load from address 0x10001000 to $t2
    
    instructions = [
        0x20081000,  # addi $t0, $zero, 0x1000
        0x20090042,  # addi $t1, $zero, 0x42
        0xAD090000,  # sw $t1, 0($t0)
        0x200A0000,  # addi $t2, $zero, 0
        0x8D0A0000   # lw $t2, 0($t0)
    ]
    
    addr = 0x00400000
    for i, instr in enumerate(instructions):
        mem.store_word(addr, instr)
        addr += 4
        print(f"Instruction {i} at 0x{addr-4:08x}: 0x{instr:08x}")
    
    # Execute all instructions
    cpu.run(5)
    
    # Verify memory and register values
    mem_addr = 0x10000000 + 0x1000
    mem_value = mem.load_word(mem_addr)
    print(f"Value in memory at 0x{mem_addr:08x} = 0x{mem_value:x}")
    print(f"$t2 (loaded value) = 0x{cpu.registers.read(10):x}")
    
    # Check results
    assert mem_value == 0x42, f"Store word failed. Expected 0x42, got 0x{mem_value:x}"
    assert cpu.registers.read(10) == 0x42, f"Load word failed. Expected 0x42, got 0x{cpu.registers.read(10):x}"
    
    print("Load/Store instructions test passed!")

def test_branch_instructions():
    """Test branch instructions (beq)"""
    print("\n=== Testing Branch Instructions ===")
    mem = Memory()
    cpu = CPU(mem)
    
    # Test beq instruction (branch if equal)
    # Program:
    # 1. addi $t0, $zero, 5   -> Set $t0 to 5
    # 2. addi $t1, $zero, 5   -> Set $t1 to 5
    # 3. beq $t0, $t1, 2      -> Branch if $t0 == $t1 (skips 2 instructions)
    # 4. addi $t2, $zero, 10  -> Should be skipped
    # 5. addi $t3, $zero, 20  -> Should be skipped
    # 6. addi $t4, $zero, 30  -> Should be executed
    
    instructions = [
        0x20080005,  # addi $t0, $zero, 5
        0x20090005,  # addi $t1, $zero, 5
        0x11090002,  # beq $t0, $t1, 2
        0x200A000A,  # addi $t2, $zero, 10
        0x200B0014,  # addi $t3, $zero, 20
        0x200C001E   # addi $t4, $zero, 30
    ]
    
    addr = 0x00400000
    for i, instr in enumerate(instructions):
        mem.store_word(addr, instr)
        addr += 4
        print(f"Instruction {i} at 0x{addr-4:08x}: 0x{instr:08x}")
    
    # Execute all instructions
    cpu.run(4)  # We need 4 cycles: 2 addi, 1 beq, 1 final addi
    
    # Check results
    print(f"$t0 = {cpu.registers.read(8)}, $t1 = {cpu.registers.read(9)}")
    print(f"$t2 = {cpu.registers.read(10)} (should be 0 if branch worked)")
    print(f"$t3 = {cpu.registers.read(11)} (should be 0 if branch worked)")
    print(f"$t4 = {cpu.registers.read(12)} (should be 30)")
    
    assert cpu.registers.read(10) == 0, "beq failed to skip instructions"
    assert cpu.registers.read(11) == 0, "beq failed to skip instructions"
    assert cpu.registers.read(12) == 30, "beq failed to continue execution after branch"
    
    print("Branch instructions test passed!")

def test_jump_and_function_calls():
    """Test jump instructions and function calls"""
    print("\n=== Testing Function Calls ===")
    mem = Memory()
    cpu = CPU(mem)
    
    # Simple function call example
    instructions = [
        0x20020000,  # addi $v0, $zero, 0 (initialize result)
        0x0C100003,  # jal function (at PC+12 bytes, which is 0x0040000C)
        0x08100005,  # j end
        # Function at 0x0040000C
        0x2002002A,  # addi $v0, $zero, 42 (set return value)
        0x03E00008,  # jr $ra (return to caller)
        # End at 0x00400014
    ]
    
    addr = 0x00400000
    for i, instr in enumerate(instructions):
        mem.store_word(addr, instr)
        addr += 4
        print(f"Instruction {i} at 0x{addr-4:08x}: 0x{instr:08x}")
    
    # Execute the entire function call sequence
    cpu.run(5)
    
    # Check result in $v0 (return value should be 42)
    print(f"Final $v0 value: {cpu.registers.read(2)}")
    assert cpu.registers.read(2) == 42, f"Function call test failed. $v0 = {cpu.registers.read(2)}, expected 42"
    print("Function call test passed!")

def test_bit_operations():
    """Test bitwise operations (and, or, xor, nor)"""
    print("\n=== Testing Bit Operations ===")
    mem = Memory()
    cpu = CPU(mem)
    
    instructions = [
        0x200800FF,  # addi $t0, $zero, 0xFF
        0x20090F0F,  # addi $t1, $zero, 0xF0F
        0x01095024,  # and $t2, $t0, $t1 (should be 0x0F)
        0x01095825,  # or $t3, $t0, $t1 (should be 0xFFF)
        0x01096026,  # xor $t4, $t0, $t1 (should be 0xFF0)
        0x01096827   # nor $t5, $t0, $t1 (should be 0xFFFFF000)
    ]
    
    addr = 0x00400000
    for i, instr in enumerate(instructions):
        mem.store_word(addr, instr)
        addr += 4
        print(f"Instruction {i} at 0x{addr-4:08x}: 0x{instr:08x}")
    
    cpu.run(6)
    
    # Print results
    print(f"$t0 = 0x{cpu.registers.read(8):x}, $t1 = 0x{cpu.registers.read(9):x}")
    print(f"AND result: 0x{cpu.registers.read(10):x} (should be 0x0F)")
    print(f"OR result: 0x{cpu.registers.read(11):x} (should be 0xFFF)")
    print(f"XOR result: 0x{cpu.registers.read(12):x} (should be 0xFF0)")
    print(f"NOR result: 0x{cpu.registers.read(13):x} (should be 0xFFFFF000)")
    
    # Check results
    assert cpu.registers.read(10) == 0x0F, f"and operation failed: got {cpu.registers.read(10):#x}, expected 0xF"
    assert cpu.registers.read(11) == 0xFFF, f"or operation failed: got {cpu.registers.read(11):#x}, expected 0xFFF"
    assert cpu.registers.read(12) == 0xFF0, f"xor operation failed: got {cpu.registers.read(12):#x}, expected 0xFF0"
    assert cpu.registers.read(13) & 0xFFFFFFFF == 0xFFFFF000, f"nor operation failed: got {cpu.registers.read(13):#x}, expected 0xFFFFF000"
    print("Bit operations test passed!")

def test_factorial():
    """Test complete factorial program execution"""
    print("\n=== Testing Factorial Program ===")
    mem = Memory()
    cpu = CPU(mem)
    
    # Load factorial program for n=5
    instructions = [
        0x20080005,  # addi $t0, $zero, 5 (n=5)
        0x20090001,  # addi $t1, $zero, 1 (result=1)
        0x11000004,  # beq $t0, $zero, 4 (if n==0, exit loop)
        0x01280018,  # mult $t1, $t0 (result * n)
        0x00004812,  # mflo $t1 (move result from lo register)
        0x2108FFFF,  # addi $t0, $t0, -1 (n--)
        0x08100002   # j 0x00400008 (jump to loop check)
    ]
    
    addr = 0x00400000
    for i, instr in enumerate(instructions):
        mem.store_word(addr, instr)
        addr += 4
        print(f"Instruction {i} at 0x{addr-4:08x}: 0x{instr:08x}")
    
    # Run for enough cycles to complete factorial calculation
    print("Running factorial program...")
    cpu.run(20)
    
    # Check result in $t1 (should be 120 for 5!)
    result = cpu.registers.read(9)
    print(f"Factorial result in $t1: {result}")
    assert result == 120, f"Factorial program failed. Got {result}, expected 120"
    print(f"Factorial program test passed! 5! = {result}")

def run_all_tests():
    """Run all tests for the MIPS simulator"""
    print("Starting MIPS simulator tests...")
    
    try:
        test_register_file()
        test_memory()
        test_basic_instructions()
        test_load_store_instructions()
        test_branch_instructions()
        test_jump_and_function_calls()
        test_bit_operations()
        test_factorial()
        
        print("\n=== All tests passed! The MIPS simulator is working correctly within its scope. ===")
    except AssertionError as e:
        print(f"\n=== Test failed: {e} ===")

if __name__ == "__main__":
    run_all_tests() 