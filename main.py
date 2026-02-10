"""
Main entry point for the Simple C-Style Language interpreter.
"""

import sys

from version import __version__
from pipeline import build_ast
from interpreter import Interpreter, RuntimeError
from preprocessor import PreprocessingError


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    if source_file in ("-h", "--help", "-help"):
        print("Usage: python main.py <source_file>")
        print("")
        print("Runs the Simple C-Style Language interpreter on the given .sc source file.")
        print(f"Version: {__version__}")
        sys.exit(0)
    if source_file in ("-V", "--version"):
        print(__version__)
        sys.exit(0)

    try:
        ast = build_ast(source_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PreprocessingError as e:
        print(f"Preprocessing error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        if str(e).startswith("Lexer error:"):
            print(e)
        else:
            raise
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        sys.exit(1)

    interpreter = Interpreter(ast)
    try:
        result = interpreter.interpret()
        print(f"Program executed successfully. Return value: {result}")
        sys.exit(0)
    except RuntimeError as e:
        print(f"Runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
