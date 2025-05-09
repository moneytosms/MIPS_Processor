# MIPS Processor Simulator

A Python-based simulator for a MIPS processor that supports various instruction types:

- R-type (add, sub, sll, slt, xor, or, nor, and, jr)
- I-type (addi, lw, sw, beq, bne)
- J-type (j, jal)

## Features

- Simulates 32 general-purpose MIPS registers
- Supports stack operations
- Implements memory hierarchy
- Supports jr $ra for function returns
- Interactive menu interface

## Usage

Run the simulator from the command line:

```bash
python proj2.py
```

### Menu Options

1. Load instructions (as hex words)
2. Execute cycles
3. Show all registers
4. Help - Learn about MIPS
5. Exit

## Example: Factorial Calculation

To calculate factorial of 5, enter these instructions:

```
0x20080005 0x20090001 0x11000004 0x01280018 0x00004812 0x2108FFFF 0x08100002
```

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
