# Examples Directory

This directory contains example programs organized by category.

## Directory Structure

### `basic/`
Basic programming examples:
- `sum_range.sc` - Sum of numbers using for loop
- `nested_loops.sc` - Nested for loops example
- `hello_world/hello_world.sc` - Hello World example (outputs "Hello World" to UART)
- `array_example.sc` - Basic array operations (declaration, initialization, access)
- `array_init_example.sc` - Array initialization with values
- `array_init_partial.sc` - Partial array initialization
- `pointer_example.sc` - Pointer operations (address-of, dereference, assignment)
- `array_pointer.sc` - Arrays and pointers together
- `pointer_function.sc` - Passing pointers to functions
- `array_sum.sc` - Calculate sum of array elements using pointer arithmetic

### `hardware/`
Hardware-specific examples for MCU programming:
- `register_test.sc` - Register variable access
- `volatile_test.sc` - Volatile variables
- `gpio_blink.sc` - GPIO LED blink example
- `uart_echo.sc` - UART echo example
- `timer_example.sc` - Timer usage example
- `interrupt_example.sc` - Timer interrupt example
- `bit_manipulation.sc` - Bit manipulation functions
- `bit_test_simple.sc` - Simple bit manipulation test
- `gpio.h`, `uart.h`, `timer.h`, `hardware.h` - Hardware header files

### `operators/`
Operator testing examples:
- `logical_operators.sc` - Logical operators (&&, ||, !)
- `relational_operators.sc` - Relational operators (==, !=, <, <=, >, >=)
- `operator_precedence.sc` - Operator precedence testing
- `prefix_vs_postfix.sc` - Prefix vs postfix increment/decrement
- `increment_test.sc` - Increment/decrement operators

### `includes/`
File include examples:
- `include_example.sc` - Basic include directive
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
- `for_increment.sc` - For loop with increment operator
- `for_decrement.sc` - For loop with decrement operator

## Running Examples

Run any example with:
```bash
python main.py examples/<category>/<filename>
```

Example:
```bash
python main.py examples/hardware/gpio_blink.sc
```
