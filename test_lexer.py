"""
Unit tests for the lexer (tokenizer).
"""

import unittest
from lexer import Lexer, TokenType, Token


class TestLexer(unittest.TestCase):
    
    def test_keywords(self):
        """Test keyword tokenization."""
        source = "uint32 function for while if else return"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.UINT32, TokenType.FUNCTION, TokenType.FOR,
            TokenType.WHILE, TokenType.IF, TokenType.ELSE, TokenType.RETURN,
            TokenType.EOF
        ]
        self.assertEqual(len(tokens), len(expected_types))
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)
    
    def test_identifiers(self):
        """Test identifier tokenization."""
        source = "x myVar _count counter123"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(len(identifiers), 4)
        self.assertEqual(identifiers[0].value, "x")
        self.assertEqual(identifiers[1].value, "myVar")
        self.assertEqual(identifiers[2].value, "_count")
        self.assertEqual(identifiers[3].value, "counter123")
    
    def test_literals(self):
        """Test numeric literal tokenization."""
        source = "0 42 1000 4294967295"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        literals = [t for t in tokens if t.type == TokenType.LITERAL]
        self.assertEqual(len(literals), 4)
        self.assertEqual(literals[0].value, "0")
        self.assertEqual(literals[1].value, "42")
        self.assertEqual(literals[2].value, "1000")
        self.assertEqual(literals[3].value, "4294967295")
    
    def test_arithmetic_operators(self):
        """Test arithmetic operator tokenization."""
        source = "+ - * / %"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
            TokenType.DIVIDE, TokenType.MODULO, TokenType.EOF
        ]
        actual_types = [t.type for t in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_relational_operators(self):
        """Test relational operator tokenization."""
        source = "< <= > >= == !="
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER,
            TokenType.GREATER_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.EOF
        ]
        actual_types = [t.type for t in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_logical_operators(self):
        """Test logical operator tokenization."""
        source = "&& || !"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.AND, TokenType.OR, TokenType.NOT, TokenType.EOF
        ]
        actual_types = [t.type for t in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_increment_decrement(self):
        """Test increment and decrement operators."""
        source = "++ --"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.INCREMENT, TokenType.DECREMENT, TokenType.EOF
        ]
        actual_types = [t.type for t in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_assignment_operator(self):
        """Test assignment operator."""
        source = "= =="
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.ASSIGN, TokenType.EQUAL, TokenType.EOF
        ]
        actual_types = [t.type for t in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_punctuation(self):
        """Test punctuation tokens."""
        source = "; , ( ) { }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.SEMICOLON, TokenType.COMMA, TokenType.LPAREN,
            TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE, TokenType.EOF
        ]
        actual_types = [t.type for t in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_single_line_comment(self):
        """Test single-line comment handling."""
        source = "x = 5; // this is a comment\ny = 10;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should have: x = 5 ; y = 10 ;
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(len(identifiers), 2)
        self.assertEqual(identifiers[0].value, "x")
        self.assertEqual(identifiers[1].value, "y")
        
        # Comment should be skipped
        comment_tokens = [t for t in tokens if "comment" in t.value.lower()]
        self.assertEqual(len(comment_tokens), 0)
    
    def test_multi_line_comment(self):
        """Test multi-line comment handling."""
        source = "x = 5; /* this is a\nmulti-line\ncomment */ y = 10;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(len(identifiers), 2)
        self.assertEqual(identifiers[0].value, "x")
        self.assertEqual(identifiers[1].value, "y")
    
    def test_unterminated_comment(self):
        """Test that unterminated multi-line comment produces error token."""
        source = "x = 5; /* this comment never ends"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should produce an ERROR token for unterminated comment
        error_tokens = [t for t in tokens if t.type == TokenType.ERROR]
        self.assertGreater(len(error_tokens), 0)
        self.assertIn("Unterminated comment", error_tokens[0].value)
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly skipped."""
        source = "   x   =   5   ;   "
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should have: x = 5 ;
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        expected_types = [
            TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.LITERAL,
            TokenType.SEMICOLON
        ]
        actual_types = [t.type for t in non_eof]
        self.assertEqual(actual_types, expected_types)
    
    def test_line_column_tracking(self):
        """Test that line and column numbers are tracked correctly."""
        source = "x = 5;\ny = 10;\nz = x + y;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Find 'x' token
        x_token = next(t for t in tokens if t.value == "x")
        self.assertEqual(x_token.line, 1)
        self.assertEqual(x_token.column, 1)
        
        # Find 'y' token
        y_token = next(t for t in tokens if t.value == "y")
        self.assertEqual(y_token.line, 2)
        self.assertEqual(y_token.column, 1)
        
        # Find 'z' token
        z_token = next(t for t in tokens if t.value == "z")
        self.assertEqual(z_token.line, 3)
        self.assertEqual(z_token.column, 1)
    
    def test_operator_precedence_in_tokenization(self):
        """Test that multi-character operators are tokenized correctly."""
        source = "x++ y-- a == b c != d"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        token_values = [t.value for t in tokens if t.type != TokenType.EOF]
        # Should have: x ++ y -- a == b c != d
        # (spaces between tokens, but ++, --, ==, != should be single tokens)
        self.assertIn("++", token_values)
        self.assertIn("--", token_values)
        self.assertIn("==", token_values)
        self.assertIn("!=", token_values)
    
    def test_complex_expression_tokens(self):
        """Test tokenization of a complex expression."""
        source = "x = (a + b) * c - d / e;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        expected_sequence = [
            TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.LPAREN,
            TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER,
            TokenType.RPAREN, TokenType.MULTIPLY, TokenType.IDENTIFIER,
            TokenType.MINUS, TokenType.IDENTIFIER, TokenType.DIVIDE,
            TokenType.IDENTIFIER, TokenType.SEMICOLON
        ]
        actual_sequence = [t.type for t in non_eof]
        self.assertEqual(actual_sequence, expected_sequence)
    
    def test_keyword_vs_identifier(self):
        """Test that keywords are not recognized as identifiers."""
        source = "uint32 myUint32 function myFunction"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should have: UINT32 keyword, myUint32 identifier, FUNCTION keyword, myFunction identifier
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        expected_types = [
            TokenType.UINT32, TokenType.IDENTIFIER, TokenType.FUNCTION, TokenType.IDENTIFIER
        ]
        actual_types = [t.type for t in non_eof]
        self.assertEqual(actual_types, expected_types)
        self.assertEqual(non_eof[1].value, "myUint32")
        self.assertEqual(non_eof[3].value, "myFunction")


if __name__ == '__main__':
    unittest.main()
