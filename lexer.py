"""
Lexer (Tokenizer) for Simple C-Style Language

This module converts source code into a stream of tokens. The lexer recognizes:
- Keywords (function, uint32, if, else, while, for, return, etc.)
- Operators (arithmetic, logical, relational, bitwise)
- Identifiers (variable and function names)
- Literals (integer constants)
- Punctuation (semicolons, commas, parentheses, braces)
- Comments (single-line and multi-line)

The lexer tracks line and column numbers for error reporting.
"""

import re
from enum import Enum
from typing import List, Optional, Tuple


class TokenType(Enum):
    # Keywords
    UINT32 = "UINT32"
    FUNCTION = "FUNCTION"
    FOR = "FOR"
    WHILE = "WHILE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"
    REGISTER = "REGISTER"
    VOLATILE = "VOLATILE"
    INTERRUPT = "INTERRUPT"
    
    # Identifiers and literals
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    ASSIGN = "ASSIGN"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    BITWISE_AND = "BITWISE_AND"
    BITWISE_OR = "BITWISE_OR"
    BITWISE_XOR = "BITWISE_XOR"
    SHIFT_LEFT = "SHIFT_LEFT"
    SHIFT_RIGHT = "SHIFT_RIGHT"
    INCREMENT = "INCREMENT"
    DECREMENT = "DECREMENT"
    
    # Punctuation
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    
    # Special
    EOF = "EOF"
    ERROR = "ERROR"


class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get the current character, or None if at EOF."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek ahead by offset characters."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> Optional[str]:
        """Move to the next character and return it."""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char() and self.current_char() in ' \t\r\n':
            # For newlines, we still need to update line/column, so use advance
            if self.current_char() == '\n':
                self.advance()
            elif self.current_char() in ' \t\r':
                self.advance()
    
    def skip_comment(self):
        """Skip single-line and multi-line comments."""
        if self.current_char() == '/' and self.peek_char() == '/':
            # Single-line comment
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Multi-line comment
            self.advance()  # skip '/'
            self.advance()  # skip '*'
            while True:
                if not self.current_char():
                    raise SyntaxError(f"Unterminated comment at line {self.line}, column {self.column}")
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # skip '*'
                    self.advance()  # skip '/'
                    break
                self.advance()
    
    def read_identifier_or_keyword(self) -> str:
        """Read an identifier or keyword."""
        start = self.pos
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        return self.source[start:self.pos]
    
    def read_number(self) -> str:
        """Read a numeric literal (decimal or hexadecimal)."""
        start = self.pos
        
        # Check for hex prefix: 0x or 0X
        if self.current_char() == '0':
            peek = self.peek_char()
            if peek in ['x', 'X']:
                # It's a hex literal: consume '0' and 'x'/'X'
                self.advance()  # consume '0'
                self.advance()  # consume 'x' or 'X'
                # Read hex digits
                while self.current_char() and self.current_char() in '0123456789ABCDEFabcdef':
                    self.advance()
                return self.source[start:self.pos]
        
        # Decimal number (includes standalone '0')
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        return self.source[start:self.pos]
    
    def tokenize(self) -> List[Token]:
        """Tokenize the source code."""
        while True:
            self.skip_whitespace()
            
            if not self.current_char():
                self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
                break
            
            # Skip comments
            if self.current_char() == '/' and self.peek_char() in ['/', '*']:
                try:
                    self.skip_comment()
                    continue
                except SyntaxError as e:
                    self.tokens.append(Token(TokenType.ERROR, str(e), self.line, self.column))
                    break
            
            line = self.line
            column = self.column
            char = self.current_char()
            
            # Keywords and identifiers
            if char.isalpha() or char == '_':
                identifier = self.read_identifier_or_keyword()
                keyword_map = {
                    'uint32': TokenType.UINT32,
                    'function': TokenType.FUNCTION,
                    'for': TokenType.FOR,
                    'while': TokenType.WHILE,
                    'if': TokenType.IF,
                    'else': TokenType.ELSE,
                    'return': TokenType.RETURN,
                    'register': TokenType.REGISTER,
                    'volatile': TokenType.VOLATILE,
                    'interrupt': TokenType.INTERRUPT,
                }
                token_type = keyword_map.get(identifier, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, identifier, line, column))
                continue
            
            # Numbers
            if char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.LITERAL, number, line, column))
                continue
            
            # Two-character operators
            if char == '=' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQUAL, "==", line, column))
                continue
            
            if char == '!' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", line, column))
                continue
            
            # Check for shift operators BEFORE <= and >= to ensure correct precedence
            if char == '<' and self.peek_char() == '<':
                self.advance()
                self.advance()
                # #region agent log
                with open('e:\\aiproj\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                    f.write('{"id":"log_lexer_shift_left_token","timestamp":' + str(int(__import__('time').time() * 1000)) + ',"location":"lexer.py:229","message":"Tokenizing shift left operator","data":{"operator":"<<"},"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A"}\n')
                # #endregion agent log
                self.tokens.append(Token(TokenType.SHIFT_LEFT, "<<", line, column))
                continue
            
            if char == '>' and self.peek_char() == '>':
                self.advance()
                self.advance()
                # #region agent log
                with open('e:\\aiproj\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                    f.write('{"id":"log_lexer_shift_right_token","timestamp":' + str(int(__import__('time').time() * 1000)) + ',"location":"lexer.py:237","message":"Tokenizing shift right operator","data":{"operator":">>"},"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A"}\n')
                # #endregion agent log
                self.tokens.append(Token(TokenType.SHIFT_RIGHT, ">>", line, column))
                continue
            
            if char == '<' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", line, column))
                continue
            
            if char == '>' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", line, column))
                continue
            
            if char == '&' and self.peek_char() == '&':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.AND, "&&", line, column))
                continue
            
            # Check for single & (bitwise AND) - must check after &&
            if char == '&':
                self.advance()
                self.tokens.append(Token(TokenType.BITWISE_AND, "&", line, column))
                continue
            
            if char == '|' and self.peek_char() == '|':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.OR, "||", line, column))
                continue
            
            # Check for single | (bitwise OR) - must check after ||
            if char == '|':
                self.advance()
                self.tokens.append(Token(TokenType.BITWISE_OR, "|", line, column))
                continue
            
            if char == '+' and self.peek_char() == '+':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.INCREMENT, "++", line, column))
                continue
            
            if char == '-' and self.peek_char() == '-':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.DECREMENT, "--", line, column))
                continue
            
            # Single-character operators and punctuation
            token_map = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS,
                '>': TokenType.GREATER,
                '!': TokenType.NOT,
                '^': TokenType.BITWISE_XOR,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
            }
            
            if char in token_map:
                self.advance()
                self.tokens.append(Token(token_map[char], char, line, column))
                continue
            
            # Unknown character
            self.tokens.append(Token(TokenType.ERROR, f"Unexpected character: {char}", line, column))
            self.advance()
        
        return self.tokens
