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

- `simple.sc` - Basic arithmetic and variables
- `factorial.sc` - Factorial calculation using while loop
- `fibonacci.sc` - Fibonacci sequence calculation
- `sum_range.sc` - Sum of numbers using for loop
- `nested_loops.sc` - Nested for loops example
- `gcd.sc` - Greatest Common Divisor using Euclidean algorithm

## Project Structure

- `lexer.py` - Tokenizer that converts source code to tokens
- `parser.py` - Parser that builds an Abstract Syntax Tree (AST)
- `interpreter.py` - Interpreter that executes the AST
- `main.py` - Main entry point
- `LANGUAGE_SPEC.md` - Complete language specification
- `examples/` - Example programs

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

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
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

## Limitations

- No arrays or pointers
- No strings or characters
- No floating-point numbers
- Single data type only (uint32)
- Division by zero causes runtime error
- Integer overflow wraps around (modulo 2^32)

## License

This is an educational project.
