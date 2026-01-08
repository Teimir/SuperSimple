"""
Compiler entry point for Simple C-Style Language.
Compiles .sc source files to FASM assembly (.asm) files, then to binary (.bin) using FASM.
Also provides option to run the binary using interpreter_x64.exe.
"""

import sys
import os
import subprocess
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
            # Pass output file path to generator for proper include path calculation
            assembly_code = generator.generate(output_file)
        except Exception as e:
            print(f"Code generation error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Write assembly file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(assembly_code)
            print(f"Assembly generated: {output_file}")
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)
        
        # Compile assembly to binary using FASM from int_pack
        try:
            compile_with_fasm(output_file)
        except Exception as e:
            print(f"FASM compilation error: {e}")
            sys.exit(1)
    
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def compile_with_fasm(asm_file: str):
    """Compile .asm file to .bin using FASM from int_pack."""
    # Get absolute path to FASM.EXE
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fasm_exe = os.path.join(script_dir, "int_pack", "FASM.EXE")
    
    if not os.path.exists(fasm_exe):
        print(f"Warning: FASM.EXE not found at {fasm_exe}")
        print("Skipping binary compilation. You can compile manually with:")
        print(f'  "{fasm_exe}" "{asm_file}"')
        return
    
    # Get absolute path to .asm file
    asm_abs = os.path.abspath(asm_file)
    asm_dir = os.path.dirname(asm_abs)
    
    # Change to directory containing .asm file for FASM to work correctly
    # (FASM needs to resolve includes relative to current directory)
    old_cwd = os.getcwd()
    try:
        os.chdir(asm_dir)
        
        # Run FASM
        result = subprocess.run(
            [fasm_exe, os.path.basename(asm_abs)],
            capture_output=True,
            text=True,
            cwd=asm_dir
        )
        
        if result.returncode == 0:
            bin_file = asm_file.replace('.asm', '.bin')
            mif_file = asm_file.replace('.asm', '.mif')
            print(f"FASM compilation successful.")
            if os.path.exists(bin_file):
                print(f"  Binary: {bin_file}")
            if os.path.exists(mif_file):
                print(f"  MIF: {mif_file}")
        else:
            print(f"FASM compilation failed:")
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError("FASM compilation failed")
    finally:
        os.chdir(old_cwd)


def run_interpreter(bin_file: str):
    """Run the compiled .bin file using interpreter_x64.exe."""
    # Get absolute path to interpreter
    script_dir = os.path.dirname(os.path.abspath(__file__))
    interpreter_exe = os.path.join(script_dir, "int_pack", "interpreter_x64.exe")
    
    if not os.path.exists(interpreter_exe):
        print(f"Error: interpreter_x64.exe not found at {interpreter_exe}")
        sys.exit(1)
    
    if not os.path.exists(bin_file):
        print(f"Error: Binary file '{bin_file}' not found.")
        print("Compile the .asm file first with FASM.")
        sys.exit(1)
    
    # Get absolute path to .bin file
    bin_abs = os.path.abspath(bin_file)
    
    print(f"Running interpreter: {bin_abs}")
    print("=" * 50)
    
    # Run interpreter and capture output
    result = subprocess.run(
        [interpreter_exe, bin_abs],
        cwd=os.path.dirname(bin_abs),
        capture_output=True,
        text=True
    )
    
    # Print output (always limit to last 150 lines for readability)
    if result.stdout:
        lines = result.stdout.split('\n')
        # Always print last 150 lines (or all if less than 150)
        if len(lines) > 150:
            print(f"... ({len(lines) - 150} lines omitted) ...")
            print('\n'.join(lines[-150:]))
        else:
            print(result.stdout)
    elif result.stdout == "":
        # If no output, still print message
        pass
    
    if result.stderr:
        print("Errors:", file=sys.stderr)
        stderr_lines = result.stderr.split('\n')
        if len(stderr_lines) > 150:
            print(f"... ({len(stderr_lines) - 150} lines omitted) ...", file=sys.stderr)
            print('\n'.join(stderr_lines[-150:]), file=sys.stderr)
        else:
            print(result.stderr, file=sys.stderr)
    
    sys.exit(result.returncode)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python compile.py <source_file> [output_file] [--run]")
        print("")
        print("Compiles a .sc source file to FASM assembly (.asm), then to binary (.bin).")
        print("If output_file is not specified, output will be <source_file>.asm")
        print("")
        print("Options:")
        print("  --run    After compilation, run the binary using interpreter_x64.exe")
        print("")
        print("Examples:")
        print("  python compile.py examples/basic/sum_range.sc")
        print("  python compile.py examples/basic/sum_range.sc --run")
        sys.exit(1)
    
    source_file = sys.argv[1]
    output_file = None
    run_after = False
    
    # Parse arguments
    for arg in sys.argv[2:]:
        if arg == '--run':
            run_after = True
        elif not arg.startswith('-'):
            output_file = arg
    
    if output_file is None:
        base_name = os.path.splitext(source_file)[0]
        output_file = f"{base_name}.asm"
    
    compile_file(source_file, output_file)
    
    # Run interpreter if requested
    if run_after:
        bin_file = output_file.replace('.asm', '.bin')
        run_interpreter(bin_file)


if __name__ == '__main__':
    main()
