# Project Structure

This document provides an overview of the project file organization.

## Root Directory

```
aiproj/
├── Core Implementation Files (root)
│   ├── main.py              # Main entry point
│   ├── lexer.py             # Tokenizer (source → tokens)
│   ├── parser.py            # Parser (tokens → AST)
│   ├── interpreter.py       # Interpreter (AST → execution)
│   ├── preprocessor.py      # Preprocessor (#include handling)
│   ├── codegen.py           # Code generator (AST → assembly)
│   └── compile.py           # Compilation script
│
├── Documentation
│   ├── README.md            # Main project documentation (root)
│   └── doc/                 # Documentation directory
│       ├── LANGUAGE_SPEC.md     # Complete language specification
│       ├── ARCHITECTURE.md       # System architecture overview
│       ├── INCLUDE_MECHANISM.md  # #include directive details
│       ├── CONTRIBUTING.md      # Development guidelines
│       ├── CODE_GENERATION.md   # Code generation details
│       └── PROJECT_STRUCTURE.md  # This file
│
├── Examples
│   ├── examples/
│   │   ├── basic/           # Basic programming examples
│   │   │   └── hello_world/ # Hello World example
│   │   ├── hardware/        # Hardware/MCU examples
│   │   ├── operators/       # Operator testing examples
│   │   ├── includes/        # Include directive examples
│   │   ├── advanced/        # Advanced programming examples
│   │   └── README.md        # Examples documentation
│   └── user_examples/       # User example programs
│       ├── simple_return/   # Simple return example
│       ├── complex_example/ # Complex example with functions
│       └── test_example/    # Test example
│
├── Tests
│   └── self_tests/          # Unit tests directory
│       ├── test_lexer.py        # Lexer unit tests
│       ├── test_parser.py       # Parser unit tests
│       ├── test_interpreter.py  # Interpreter unit tests
│       ├── test_preprocessor.py # Preprocessor unit tests
│       └── run_tests.py        # Test runner script
│
├── ISA Documentation
│   └── isa/                 # Instruction Set Architecture docs
│       ├── README.md
│       └── ISA.xlsx
│
└── int_pack/                # FASM tools and includes
    ├── FASM.EXE             # FASM assembler
    ├── interpreter_x64.exe  # Binary interpreter
    ├── ISA.inc              # ISA definitions
    ├── macros.inc           # FASM macros
    └── ...
```

## File Descriptions

### Core Implementation

- **`main.py`**: Orchestrates the compilation pipeline (preprocess → lex → parse → interpret)
- **`lexer.py`**: Converts source code into tokens
- **`parser.py`**: Builds Abstract Syntax Tree from tokens
- **`interpreter.py`**: Executes the AST and manages runtime state
- **`preprocessor.py`**: Handles `#include` directives before lexing

### Documentation

- **`README.md`**: Main documentation with quick start guide
- **`LANGUAGE_SPEC.md`**: Complete language grammar and syntax
- **`ARCHITECTURE.md`**: System design and component details
- **`INCLUDE_MECHANISM.md`**: Detailed `#include` explanation
- **`CONTRIBUTING.md`**: Development and contribution guidelines
- **`PROJECT_STRUCTURE.md`**: Project organization (this file)

### Examples

- **`examples/basic/`**: Simple programming examples
  - **`hello_world/`**: Hello World example with UART output
- **`examples/hardware/`**: MCU hardware interaction examples
- **`examples/operators/`**: Operator testing and demonstration
- **`examples/includes/`**: File inclusion examples
- **`examples/advanced/`**: Complex programming patterns
- **`user_examples/`**: User-contributed example programs
  - **`simple_return/`**: Simple return example
  - **`complex_example/`**: Complex example with functions
  - **`test_example/`**: Test example

### Tests

- **`self_tests/test_*.py`**: Unit tests for each component
- **`self_tests/run_tests.py`**: Test runner that executes all tests

## Code Organization Principles

1. **Separation of Concerns**: Each component in its own file
2. **Clear Dependencies**: Minimal coupling between components
3. **Comprehensive Testing**: Unit tests for all components
4. **Documentation**: Inline comments and external documentation
5. **Examples**: Real-world usage examples organized by category

## Dependencies

- **Python 3.7+**: Required runtime
- **No external libraries**: Uses only Python standard library
- **unittest**: Built-in testing framework

## Build/Execution Flow

```
Source File (.sc)
    ↓
main.py
    ↓
preprocessor.py (#include expansion)
    ↓
lexer.py (tokenization)
    ↓
parser.py (AST construction)
    ↓
interpreter.py (execution)
    ↓
Program Result
```

## Testing Strategy

- **Unit Tests**: Each component tested independently
- **Integration Tests**: Example programs serve as integration tests
- **Error Cases**: Tests cover error conditions and edge cases
- **Coverage**: All major features have test coverage

## Maintenance

- Keep documentation up to date with code changes
- Add examples for new features
- Update tests when adding functionality
- Maintain consistent code style
- Review and refactor as needed
