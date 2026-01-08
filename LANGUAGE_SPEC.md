# Simple C-Style Language Specification

## Overview

This is a simple, C-style programming language with a minimal feature set. The language is designed for educational purposes and focuses on core programming concepts with a restricted type system.

## Key Features

- **Single Data Type**: Only 32-bit unsigned integers (`uint32`) are supported
- **Functions**: User-defined functions with parameters and return values
- **Control Flow**: `for` and `while` loops
- **Expressions**: Arithmetic and logical operations
- **Statements**: Variable declarations, assignments, function calls, and control flow

## Data Types

### Unsigned 32-bit Integer (uint32)

The only data type in the language. All variables, function parameters, and return values are implicitly `uint32`.

- Range: 0 to 4,294,967,295 (2^32 - 1)
- Overflow behavior: Wraps around (modulo 2^32)

## Lexical Elements

### Identifiers

- Must start with a letter or underscore
- Can contain letters, digits, and underscores
- Case-sensitive
- Examples: `x`, `myVar`, `_count`, `counter123`

### Literals

- Integer literals: sequences of digits (0-9)
- Examples: `0`, `42`, `1000`, `4294967295`

### Keywords

```
uint32    (type keyword, though all types are uint32)
function  (function declaration)
for       (for loop)
while     (while loop)
if        (conditional statement)
else      (else clause)
return    (return statement)
```

### Operators

**Arithmetic:**
- `+` (addition)
- `-` (subtraction)
- `*` (multiplication)
- `/` (integer division)
- `%` (modulo)

**Relational:**
- `==` (equality)
- `!=` (inequality)
- `<` (less than)
- `<=` (less than or equal)
- `>` (greater than)
- `>=` (greater than or equal)

**Logical:**
- `&&` (logical AND)
- `||` (logical OR)
- `!` (logical NOT)

**Assignment:**
- `=` (assignment)

### Punctuation

- `;` (semicolon - statement terminator)
- `,` (comma - parameter/argument separator)
- `(` `)` (parentheses - grouping, function calls, parameters)
- `{` `}` (braces - block delimiters)

### Comments

- Single-line comments: `// comment text`
- Multi-line comments: `/* comment text */`

## Syntax

### Program Structure

A program consists of a series of function definitions. The entry point is the `main` function, which takes no parameters.

```c
function main() {
    // program code
}
```

### Variable Declaration

Variables must be declared with the `uint32` keyword before use.

```c
uint32 x;
uint32 y = 42;
uint32 z = x + y;
```

### Assignment

Variables are assigned using the `=` operator.

```c
x = 10;
x = x + 1;
x = y * 2;
```

### Expressions

Expressions combine literals, variables, and operators. Operator precedence follows standard C rules:
1. Parentheses
2. Unary operators (`!`, `-`)
3. Multiplicative (`*`, `/`, `%`)
4. Additive (`+`, `-`)
5. Relational (`<`, `<=`, `>`, `>=`)
6. Equality (`==`, `!=`)
7. Logical AND (`&&`)
8. Logical OR (`||`)

### Functions

Functions are declared with the `function` keyword, followed by the function name, parameters, and body.

```c
function functionName(param1, param2, ...) {
    // function body
    return value;
}
```

- Function names follow identifier rules
- Parameters are implicitly `uint32` (do not include `uint32` keyword in parameter list)
- Functions can return a value using `return`
- If no return statement is executed, the function returns 0
- Functions can be called before they are defined (forward declaration support)

### Conditional Statements

```c
if (condition) {
    // statements
}

if (condition) {
    // statements
} else {
    // statements
}
```

### While Loop

```c
while (condition) {
    // statements
}
```

### For Loop

The `for` loop follows C-style syntax:

```c
for (initialization; condition; increment) {
    // statements
}
```

- `initialization`: executed once before the loop (typically variable assignment)
- `condition`: evaluated before each iteration
- `increment`: executed after each iteration (typically variable update)

Example:
```c
for (uint32 i = 0; i < 10; i = i + 1) {
    // loop body
}
```

## Grammar (BNF-like)

```
program        := function_def*
function_def   := 'function' IDENTIFIER '(' param_list? ')' '{' statement* '}'
param_list     := IDENTIFIER (',' IDENTIFIER)*

statement      := var_decl ';'
                | assignment ';'
                | function_call ';'
                | return_stmt ';'
                | if_stmt
                | while_stmt
                | for_stmt
                | block

var_decl       := 'uint32' IDENTIFIER ('=' expression)?
assignment     := IDENTIFIER '=' expression
function_call  := IDENTIFIER '(' expr_list? ')'
return_stmt    := 'return' expression?

if_stmt        := 'if' '(' expression ')' statement ('else' statement)?
while_stmt     := 'while' '(' expression ')' statement
for_stmt       := 'for' '(' (var_decl | assignment)? ';' expression? ';' assignment? ')' statement

block          := '{' statement* '}'
expr_list      := expression (',' expression)*

expression     := logical_or
logical_or     := logical_and ('||' logical_and)*
logical_and    := equality ('&&' equality)*
equality       := relational (('==' | '!=') relational)*
relational     := additive (('<' | '<=' | '>' | '>=') additive)*
additive       := multiplicative (('+' | '-') multiplicative)*
multiplicative := unary (('*' | '/' | '%') unary)*
unary          := ('!' | '-') unary | primary
primary        := IDENTIFIER
                | LITERAL
                | '(' expression ')'
                | function_call
```

## Examples

### Example 1: Simple Program

```c
function main() {
    uint32 x = 10;
    uint32 y = 20;
    uint32 sum = x + y;
    return sum;
}
```

### Example 2: Factorial Function

```c
function factorial(n) {
    if (n == 0 || n == 1) {
        return 1;
    }
    uint32 result = 1;
    uint32 i = 2;
    while (i <= n) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

function main() {
    uint32 n = 5;
    uint32 fact = factorial(n);
    return fact;  // returns 120
}
```

### Example 3: For Loop Example

```c
function sum_range(start, end) {
    uint32 sum = 0;
    uint32 i;
    for (i = start; i <= end; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

function main() {
    uint32 result = sum_range(1, 10);
    return result;  // returns 55
}
```

### Example 4: Nested Loops

```c
function main() {
    uint32 result = 0;
    uint32 i;
    uint32 j;
    for (i = 0; i < 5; i = i + 1) {
        for (j = 0; j < 3; j = j + 1) {
            result = result + 1;
        }
    }
    return result;  // returns 15
}
```

### Example 5: Fibonacci

```c
function fibonacci(n) {
    if (n == 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    uint32 a = 0;
    uint32 b = 1;
    uint32 i = 2;
    while (i <= n) {
        uint32 temp = a + b;
        a = b;
        b = temp;
        i = i + 1;
    }
    return b;
}

function main() {
    return fibonacci(10);  // returns 55
}
```

## Implementation Notes

### Integer Overflow

Since we're working with 32-bit unsigned integers, overflow wraps around:
- `4294967295 + 1 = 0`
- `0 - 1 = 4294967295`

### Division by Zero

Division by zero should result in an error or undefined behavior (implementation-dependent).

### Variable Scope

- Variables are block-scoped
- Function parameters are scoped to the function body
- Variables in inner scopes shadow outer scope variables

### Evaluation Order

- Function arguments are evaluated left-to-right
- Logical operators use short-circuit evaluation (`&&` and `||`)
- For loop: initialization → condition check → body → increment → condition check (repeat)

## Error Handling

The language should report errors for:
- Undefined variables
- Type mismatches (not applicable since all are uint32, but structure errors)
- Undefined functions
- Syntax errors
- Division by zero (runtime error)
