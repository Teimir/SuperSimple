# Simple C-Style Language

A minimal, educational C-style programming language with support for:
- 32-bit unsigned integers as the only data type
- Functions with parameters and return values
- For and while loops
- Conditional statements (if/else)
- Arithmetic and logical operations

## Documentation

See [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) for complete language specification and grammar.

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

Several example programs are included in the `examples/` directory:

### Basic Examples
- `simple.sc` - Basic arithmetic and variables
- `factorial.sc` - Factorial calculation using while loop
- `fibonacci.sc` - Fibonacci sequence calculation
- `sum_range.sc` - Sum of numbers using for loop
- `nested_loops.sc` - Nested for loops example
- `gcd.sc` - Greatest Common Divisor using Euclidean algorithm

### Advanced Examples
- `overflow.sc` - Test integer overflow/wrap-around behavior
- `recursion.sc` - Recursive factorial and Fibonacci examples
- `scope_test.sc` - Variable shadowing and scope testing
- `operator_precedence.sc` - Complex expressions testing operator precedence
- `complex_nested.sc` - Complex nested structures (nested loops, nested ifs)
- `prefix_vs_postfix.sc` - Demonstrate prefix vs postfix increment/decrement
- `logical_operators.sc` - Comprehensive logical operator tests
- `relational_operators.sc` - All relational operators tests

### Include Examples
- `include_example.sc` - Basic include directive example
- `nested_include.sc` - Multiple nested includes example
- `utils.sc` - Utility functions library (for includes)
- `math_ops.sc` - Math operations library (for includes)

## Project Structure

- `lexer.py` - Tokenizer that converts source code to tokens
- `parser.py` - Parser that builds an Abstract Syntax Tree (AST)
- `interpreter.py` - Interpreter that executes the AST
- `preprocessor.py` - Preprocessor that handles #include directives
- `main.py` - Main entry point
- `LANGUAGE_SPEC.md` - Complete language specification
- `examples/` - Example programs
- `test/` - Test programs

### Test Files
- `test_lexer.py` - Unit tests for the lexer
- `test_parser.py` - Unit tests for the parser
- `test_interpreter.py` - Unit tests for the interpreter
- `test_preprocessor.py` - Unit tests for the preprocessor
- `run_tests.py` - Test runner script

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

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Increment/Decrement: `++`, `--` (both prefix and postfix)
- Relational: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical: `&&`, `||`, `!`

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
python run_tests.py
```

Or run individual test files:

```bash
python -m unittest test_lexer
python -m unittest test_parser
python -m unittest test_interpreter
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

## License

This is an educational project.
