"""
Main entry point for the Simple C-Style Language interpreter.
"""

import sys
from lexer import Lexer, TokenType
from parser import Parser
from interpreter import Interpreter, RuntimeError


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    
    try:
        # Read source file
        with open(source_file, 'r') as f:
            source_code = f.read()
        
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
