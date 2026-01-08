# Architecture Overview

This document describes the architecture and design of the Simple C-Style Language interpreter.

## Compilation Pipeline

The language follows a traditional compiler/interpreter pipeline:

```
Source File (.sc)
    ↓
[Preprocessor]  # Handles #include directives
    ↓
Source Code (with includes expanded)
    ↓
[Lexer]         # Tokenization
    ↓
Token Stream
    ↓
[Parser]        # Syntax analysis
    ↓
Abstract Syntax Tree (AST)
    ↓
[Interpreter]   # Execution
    ↓
Program Result
```

## Component Details

### 1. Preprocessor (`preprocessor.py`)

**Purpose**: Handles `#include` directives before lexing.

**Key Features**:
- Recursive file inclusion
- Circular dependency detection
- Path resolution (relative and absolute)
- Comment injection for debugging

**Classes**:
- `Preprocessor` - Main preprocessing class
- `PreprocessingError` - Exception for preprocessing errors

**Methods**:
- `preprocess(filepath)` - Main entry point
- `process_file(filepath)` - Process a single file
- `process_content(content)` - Process source content
- `resolve_path(filename, current_dir)` - Resolve include paths

### 2. Lexer (`lexer.py`)

**Purpose**: Converts source code into a stream of tokens.

**Key Features**:
- Token recognition for all language elements
- Line and column tracking for error reporting
- Comment handling (single-line and multi-line)
- Whitespace handling

**Classes**:
- `TokenType` - Enumeration of all token types
- `Token` - Token with type, value, line, and column
- `Lexer` - Main lexer class

**Token Categories**:
- Keywords: `function`, `uint32`, `if`, `else`, `while`, `for`, `return`, etc.
- Operators: Arithmetic, logical, relational, bitwise
- Punctuation: `;`, `,`, `(`, `)`, `{`, `}`
- Literals: Integer literals
- Identifiers: Variable and function names

### 3. Parser (`parser.py`)

**Purpose**: Builds an Abstract Syntax Tree (AST) from tokens.

**Key Features**:
- Recursive descent parsing
- Operator precedence handling
- Expression parsing with proper associativity
- Statement parsing (declarations, assignments, control flow)

**AST Node Types**:
- `Program` - Root node containing all functions
- `FunctionDef` - Function definition
- `VarDecl` - Variable declaration
- `Assignment` - Variable assignment
- `IfStmt` - If/else statement
- `WhileStmt` - While loop
- `ForStmt` - For loop
- `ReturnStmt` - Return statement
- `Block` - Code block
- `BinaryOp` - Binary operation
- `UnaryOp` - Unary operation
- `FunctionCall` - Function call
- `Identifier` - Variable reference
- `Literal` - Integer literal

**Parsing Methods**:
- `parse()` - Main entry point
- `parse_function()` - Parse function definition
- `parse_statement()` - Parse a statement
- `parse_expression()` - Parse an expression (with precedence)
- Various expression parsers for different precedence levels

### 4. Interpreter (`interpreter.py`)

**Purpose**: Executes the AST and manages runtime state.

**Key Features**:
- Environment management (variable scoping)
- Function call handling
- Control flow execution
- Built-in hardware functions
- Register simulation
- Interrupt handling

**Classes**:
- `Environment` - Variable scope management
- `Interpreter` - Main interpreter class
- `RuntimeError` - Runtime exception

**Runtime State**:
- `global_env` - Global variable environment
- `functions` - Function definitions
- `registers` - CPU register simulation (32 registers)
- `register_map` - Mapping from register names to indices
- `interrupt_handlers` - Interrupt service routines
- Hardware state (GPIO, UART, Timer)

**Execution Methods**:
- `interpret()` - Main entry point
- `execute_statement()` - Execute a statement
- `evaluate_expression()` - Evaluate an expression
- `execute_function()` - Execute a function call
- Various hardware function implementations

## Data Flow

### Variable Declaration
```
VarDecl AST Node
    ↓
execute_var_decl()
    ↓
Environment.declare()
    ↓
Variable stored in environment
```

### Function Call
```
FunctionCall AST Node
    ↓
evaluate_expression()
    ↓
execute_function()
    ↓
Create new environment for parameters
    ↓
Execute function body
    ↓
Return value
```

### Control Flow
```
IfStmt/WhileStmt/ForStmt AST Node
    ↓
execute_statement()
    ↓
Evaluate condition
    ↓
Execute body (if condition true)
    ↓
Loop back (for loops)
```

## Memory Model

### Variable Storage
- Variables are stored in `Environment` objects
- Each scope has its own environment
- Environments form a chain (parent-child relationship)
- Global variables are in `global_env`

### Register Storage
- CPU registers (r0-r31) are stored in `interpreter.registers` array
- Register variables are accessed via `register_map`
- Register access bypasses normal variable lookup

### Hardware State
- GPIO state: pin configurations and values
- UART state: baud rate, status flags
- Timer state: mode, period, running status, value

## Error Handling

### Preprocessing Errors
- `PreprocessingError` - File not found, circular includes, invalid directives

### Lexing Errors
- `TokenType.ERROR` - Invalid characters, unterminated comments

### Parsing Errors
- `SyntaxError` - Invalid syntax, unexpected tokens, missing tokens

### Runtime Errors
- `RuntimeError` - Undefined variables, undefined functions, division by zero

## Extension Points

### Adding New Operators
1. Add token type to `TokenType` enum in `lexer.py`
2. Add token recognition in `Lexer.tokenize()`
3. Add parsing method in `Parser` (if needed for precedence)
4. Add evaluation in `Interpreter.evaluate_binary_op()` or `evaluate_unary_op()`

### Adding New Hardware Functions
1. Add function implementation method in `Interpreter` class
2. Register function in `_register_hardware_functions()`
3. Update documentation

### Adding New Statement Types
1. Add AST node class in `parser.py`
2. Add parsing method in `Parser`
3. Add execution method in `Interpreter`
4. Update `execute_statement()` to handle new node type

## Testing Strategy

### Unit Tests
- Each component has dedicated test file
- Tests cover normal cases, edge cases, and error cases
- Tests use Python's `unittest` framework

### Integration Tests
- Example programs serve as integration tests
- Test real-world usage scenarios
- Verify end-to-end functionality

### Test Coverage
- **Lexer**: Token recognition, error handling, line/column tracking
- **Parser**: All statement types, expression parsing, error cases
- **Interpreter**: Arithmetic, control flow, functions, edge cases
- **Preprocessor**: Includes, nested includes, circular detection

## Performance Considerations

### Current Implementation
- Interpreter-based (not compiled)
- No optimization passes
- Direct AST execution

### Future Improvements
- Code generation to ISA instructions
- Register allocation
- Instruction scheduling
- Optimization passes

## Code Organization

### File Structure
- One component per file
- Clear separation of concerns
- Minimal dependencies between components

### Naming Conventions
- Classes: PascalCase (`Token`, `Lexer`, `Parser`)
- Methods: snake_case (`tokenize()`, `parse_expression()`)
- Constants: UPPER_SNAKE_CASE (token types in enum)

### Documentation
- Docstrings for all classes and public methods
- Inline comments for complex logic
- External documentation in markdown files
