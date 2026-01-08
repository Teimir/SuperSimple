"""
Unit tests for the parser.
"""

import unittest
from lexer import Lexer, TokenType
from parser import Parser, Program, FunctionDef, VarDecl, Assignment, Return
from parser import IfStmt, WhileStmt, ForStmt, Block, BinaryOp, Literal
from parser import Identifier, UnaryOp, FunctionCall, Increment, Decrement


class TestParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def parse_source(self, source):
        """Helper to parse source code."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_function_without_parameters(self):
        """Test parsing a function without parameters."""
        source = "function main() { return 0; }"
        program = self.parse_source(source)
        
        self.assertEqual(len(program.functions), 1)
        self.assertEqual(program.functions[0].name, "main")
        self.assertEqual(len(program.functions[0].params), 0)
    
    def test_function_with_parameters(self):
        """Test parsing a function with parameters."""
        source = "function add(a, b) { return a + b; } function main() { return 0; }"
        program = self.parse_source(source)
        
        self.assertEqual(len(program.functions), 2)
        add_func = program.functions[0]
        self.assertEqual(add_func.name, "add")
        self.assertEqual(add_func.params, ["a", "b"])
    
    def test_function_with_multiple_parameters(self):
        """Test parsing a function with multiple parameters."""
        source = "function test(a, b, c, d) { return 0; } function main() { return 0; }"
        program = self.parse_source(source)
        
        test_func = program.functions[0]
        self.assertEqual(test_func.params, ["a", "b", "c", "d"])
    
    def test_variable_declaration_without_initializer(self):
        """Test parsing variable declaration without initializer."""
        source = "function main() { uint32 x; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        self.assertIsInstance(main_body[0], VarDecl)
        self.assertEqual(main_body[0].name, "x")
        self.assertIsNone(main_body[0].initializer)
    
    def test_variable_declaration_with_initializer(self):
        """Test parsing variable declaration with initializer."""
        source = "function main() { uint32 x = 42; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        var_decl = main_body[0]
        self.assertIsInstance(var_decl, VarDecl)
        self.assertEqual(var_decl.name, "x")
        self.assertIsInstance(var_decl.initializer, Literal)
        self.assertEqual(var_decl.initializer.value, 42)
    
    def test_assignment_statement(self):
        """Test parsing assignment statement."""
        source = "function main() { uint32 x; x = 10; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        assignment = main_body[1]
        self.assertIsInstance(assignment, Assignment)
        self.assertEqual(assignment.name, "x")
        self.assertIsInstance(assignment.value, Literal)
        self.assertEqual(assignment.value.value, 10)
    
    def test_return_statement_with_value(self):
        """Test parsing return statement with value."""
        source = "function main() { return 42; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        return_stmt = main_body[0]
        self.assertIsInstance(return_stmt, Return)
        self.assertIsNotNone(return_stmt.value)
        self.assertEqual(return_stmt.value.value, 42)
    
    def test_return_statement_without_value(self):
        """Test parsing return statement without value."""
        source = "function main() { return; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        return_stmt = main_body[0]
        self.assertIsInstance(return_stmt, Return)
        self.assertIsNone(return_stmt.value)
    
    def test_if_statement(self):
        """Test parsing if statement."""
        source = "function main() { if (x == 0) { return 1; } return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        if_stmt = main_body[0]
        self.assertIsInstance(if_stmt, IfStmt)
        self.assertIsInstance(if_stmt.condition, BinaryOp)
        self.assertIsInstance(if_stmt.then_stmt, Block)
        self.assertIsNone(if_stmt.else_stmt)
    
    def test_if_else_statement(self):
        """Test parsing if-else statement."""
        source = "function main() { if (x == 0) { return 1; } else { return 0; } }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        if_stmt = main_body[0]
        self.assertIsInstance(if_stmt, IfStmt)
        self.assertIsNotNone(if_stmt.else_stmt)
        self.assertIsInstance(if_stmt.else_stmt, Block)
    
    def test_while_statement(self):
        """Test parsing while statement."""
        source = "function main() { while (x > 0) { x = x - 1; } return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        while_stmt = main_body[0]
        self.assertIsInstance(while_stmt, WhileStmt)
        self.assertIsInstance(while_stmt.condition, BinaryOp)
        self.assertIsInstance(while_stmt.body, Block)
    
    def test_for_statement(self):
        """Test parsing for statement."""
        source = "function main() { uint32 i; for (i = 0; i < 10; i = i + 1) { } return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        for_stmt = main_body[1]
        self.assertIsInstance(for_stmt, ForStmt)
        self.assertIsNotNone(for_stmt.init)
        self.assertIsNotNone(for_stmt.condition)
        self.assertIsNotNone(for_stmt.increment)
    
    def test_for_statement_with_increment_operator(self):
        """Test parsing for statement with increment operator."""
        source = "function main() { uint32 i; for (i = 0; i < 10; i++) { } return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        for_stmt = main_body[1]
        self.assertIsInstance(for_stmt, ForStmt)
        self.assertIsInstance(for_stmt.increment, Increment)
        self.assertEqual(for_stmt.increment.name, "i")
        self.assertFalse(for_stmt.increment.is_prefix)
    
    def test_increment_postfix(self):
        """Test parsing postfix increment statement."""
        source = "function main() { uint32 x = 5; x++; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        increment = main_body[1]
        self.assertIsInstance(increment, Increment)
        self.assertEqual(increment.name, "x")
        self.assertFalse(increment.is_prefix)
    
    def test_increment_prefix(self):
        """Test parsing prefix increment statement."""
        source = "function main() { uint32 x = 5; ++x; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        increment = main_body[1]
        self.assertIsInstance(increment, Increment)
        self.assertEqual(increment.name, "x")
        self.assertTrue(increment.is_prefix)
    
    def test_decrement_postfix(self):
        """Test parsing postfix decrement statement."""
        source = "function main() { uint32 x = 5; x--; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        decrement = main_body[1]
        self.assertIsInstance(decrement, Decrement)
        self.assertEqual(decrement.name, "x")
        self.assertFalse(decrement.is_prefix)
    
    def test_decrement_prefix(self):
        """Test parsing prefix decrement statement."""
        source = "function main() { uint32 x = 5; --x; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        decrement = main_body[1]
        self.assertIsInstance(decrement, Decrement)
        self.assertEqual(decrement.name, "x")
        self.assertTrue(decrement.is_prefix)
    
    def test_arithmetic_expression(self):
        """Test parsing arithmetic expression."""
        source = "function main() { uint32 x = 1 + 2 * 3; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        var_decl = main_body[0]
        expr = var_decl.initializer
        # Should parse as 1 + (2 * 3) due to precedence
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "+")
    
    def test_unary_operators(self):
        """Test parsing unary operators."""
        source = "function main() { uint32 x = -5; uint32 y = !x; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        # First variable declaration should have unary minus
        var_decl1 = main_body[0]
        self.assertIsInstance(var_decl1.initializer, UnaryOp)
        self.assertEqual(var_decl1.initializer.op, "-")
        
        # Second variable declaration should have logical not
        var_decl2 = main_body[1]
        self.assertIsInstance(var_decl2.initializer, UnaryOp)
        self.assertEqual(var_decl2.initializer.op, "!")
    
    def test_function_call(self):
        """Test parsing function call."""
        source = "function add(a, b) { return a + b; } function main() { uint32 x = add(1, 2); return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[1].body.statements
        var_decl = main_body[0]
        func_call = var_decl.initializer
        self.assertIsInstance(func_call, FunctionCall)
        self.assertEqual(func_call.name, "add")
        self.assertEqual(len(func_call.args), 2)
    
    def test_nested_blocks(self):
        """Test parsing nested blocks."""
        source = "function main() { if (x == 0) { if (y == 0) { return 1; } } return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        outer_if = main_body[0]
        self.assertIsInstance(outer_if, IfStmt)
        inner_block = outer_if.then_stmt
        inner_statement = inner_block.statements[0]
        self.assertIsInstance(inner_statement, IfStmt)
    
    def test_complex_expression_precedence(self):
        """Test that operator precedence is correctly parsed."""
        source = "function main() { uint32 x = 1 + 2 * 3 - 4 / 2; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        var_decl = main_body[0]
        expr = var_decl.initializer
        # Expression should be parsed according to precedence
        self.assertIsInstance(expr, BinaryOp)
    
    def test_logical_operators(self):
        """Test parsing logical operators."""
        source = "function main() { uint32 x = a && b || c; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        var_decl = main_body[0]
        expr = var_decl.initializer
        self.assertIsInstance(expr, BinaryOp)
        # || should have lower precedence, so it should be the top-level op
        self.assertEqual(expr.op, "||")
    
    def test_relational_operators(self):
        """Test parsing relational operators."""
        source = "function main() { uint32 x = a < b && c >= d; return 0; }"
        program = self.parse_source(source)
        
        main_body = program.functions[0].body.statements
        var_decl = main_body[0]
        expr = var_decl.initializer
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "&&")
    
    def test_missing_main_function(self):
        """Test that missing main function raises error."""
        source = "function test() { return 0; }"
        
        with self.assertRaises(SyntaxError) as context:
            self.parse_source(source)
        
        self.assertIn("main", str(context.exception))
    
    def test_missing_semicolon(self):
        """Test that missing semicolon raises syntax error."""
        source = "function main() { uint32 x = 5 return 0; }"
        
        with self.assertRaises(SyntaxError):
            self.parse_source(source)
    
    def test_missing_closing_brace(self):
        """Test that missing closing brace raises syntax error."""
        source = "function main() { return 0; "
        
        with self.assertRaises(SyntaxError):
            self.parse_source(source)
    
    def test_empty_program(self):
        """Test that empty program raises error."""
        source = ""
        
        with self.assertRaises(SyntaxError):
            self.parse_source(source)


if __name__ == '__main__':
    unittest.main()
