"""
Main entry point for the Simple C-Style Language interpreter.
"""

__version__ = "1.0.0"

import sys
import os
from lexer import Lexer, TokenType
from parser import Parser
from interpreter import Interpreter, RuntimeError
from preprocessor import Preprocessor, PreprocessingError


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    if source_file in ('-h', '--help', '-help'):
        print("Usage: python main.py <source_file>")
        print("")
        print("Runs the Simple C-Style Language interpreter on the given .sc source file.")
        print(f"Version: {__version__}")
        sys.exit(0)
    if source_file in ('-V', '--version'):
        print(__version__)
        sys.exit(0)
    
    try:
        # Preprocess (handle #include directives)
        preprocessor = Preprocessor()
        try:
            source_code = preprocessor.preprocess(source_file)
        except PreprocessingError as e:
            print(f"Preprocessing error: {e}")
            sys.exit(1)
        
        # Tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Check for lexer errors
        for token in tokens:
            if token.type == TokenType.ERROR:
                print(f"Lexer error: {token.value}")
                sys.exit(1)
        
        # Parse
        parser = Parser(tokens)
        try:
            ast = parser.parse()
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            sys.exit(1)
        
        # Interpret
        interpreter = Interpreter(ast)
        try:
            result = interpreter.interpret()
            print(f"Program executed successfully. Return value: {result}")
            sys.exit(0)
        except RuntimeError as e:
            print(f"Runtime error: {e}")
            sys.exit(1)
    
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
