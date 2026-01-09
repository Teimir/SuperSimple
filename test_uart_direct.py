#!/usr/bin/env python3
"""Direct test of UART write"""
import sys

# Test direct output
print("Direct test:", end="", flush=True)
sys.stdout.write(chr(72))
sys.stdout.write(chr(101))
sys.stdout.write(chr(108))
sys.stdout.write(chr(108))
sys.stdout.write(chr(111))
sys.stdout.flush()
print(" - done")

# Test with interpreter
from interpreter import Interpreter
from parser import Parser
from lexer import Lexer

code = "function main() { uart_write(72); uart_write(101); uart_write(108); uart_write(108); uart_write(111); return 0; }"

print("Interpreter test:", end="", flush=True)
try:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    interpreter = Interpreter(program)
    result = interpreter.interpret()
    print(f" - returned {result}")
except Exception as e:
    print(f" - ERROR: {e}")
    import traceback
    traceback.print_exc()
