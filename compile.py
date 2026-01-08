"""
Compiler entry point for Simple C-Style Language.
Compiles .sc source files to FASM assembly (.asm) files.
"""

import sys
import os
from lexer import Lexer, TokenType
from parser import Parser
from preprocessor import Preprocessor, PreprocessingError
from codegen import CodeGenerator


def compile_file(source_file: str, output_file: str = None):
    """Compile a source file to assembly."""
    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found.")
        sys.exit(1)
    
    # Determine output file name
    if output_file is None:
        base_name = os.path.splitext(source_file)[0]
        output_file = f"{base_name}.asm"
    
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
        
        # Generate assembly code
        try:
            generator = CodeGenerator(ast)
            assembly_code = generator.generate()
        except Exception as e:
            print(f"Code generation error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Write assembly file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(assembly_code)
            print(f"Compilation successful. Output: {output_file}")
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)
    
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python compile.py <source_file> [output_file]")
        print("")
        print("Compiles a .sc source file to FASM assembly (.asm file).")
        print("If output_file is not specified, output will be <source_file>.asm")
        sys.exit(1)
    
    source_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    compile_file(source_file, output_file)


if __name__ == '__main__':
    main()
