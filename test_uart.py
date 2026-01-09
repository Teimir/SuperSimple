#!/usr/bin/env python3
"""Test script for UART implementation"""
from interpreter import Interpreter
from parser import Parser
from lexer import Lexer

# Simple test: output "Hello"
code = """
function main() {
    uart_write(72);   // H
    uart_write(101);   // e
    uart_write(108);   // l
    uart_write(108);   // l
    uart_write(111);   // o
    return 0;
}
"""

try:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    interpreter = Interpreter(program)
    print("Output: ", end="", flush=True)
    result = interpreter.interpret()
    print()  # New line after output
    print(f"Program returned: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
