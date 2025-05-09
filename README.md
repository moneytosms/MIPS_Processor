# MIPS Simulator

A simple Python-based MIPS processor simulator that supports essential MIPS instructions and features.

## Overview

This simulator implements a basic MIPS architecture with:

- 32 general-purpose registers
- Memory model with text, data, and stack segments
- Support for core instruction types (R, I, and J)
- Function calls via `jal` and `jr $ra`
- Stack operations

## Memory Layout

The simulator uses the standard MIPS memory layout:

- `0x00400000`: Text segment (Code)
- `0x10000000`: Data segment (Global variables)
- `0x7fffffff`: Stack segment (grows downward)

## Supported Instructions

### R-type Instructions

- `add` - Add two registers
- `sub` - Subtract two registers
- `sll` - Shift left logical
- `slt` - Set less than
- `xor` - Exclusive OR
- `or` - Logical OR
- `nor` - Logical NOR
- `and` - Logical AND
- `jr` - Jump register
- `mult` - Multiply
- `div` - Divide
- `mflo` - Move from LO register

### I-type Instructions

- `addi` - Add immediate
- `lw` - Load word
- `sw` - Store word
- `beq` - Branch if equal
- `bne` - Branch if not equal

### J-type Instructions

- `j` - Jump
- `jal` - Jump and link (function calls)

## Usage

Run the simulator with Python:

```
python proj2.py
```

The interactive menu provides options to:

1. Load instructions as hex words
2. Execute a specified number of cycles
3. Show register contents
4. Access help information
5. Exit the simulator

## Example: Factorial Calculation

The following MIPS program calculates the factorial of 5:

```
0x20080005  # addi $t0, $zero, 5 (n=5)
0x20090001  # addi $t1, $zero, 1 (result=1)
0x11000004  # beq $t0, $zero, 4 (if n==0, exit loop)
0x01280018  # mult $t1, $t0 (result * n)
0x00004812  # mflo $t1 (move result from lo register)
0x2108FFFF  # addi $t0, $t0, -1 (n--)
0x08100002  # j 0x00400008 (jump to loop check)
```

To run this example:

1. Load these instructions using option 1
2. Execute with option 2 (20 cycles should be enough)
3. View the result in the registers with option 3 ($t1 should contain 120)

## Function Calls

The simulator supports nested function calls with stack management. For example:

```
# Save return address
addi $sp, $sp, -4
sw   $ra, 0($sp)

# Function body...

# Restore return address and return
lw   $ra, 0($sp)
addi $sp, $sp, 4
jr   $ra
```

## Testing

The simulator has been thoroughly tested with:

- Register operations
- Memory operations
- Basic arithmetic and logical operations
- Branch instructions
- Function calls
- Complex programs (e.g., factorial calculation)

## Learning Resources

For more information about MIPS architecture and assembly:

1. MIPS Reference Sheet: https://inst.eecs.berkeley.edu/~cs61c/resources/MIPS_Green_Sheet.pdf
2. MIPS Assembly Programming Tutorial: https://chortle.ccsu.edu/AssemblyTutorial/index.html
3. Book: 'See MIPS Run' by Dominic Sweetman
4. Book: 'Computer Organization and Design' by Patterson and Hennessy
