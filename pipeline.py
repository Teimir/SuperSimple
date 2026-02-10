"""
Shared front-end pipeline: preprocess → lex → parse.
Used by main.py (interpreter) and compile.py (compiler).
"""

import os

from lexer import Lexer, TokenType
from parser import Parser
from preprocessor import Preprocessor, PreprocessingError


def build_ast(source_file: str):
    """
    Run preprocess, lex, parse on a source file. Returns the AST.

    Raises:
        FileNotFoundError: if source_file does not exist.
        PreprocessingError: on preprocessor errors.
        RuntimeError: on lexer errors (message starts with "Lexer error: ").
        SyntaxError: on parser errors.
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"File '{source_file}' not found.")

    preprocessor = Preprocessor()
    source_code = preprocessor.preprocess(source_file)

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    for token in tokens:
        if token.type == TokenType.ERROR:
            raise RuntimeError(f"Lexer error: {token.value}")

    parser = Parser(tokens)
    return parser.parse()
