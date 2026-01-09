# Test Examples Directory

This directory contains test example programs organized by category.

## Directory Structure

### `basic/`
Basic programming examples:
- `hello_world/hello_world.sc` - Hello World example (outputs "Hello World" to UART)
- `arrays.sc` - Comprehensive array operations (declaration, initialization, access, partial init)
- `sum_range.sc` - Sum of numbers using for loop
- `nested_loops.sc` - Nested for loops example
- `pointer_example.sc` - Pointer operations (address-of, dereference, assignment)
- `array_pointer.sc` - Arrays and pointers together
- `pointer_function.sc` - Passing pointers to functions
- `array_sum.sc` - Calculate sum of array elements using pointer arithmetic

### `operators/`
Operator testing examples:
- `hex_literals.sc` - Hexadecimal literal values
- `relational_operators.sc` - Relational operators (==, !=, <, <=, >, >=)
- `operator_precedence.sc` - Operator precedence testing
- `increment_decrement.sc` - Increment/decrement operators (prefix and postfix)

### `hardware/`
Hardware-specific examples for MCU programming:
- `gpio_blink.sc` - GPIO LED blink example
- `uart_echo.sc` - UART echo example
- `timer_example.sc` - Timer usage example
- `interrupt_example.sc` - Timer interrupt example
- `bit_manipulation.sc` - Bit manipulation functions
- `bit_test_simple.sc` - Simple bit manipulation test
- `volatile_test.sc` - Volatile variables
- `gpio.h`, `uart.h`, `timer.h`, `hardware.h` - Hardware header files

### `includes/`
File include examples:
- `nested_include.sc` - Nested includes
- `circular_a.sc`, `circular_b.sc` - Circular include test files
- `utils.sc` - Utility functions library
- `math_ops.sc` - Math operations library

### `advanced/`
Advanced programming examples:
- `fibonacci.sc` - Fibonacci sequence
- `recursion.sc` - Recursive functions
- `gcd.sc` - Greatest Common Divisor
- `scope_test.sc` - Variable scoping
- `complex_nested.sc` - Complex nested structures
- `overflow.sc` - Integer overflow testing
- `for_loops.sc` - For loops with increment and decrement

### `math_test/`
Math library testing:
- `test_div_simple.sc` - Simple division test
- `test6.sc` - Complex math operations
- `div_lib.sc` - Division library

### `complex_example/`
Complex example combining multiple features:
- `complex_example.sc` - Complex program with multiple features

### `uart_message/`
UART message output examples:
- `test5.sc` - Complex UART message example

### `uart_number/`
UART number output examples:
- `uart_number.sc` - Output a predefined number to UART (extracts digits using loops)
- `uart_number_div.sc` - UART number output using division
- `t.sc`, `t2.sc` - Test examples for UART number output
- Various test files for debugging and development

## Running Examples

### Using Python Interpreter:
```bash
python main.py test_examples/<category>/<filename>
```

### Using Compiler:
```bash
python compile.py test_examples/<category>/<filename>
```

### Compile and Run:
```bash
python compile.py test_examples/<category>/<filename> --run
```

## Examples

### Basic Example:
```bash
python main.py test_examples/basic/hello_world/hello_world.sc
python compile.py test_examples/basic/hello_world/hello_world.sc --run
```

### Hardware Example:
```bash
python compile.py test_examples/hardware/gpio_blink.sc --run
```

## Notes

- All arrays are now allocated in memory (not on stack) for better performance and simpler code generation
- r:30 is used as stack pointer for local variables only
- Generated files (.asm, .bin, .mif) are ignored by git and can be regenerated
