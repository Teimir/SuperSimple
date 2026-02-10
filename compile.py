"""
Compiler entry point for Simple C-Style Language.
Compiles .sc source files to FASM assembly (.asm), then to binary (.bin) using FASM.
Optionally runs the binary via interpreter_x64.exe.
"""

import sys
import os
import subprocess

from version import __version__
from pipeline import build_ast
from codegen import CodeGenerator
from preprocessor import PreprocessingError


def compile_file(source_file: str, output_file: str = None) -> str:
    """Compile a source file to assembly and optionally to binary. Returns path to .asm file."""
    if output_file is None:
        output_file = f"{os.path.splitext(source_file)[0]}.asm"

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
            sys.exit(1)
        raise
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        sys.exit(1)

    try:
        generator = CodeGenerator(ast)
        assembly_code = generator.generate(output_file)
    except Exception as e:
        print(f"Code generation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(assembly_code)
        print(f"Assembly generated: {output_file}")
    except OSError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    try:
        compile_with_fasm(output_file)
    except Exception as e:
        print(f"FASM compilation error: {e}")
        sys.exit(1)

    return output_file


def compile_with_fasm(asm_file: str):
    """Compile .asm file to .bin using FASM from int_pack."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fasm_exe = os.path.join(script_dir, "int_pack", "FASM.EXE")

    if not os.path.exists(fasm_exe):
        print(f"Warning: FASM.EXE not found at {fasm_exe}")
        print("Skipping binary compilation. You can compile manually with:")
        print(f'  "{fasm_exe}" "{asm_file}"')
        return

    asm_abs = os.path.abspath(asm_file)
    asm_dir = os.path.dirname(asm_abs)
    old_cwd = os.getcwd()

    try:
        os.chdir(asm_dir)
        try:
            result = subprocess.run(
                [fasm_exe, os.path.basename(asm_abs)],
                capture_output=True,
                text=True,
                cwd=asm_dir,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            print("FASM compilation timed out after 30 seconds")
            raise RuntimeError("FASM compilation timed out")

        if result.returncode == 0:
            bin_file = asm_file.replace(".asm", ".bin")
            mif_file = asm_file.replace(".asm", ".mif")
            print("FASM compilation successful.")
            if os.path.exists(bin_file):
                print(f"  Binary: {bin_file}")
            if os.path.exists(mif_file):
                print(f"  MIF: {mif_file}")
        else:
            print("FASM compilation failed:")
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError("FASM compilation failed")
    finally:
        os.chdir(old_cwd)


def run_interpreter(bin_file: str):
    """Run the compiled .bin file using interpreter_x64.exe."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    interpreter_exe = os.path.join(script_dir, "int_pack", "interpreter_x64.exe")

    if not os.path.exists(interpreter_exe):
        print(f"Error: interpreter_x64.exe not found at {interpreter_exe}")
        sys.exit(1)

    if not os.path.exists(bin_file):
        print(f"Error: Binary file '{bin_file}' not found.")
        print("Compile the .asm file first with FASM.")
        sys.exit(1)

    bin_abs = os.path.abspath(bin_file)
    print(f"Running interpreter: {bin_abs}")
    print("=" * 50)

    try:
        result = subprocess.run(
            [interpreter_exe, bin_abs],
            cwd=os.path.dirname(bin_abs),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        print("=" * 50)
        print("ERROR: Program execution timed out after 10 seconds")
        print("This usually indicates an infinite loop or very slow execution.")
        print("=" * 50)
        sys.exit(124)

    if result.stdout:
        lines = result.stdout.split("\n")
        if len(lines) > 150:
            print(f"... ({len(lines) - 150} lines omitted) ...")
            print("\n".join(lines[-150:]))
        else:
            print(result.stdout)

    if result.stderr:
        print("Errors:", file=sys.stderr)
        stderr_lines = result.stderr.split("\n")
        if len(stderr_lines) > 150:
            print(f"... ({len(stderr_lines) - 150} lines omitted) ...", file=sys.stderr)
            print("\n".join(stderr_lines[-150:]), file=sys.stderr)
        else:
            print(result.stderr, file=sys.stderr)

    sys.exit(result.returncode)


def _print_usage():
    print("Usage: python compile.py <source_file> [output_file] [--run]")
    print("")
    print("Compiles a .sc source file to FASM assembly (.asm), then to binary (.bin).")
    print("If output_file is not specified, output will be <source_file>.asm")
    print("")
    print("Options:")
    print("  -h, --help    Show this help")
    print("  -V, --version Show version")
    print("  --run         After compilation, run the binary using interpreter_x64.exe")
    print(f"Version: {__version__}")
    print("")
    print("Examples:")
    print("  python compile.py test_examples/basic/sum_range.sc")
    print("  python compile.py test_examples/basic/sum_range.sc --run")
    print("  python compile.py --run test_examples/basic/sum_range.sc")


def main():
    """Main entry point."""
    args = sys.argv[1:]
    if not args:
        _print_usage()
        sys.exit(1)

    source_file = None
    output_file = None
    run_after = False

    for arg in args:
        if arg in ("-h", "--help", "-help"):
            _print_usage()
            sys.exit(0)
        if arg in ("-V", "--version"):
            print(__version__)
            sys.exit(0)
        if arg == "--run":
            run_after = True
        elif not arg.startswith("-"):
            if source_file is None:
                source_file = arg
            elif output_file is None:
                output_file = arg
            else:
                print(f"Error: unexpected argument '{arg}'")
                _print_usage()
                sys.exit(1)

    if source_file is None:
        print("Error: no source file specified.")
        _print_usage()
        sys.exit(1)

    out_asm = compile_file(source_file, output_file)

    if run_after:
        bin_file = out_asm.replace(".asm", ".bin")
        run_interpreter(bin_file)


if __name__ == "__main__":
    main()
