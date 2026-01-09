# Code Generation Documentation

## Overview

The code generator (`codegen.py`) translates the AST (Abstract Syntax Tree) into FASM assembly code targeting the ISA described in `isa/README.md`.

## Architecture

### Register Allocation

The code generator uses a simple fixed register allocation strategy:
- **r0-r10**: Temporary registers (for expression evaluation)
- **r11-r25**: Local variables
- **r26-r30**: Function parameters
- **r31**: Instruction pointer (read-only in user code, managed by hardware)

### Function Calling Convention

- Parameters passed in r26-r30 (up to 5 parameters)
- Return value in r0
- Link register: r30 (for return address, in proper implementation)

### Code Generation Pipeline

```
AST
  ↓
CodeGenerator.generate()
  ↓
RegisterAllocator (allocate registers)
  ↓
Generate assembly instructions
  ↓
FASM assembly file
```

## Implementation Status

### ✅ Implemented

- **Expressions**:
  - Literals
  - Identifiers/variables
  - Binary operations (add, sub, and, or, xor, shl, shr)
  - Unary operations (not, logical not, unary minus)
  - Comparison operations (==, !=, <, <=, >, >=)
  - Logical operations (&&, ||, !)
  
- **Statements**:
  - Variable declarations
  - Array declarations
  - Pointer declarations
  - Array element assignments
  - Pointer dereference assignments
  - Assignments
  - Return statements
  - Blocks
  
- **Hardware Functions**:
  - GPIO (gpio_set, gpio_read, gpio_write)
  - UART (uart_set_baud, uart_read, uart_write)
  
- **Functions**:
  - Function definitions
  - Function calls (simplified)

### ⚠️ Partially Implemented / Limitations

- **Function Calls**: 
  - Parameters and return values work
  - But proper call/return mechanism requires jump instructions
  - Currently simplified (functions must be sequential)
  
- **Control Flow**:
  - **If statements**: Generated but conditional jumps not implemented
  - **While loops**: Generated but loop control not implemented
  - **For loops**: Generated but loop control not implemented
  - Proper implementation requires using r31 (instruction pointer) for jumps

- **Operations**:
  - Division (`/`): Not implemented (not in ISA)
  - Modulo (`%`): Not implemented (not in ISA)
  - Multiplication (`*`): Simplified (would need proper implementation)

## ISA Mapping

### Arithmetic Operations

| Language | ISA Instruction | Format |
|----------|----------------|--------|
| `a + b` | `add r0, r1, r2` | 3-operand |
| `a - b` | `sub r0, r1, r2` | 3-operand |
| `a * b` | (repeated add - simplified) | - |
| `a / b` | Not supported | - |

### Bitwise Operations

| Language | ISA Instruction | Format |
|----------|----------------|--------|
| `a & b` | `and r0, r1, r2` | 3-operand |
| `a \| b` | `or r0, r1, r2` | 3-operand |
| `a ^ b` | `xor r0, r1, r2` | 3-operand |
| `~a` | `not r0, r1` | 2-operand |
| `a << b` | `shl r0, r1, r2` | 3-operand |
| `a >> b` | `shr r0, r1, r2` | 3-operand |

### Comparison Operations

| Language | ISA Instruction | Format |
|----------|----------------|--------|
| `a == b` | `cmpe r0, r1, r2` | 3-operand |
| `a != b` | `cmpe` + invert | - |
| `a > b` | `cmpa r0, r1, r2` | 3-operand |
| `a < b` | `cmpb r0, r1, r2` | 3-operand |
| `a >= b` | `cmpa` + invert | - |
| `a <= b` | `cmpb` + invert | - |

### Hardware Functions

| Language Function | ISA Instructions | Notes |
|-------------------|------------------|-------|
| `gpio_set(pin, dir, mode)` | `shl`, `or`, `setg` | Pack parameters |
| `gpio_read(pin)` | `getg` | - |
| `gpio_write(pin, value)` | `shl`, `or`, `outg` | Pack parameters |
| `uart_set_baud(baud)` | `setu` | - |
| `uart_read()` | `inu` | - |
| `uart_write(data)` | `outu` | - |

### Arrays and Pointers

**Array Declaration:**
- **Local arrays**: Allocated on stack using `sub r:30, r:30, size`
- **Global arrays**: Allocated in data section with label and `dd 0` for each element

**Array Access (`arr[index]`):**
1. Calculate address: `base_addr + index` (each element = 1 memory cell)
2. Load value: `lds result_reg, [addr_reg]`

**Array Assignment (`arr[i] = value`):**
1. Calculate address: `base_addr + index`
2. Store value: `lds [addr_reg], value_reg`

**Address-of (`&x`, `&arr[i]`):**
- For variables: Get address from `variable_addresses` (label or stack offset)
- For arrays: Get base address from `array_addresses`
- For array elements: Calculate `base_addr + index`

**Dereference (`*ptr`):**
1. Evaluate pointer expression to get address in register
2. Load value: `lds result_reg, [addr_reg]`

**Pointer Assignment (`*ptr = value`):**
1. Evaluate pointer expression to get address
2. Store value: `lds [addr_reg], value_reg`

**Pointer Arithmetic:**
- `ptr + i`: `add result_reg, ptr_reg, i_reg` (each element = 1 memory cell)
- `ptr - i`: `sub result_reg, ptr_reg, i_reg`
- `ptr1 - ptr2`: `sub result_reg, ptr1_reg, ptr2_reg`

## Example Generated Code

### Simple Addition

**Source** (`add.sc`):
```c
function main() {
    uint32 a = 5;
    uint32 b = 3;
    uint32 c = a + b;
    return c;
}
```

**Generated Assembly** (`add.asm`):
```asm
include "../../int_pack/ISA.inc"

func_main:
	; Function: main
	mov r11, 5
	mov r12, 3
	add r0, r11, r12
	mov r13, r0
	mov r0, r13
	hlt
```

Note: The `format binary` directive and ISA definitions are included from `int_pack/ISA.inc`.

### GPIO Blink

**Source** (`gpio_blink.sc`):
```c
function main() {
    gpio_set(0, 1, 2);
    uint32 i;
    for (i = 0; i < 10; i++) {
        gpio_write(0, 1);
        gpio_write(0, 0);
    }
    return 0;
}
```

**Generated Assembly** (simplified):
```asm
func_main:
	; GPIO setup
	mov r1, 0
	mov r2, 1
	mov r3, 2
	shl r4, r1, 16
	shl r5, r2, 8
	or r4, r4, r5
	or r4, r4, r3
	setg r4
	
	; Loop initialization
	mov r11, 0
for_start_0:
	; Loop condition check (i < 10)
	; ... comparison code ...
	
	; GPIO write HIGH
	; ... gpio_write(0, 1) ...
	
	; GPIO write LOW
	; ... gpio_write(0, 0) ...
	
	; Loop increment
	add r11, r11, 1
	
	; Loop back (requires proper jump)
for_end_1:
	mov r0, 0
	hlt
```

## Known Issues and TODOs

### High Priority

1. ✅ **Implement Conditional Jumps**: 
   - ✅ Use r31 (instruction pointer) for jumps
   - ✅ Implement proper if/else with conditional jumps using `cmovz r31, condition, addr label`
   - ✅ Implement proper while/for loops using `mov r31, addr label` and `cmovz r31, condition, addr label`

2. ✅ **Implement Function Call/Return**:
   - ✅ Save return address in r30 (link register)
   - ✅ Jump to function using `mov r31, addr func_label`
   - ✅ Return using `mov r31, r30`

3. **Handle Division/Modulo**:
   - Either implement via software (loop with subtraction)
   - Or add to ISA (if needed)

### Medium Priority

1. **Improve Register Allocation**:
   - Implement proper register spilling (use memory/stack)
   - Handle register pressure better

2. **Optimize Code Generation**:
   - Constant folding
   - Dead code elimination
   - Better instruction selection

3. **Support More Hardware Functions**:
   - Timer functions
   - Interrupt handling
   - Memory operations

### Low Priority

1. **Better Error Messages**: 
   - More specific code generation errors
   - Line number mapping

2. **Debug Information**:
   - Source line annotations in generated code
   - Variable name mappings

## Usage

### Compilation

Compile a source file to assembly and binary:
```bash
python compile.py source.sc [output.asm] [--run]
```

The compiler automatically:
1. Generates FASM assembly (`.asm` file)
2. Compiles with `int_pack/FASM.EXE` to produce:
   - `.bin` file (binary executable)
   - `.mif` file (Memory Initialization File for Quartus)

Options:
- `output.asm` - Optional output assembly file path (default: `<source>.asm`)
- `--run` - After compilation, run the binary using `int_pack/interpreter_x64.exe`

Examples:
```bash
# Compile to assembly and binary
python compile.py test_examples/basic/sum_range.sc

# Compile and run
python compile.py test_examples/basic/sum_range.sc --run
```

### Manual Compilation

If you want to compile manually:
```bash
int_pack/FASM.EXE test_examples/basic/sum_range.asm
```

This will generate `.bin` and `.mif` files in the same directory as the `.asm` file.

### Running Binaries

Run a compiled binary:
```bash
int_pack/interpreter_x64.exe test_examples/basic/sum_range.bin
```

The interpreter executes the binary and prints register states at the end.

## Future Improvements

1. ✅ **Proper Jump Implementation**: 
   - ✅ Use labels with proper address resolution (`addr label`)
   - ✅ Implement conditional jumps using `cmovz r31, condition, addr label`

2. **Stack Support**:
   - For function calls with more than 5 parameters
   - For local variable spilling
   - For recursive functions

3. **Optimization Passes**:
   - Register allocation optimization
   - Instruction scheduling
   - Constant propagation
   - Dead code elimination

4. **Full ISA Support**:
   - Memory operations (inm, outm, lds)
   - All peripheral operations
   - Interrupt handling
