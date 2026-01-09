# Simple C-Style Language

A minimal, educational C-style programming language with support for:
- 32-bit unsigned integers as the only data type
- Functions with parameters and return values
- For and while loops
- Conditional statements (if/else)
- Arithmetic and logical operations

## Documentation

- **[doc/LANGUAGE_SPEC.md](doc/LANGUAGE_SPEC.md)** - Complete language specification and grammar
- **[doc/ARCHITECTURE.md](doc/ARCHITECTURE.md)** - System architecture and design overview
- **[doc/INCLUDE_MECHANISM.md](doc/INCLUDE_MECHANISM.md)** - Detailed explanation of how `#include` directives work
- **[doc/CONTRIBUTING.md](doc/CONTRIBUTING.md)** - Development guidelines and contribution instructions
- **[doc/PROJECT_STRUCTURE.md](doc/PROJECT_STRUCTURE.md)** - Project file organization
- **[doc/CODE_GENERATION.md](doc/CODE_GENERATION.md)** - Code generation and assembly translation details
- **[examples/README.md](examples/README.md)** - Examples directory structure and descriptions

### LaTeX Documentation

- **[documentation.tex](documentation.tex)** - Полная документация проекта в формате LaTeX (на русском языке)
- **[COMPILATION_INSTRUCTIONS.md](COMPILATION_INSTRUCTIONS.md)** - Инструкции по компиляции LaTeX документации в PDF

Для компиляции в PDF рекомендуется использовать [Overleaf](https://www.overleaf.com/) или другие онлайн-сервисы (см. инструкции выше).

## Installation

Requires Python 3.7 or higher. No additional dependencies needed.

## Usage

Run a program:

```bash
python main.py <source_file>
```

The program will execute and print the return value from the `main` function.

Example:

```bash
python main.py examples/factorial.sc
```

## Examples

Example programs are organized in the `examples/` directory by category:

### Basic Examples (`examples/basic/`)
- `sum_range.sc` - Sum of numbers using for loop
- `nested_loops.sc` - Nested for loops example
- `hello_world/hello_world.sc` - Hello World example (outputs to UART)

### Hardware Examples (`examples/hardware/`)
- `register_test.sc` - Register variable access
- `volatile_test.sc` - Volatile variables
- `gpio_blink.sc` - GPIO LED blink example
- `uart_echo.sc` - UART echo example
- `timer_example.sc` - Timer usage example
- `interrupt_example.sc` - Timer interrupt example
- `bit_manipulation.sc` - Bit manipulation functions
- Header files: `gpio.h`, `uart.h`, `timer.h`, `hardware.h`

### Operator Examples (`examples/operators/`)
- `logical_operators.sc` - Logical operators tests
- `relational_operators.sc` - Relational operators tests
- `operator_precedence.sc` - Operator precedence testing
- `prefix_vs_postfix.sc` - Prefix vs postfix increment/decrement
- `increment_test.sc` - Increment/decrement operators

### Include Examples (`examples/includes/`)
- `include_example.sc` - Basic include directive
- `nested_include.sc` - Nested includes
- `circular_a.sc`, `circular_b.sc` - Circular include tests
- `utils.sc` - Utility functions library
- `math_ops.sc` - Math operations library

### Advanced Examples (`examples/advanced/`)
- `fibonacci.sc` - Fibonacci sequence
- `recursion.sc` - Recursive functions
- `gcd.sc` - Greatest Common Divisor
- `scope_test.sc` - Variable scoping
- `complex_nested.sc` - Complex nested structures
- `overflow.sc` - Integer overflow testing
- `for_increment.sc` - For loop with increment
- `for_decrement.sc` - For loop with decrement

See `examples/README.md` for detailed descriptions.

## Compilation

Compile a source file to FASM assembly, then to binary:

```bash
python compile.py <source_file> [output_file] [--run]
```

Options:
- `output_file` - Optional output `.asm` file path (default: `<source_file>.asm`)
- `--run` - After compilation, run the binary using `interpreter_x64.exe` from `int_pack`

Examples:
```bash
# Compile to assembly and binary
python compile.py examples/basic/sum_range.sc

# Compile and run
python compile.py examples/basic/sum_range.sc --run
```

This generates:
- `.asm` file - FASM assembly source
- `.bin` file - Binary executable (compiled with `int_pack/FASM.EXE`)
- `.mif` file - Memory Initialization File for Quartus

The compiler uses `int_pack/FASM.EXE` to compile assembly and `int_pack/interpreter_x64.exe` to run binaries.
The `int_pack/ISA.inc` file is automatically included in generated assembly files.

See [doc/CODE_GENERATION.md](doc/CODE_GENERATION.md) for details on code generation.

## Project Structure

```
aiproj/
├── main.py                 # Main entry point
├── lexer.py                # Tokenizer (source → tokens)
├── parser.py               # Parser (tokens → AST)
├── interpreter.py          # Interpreter (AST → execution)
├── preprocessor.py         # Preprocessor (#include handling)
├── codegen.py              # Code generator (AST → assembly)
├── compile.py              # Compilation script
│
├── README.md               # This file
│
├── examples/               # Example programs
│   ├── basic/             # Basic programming examples
│   │   └── hello_world/   # Hello World example
│   ├── hardware/          # Hardware/MCU examples
│   ├── operators/         # Operator testing examples
│   ├── includes/          # Include directive examples
│   └── advanced/          # Advanced programming examples
│
├── user_examples/          # User example programs
│   ├── simple_return/     # Simple return example
│   ├── complex_example/   # Complex example with functions
│   └── test_example/      # Test example
│
├── self_tests/            # Unit tests
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   ├── test_preprocessor.py
│   └── run_tests.py       # Test runner
│
└── doc/                   # Documentation files
    ├── LANGUAGE_SPEC.md
    ├── ARCHITECTURE.md
    ├── CODE_GENERATION.md
    ├── CONTRIBUTING.md
    ├── INCLUDE_MECHANISM.md
    └── PROJECT_STRUCTURE.md
```

### Core Components

- **`lexer.py`** - Converts source code into a stream of tokens
- **`parser.py`** - Builds an Abstract Syntax Tree (AST) from tokens
- **`interpreter.py`** - Executes the AST and manages runtime state
- **`preprocessor.py`** - Handles `#include` directives before lexing
- **`main.py`** - Orchestrates the compilation pipeline

## Features

### Data Types
- Only `uint32` (32-bit unsigned integer): range 0 to 4,294,967,295

### Control Flow
- `if` / `else` statements
- `while` loops
- `for` loops (C-style: `for (init; condition; increment)`)

### Functions
- Function definitions with parameters
- Return values
- Recursion supported

### File Includes
- `#include "filename"` or `#include <filename>` directives
- Supports nested includes
- Circular include detection
- Relative path resolution

### Hardware Support
- **Register Access**: Direct CPU register access (r0-r31)
- **GPIO**: Digital I/O operations (gpio_set, gpio_read, gpio_write)
- **UART**: Serial communication (uart_set_baud, uart_read, uart_write)
- **Timer**: Hardware timer control (timer_set_mode, timer_start, timer_stop, etc.)
- **Interrupts**: Interrupt service routines (ISRs)
- **Bit Manipulation**: Built-in bit operations (set_bit, clear_bit, toggle_bit, get_bit)
- **Delay Functions**: Software delays (delay_ms, delay_us, delay_cycles)

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Bitwise**: `&`, `|`, `^`, `~`, `<<`, `>>`
- **Increment/Decrement**: `++`, `--` (both prefix and postfix)
- **Relational**: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical**: `&&`, `||`, `!`

## Quick Example

```c
function add(uint32 a, uint32 b) {
    return a + b;
}

function main() {
    uint32 result = add(5, 3);
    return result;  // returns 8
}
```

## Testing

The project includes comprehensive unit tests for all components. Run all tests using:

```bash
python self_tests/run_tests.py
```

Or run individual test files:

```bash
python -m unittest self_tests.test_lexer
python -m unittest self_tests.test_parser
python -m unittest self_tests.test_interpreter
python -m unittest self_tests.test_preprocessor
```

### Test Coverage

- **Lexer Tests** (`test_lexer.py`): Token recognition, comment handling, whitespace, operators, error cases, line/column tracking
- **Parser Tests** (`test_parser.py`): Function definitions, variable declarations, all statement types, expression parsing, nested structures, error cases
- **Interpreter Tests** (`test_interpreter.py`): Arithmetic operations, variable scoping, function calls, control flow, increment/decrement, edge cases (overflow, division by zero, undefined variables/functions)
- **Preprocessor Tests** (`test_preprocessor.py`): Include directive handling, nested includes, circular include detection, path resolution

All tests use Python's built-in `unittest` framework - no external dependencies required.

## Limitations

- No arrays or pointers
- No strings or characters
- No floating-point numbers
- Single data type only (uint32)
- Division by zero causes runtime error
- Integer overflow wraps around (modulo 2^32)
- No `#define` macro support (only `#include` is supported)

## Development

See [doc/CONTRIBUTING.md](doc/CONTRIBUTING.md) for development guidelines and contribution instructions.

## License

This is an educational project.
