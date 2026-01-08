# Contributing Guide

## Development Setup

1. Clone the repository
2. Ensure Python 3.7+ is installed
3. No external dependencies required

## Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test suite
python -m unittest test_lexer
python -m unittest test_parser
python -m unittest test_interpreter
python -m unittest test_preprocessor
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all classes and public methods
- Keep functions focused and small
- Add comments for complex logic

## Adding New Features

### Adding a New Operator

1. **Lexer** (`lexer.py`):
   - Add token type to `TokenType` enum
   - Add recognition in `tokenize()` method
   - Ensure proper precedence (multi-character operators first)

2. **Parser** (`parser.py`):
   - Add parsing method if needed for precedence
   - Integrate into expression parsing hierarchy
   - Update operator precedence table

3. **Interpreter** (`interpreter.py`):
   - Add evaluation in `evaluate_binary_op()` or `evaluate_unary_op()`
   - Handle edge cases (overflow, division by zero, etc.)

4. **Tests**:
   - Add test cases in appropriate test file
   - Test normal cases, edge cases, and error cases

5. **Documentation**:
   - Update `LANGUAGE_SPEC.md`
   - Update `README.md` if it's a major feature

### Adding a New Hardware Function

1. **Interpreter** (`interpreter.py`):
   - Implement function as `_function_name()` method
   - Register in `_register_hardware_functions()`
   - Add to appropriate hardware state management

2. **Documentation**:
   - Update `LANGUAGE_SPEC.md` hardware section
   - Add example in `examples/hardware/`

### Adding a New Statement Type

1. **Parser** (`parser.py`):
   - Add AST node class
   - Add parsing method
   - Integrate into `parse_statement()`

2. **Interpreter** (`interpreter.py`):
   - Add execution method
   - Integrate into `execute_statement()`

3. **Tests**:
   - Add comprehensive test cases

4. **Documentation**:
   - Update `LANGUAGE_SPEC.md`
   - Add examples

## Testing Guidelines

- Write tests for all new features
- Test both success and error cases
- Test edge cases (overflow, division by zero, etc.)
- Ensure all existing tests still pass

## Documentation Guidelines

- Update relevant documentation files
- Add examples for new features
- Keep examples simple and clear
- Document limitations and edge cases

## Commit Messages

Use clear, descriptive commit messages:
- `Add support for bitwise shift operators`
- `Fix infinite loop in timer example`
- `Update documentation for hardware features`

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Ensure all tests pass
4. Update documentation
5. Submit pull request with description

## Questions?

If you have questions about the codebase:
- Check `ARCHITECTURE.md` for system design
- Check `LANGUAGE_SPEC.md` for language details
- Review existing code for patterns
- Check test files for usage examples
