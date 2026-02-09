"""
Unit tests for the interpreter.
"""

import unittest
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, RuntimeError


class TestInterpreter(unittest.TestCase):
    
    def interpret_source(self, source):
        """Helper to interpret source code."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter(ast)
        return interpreter.interpret()
    
    def test_simple_return(self):
        """Test simple return statement."""
        source = "function main() { return 42; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 42)
    
    def test_return_zero(self):
        """Test that missing return returns 0."""
        source = "function main() { uint32 x = 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)
    
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        source = "function main() { return 10 + 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 15)
        
        source = "function main() { return 10 - 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 5)
        
        source = "function main() { return 10 * 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 50)
        
        source = "function main() { return 10 / 2; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 5)
        
        source = "function main() { return 10 % 3; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)
    
    def test_variable_declaration_and_assignment(self):
        """Test variable declaration and assignment."""
        source = "function main() { uint32 x = 10; x = 20; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 20)
    
    def test_variable_declaration_without_initializer(self):
        """Test variable declaration without initializer defaults to 0."""
        source = "function main() { uint32 x; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)
    
    def test_variable_arithmetic(self):
        """Test arithmetic with variables."""
        source = "function main() { uint32 a = 5; uint32 b = 3; return a + b; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 8)
        
        source = "function main() { uint32 a = 5; uint32 b = 3; return a * b; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 15)
    
    def test_if_statement(self):
        """Test if statement."""
        source = "function main() { if (1) { return 10; } return 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 10)
        
        source = "function main() { if (0) { return 10; } return 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 5)
    
    def test_if_else_statement(self):
        """Test if-else statement."""
        source = "function main() { if (1) { return 10; } else { return 20; } }"
        result = self.interpret_source(source)
        self.assertEqual(result, 10)
        
        source = "function main() { if (0) { return 10; } else { return 20; } }"
        result = self.interpret_source(source)
        self.assertEqual(result, 20)
    
    def test_while_loop(self):
        """Test while loop."""
        source = """
        function main() {
            uint32 x = 0;
            uint32 i = 0;
            while (i < 5) {
                x = x + i;
                i = i + 1;
            }
            return x;
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 10)  # 0+1+2+3+4 = 10
    
    def test_for_loop(self):
        """Test for loop."""
        source = """
        function main() {
            uint32 sum = 0;
            uint32 i;
            for (i = 0; i < 5; i = i + 1) {
                sum = sum + i;
            }
            return sum;
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 10)  # 0+1+2+3+4 = 10
    
    def test_for_loop_with_increment_operator(self):
        """Test for loop with increment operator."""
        source = """
        function main() {
            uint32 sum = 0;
            uint32 i;
            for (i = 0; i < 5; i++) {
                sum = sum + i;
            }
            return sum;
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 10)

    def test_do_while_loop(self):
        """Test do-while loop: body runs at least once, then condition."""
        source = """
        function main() {
            uint32 x = 0;
            do {
                x = x + 1;
            } while (x < 5);
            return x;
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 5)

    def test_do_while_break_continue(self):
        """Test break and continue inside do-while."""
        source = """
        function main() {
            uint32 x = 0;
            do {
                x = x + 1;
                if (x == 2) { continue; }
                if (x >= 4) { break; }
            } while (1);
            return x;
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 4)
    
    def test_increment_operator(self):
        """Test increment operator."""
        source = "function main() { uint32 x = 5; x++; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 6)
        
        source = "function main() { uint32 x = 5; ++x; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 6)
    
    def test_decrement_operator(self):
        """Test decrement operator."""
        source = "function main() { uint32 x = 5; x--; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 4)
        
        source = "function main() { uint32 x = 5; --x; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 4)
    
    def test_function_call(self):
        """Test function call."""
        source = """
        function add(a, b) {
            return a + b;
        }
        function main() {
            return add(5, 3);
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 8)
    
    def test_recursion(self):
        """Test recursive function calls."""
        source = """
        function factorial(n) {
            if (n == 0 || n == 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }
        function main() {
            return factorial(5);
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 120)
    
    def test_nested_function_calls(self):
        """Test nested function calls."""
        source = """
        function add(a, b) {
            return a + b;
        }
        function multiply(a, b) {
            return a * b;
        }
        function main() {
            return multiply(add(2, 3), add(1, 1));
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 10)  # (2+3) * (1+1) = 5 * 2 = 10
    
    def test_relational_operators(self):
        """Test relational operators."""
        source = "function main() { return 5 < 10; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 10 < 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)  # false
        
        source = "function main() { return 5 <= 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 10 > 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 5 >= 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 5 == 5; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 5 == 3; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)  # false
        
        source = "function main() { return 5 != 3; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
    
    def test_logical_operators(self):
        """Test logical operators."""
        source = "function main() { return 1 && 1; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 1 && 0; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)  # false
        
        source = "function main() { return 1 || 0; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return 0 || 0; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)  # false
        
        source = "function main() { return !0; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # true
        
        source = "function main() { return !1; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)  # false
    
    def test_operator_precedence(self):
        """Test operator precedence."""
        source = "function main() { return 2 + 3 * 4; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 14)  # 2 + (3*4) = 14
        
        source = "function main() { return (2 + 3) * 4; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 20)  # (2+3) * 4 = 20
        
        source = "function main() { return 1 + 2 < 3 + 4; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 1)  # (1+2) < (3+4) = 3 < 7 = true
    
    def test_variable_scoping(self):
        """Test variable scoping."""
        source = """
        function main() {
            uint32 x = 10;
            {
                uint32 x = 20;
            }
            return x;
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 10)  # Inner x should not affect outer x
    
    def test_function_parameter_scoping(self):
        """Test that function parameters have their own scope."""
        source = """
        function test(x) {
            return x;
        }
        function main() {
            uint32 x = 100;
            return test(50);
        }
        """
        result = self.interpret_source(source)
        self.assertEqual(result, 50)  # Function parameter x should not affect main's x
    
    def test_integer_overflow(self):
        """Test integer overflow (wrap-around)."""
        source = "function main() { uint32 x = 4294967295; x = x + 1; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)  # Should wrap around
        
        source = "function main() { uint32 x = 0; x = x - 1; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 4294967295)  # Should wrap around
    
    def test_division_by_zero(self):
        """Test that division by zero raises RuntimeError."""
        source = "function main() { uint32 x = 10 / 0; return x; }"
        
        with self.assertRaises(RuntimeError) as context:
            self.interpret_source(source)
        
        self.assertIn("Division by zero", str(context.exception))
    
    def test_modulo_by_zero(self):
        """Test that modulo by zero raises RuntimeError."""
        source = "function main() { uint32 x = 10 % 0; return x; }"
        
        with self.assertRaises(RuntimeError) as context:
            self.interpret_source(source)
        
        self.assertIn("Modulo by zero", str(context.exception))
    
    def test_undefined_variable(self):
        """Test that undefined variable raises RuntimeError."""
        source = "function main() { return x; }"
        
        with self.assertRaises(RuntimeError) as context:
            self.interpret_source(source)
        
        self.assertIn("Undefined variable", str(context.exception))
    
    def test_undefined_function(self):
        """Test that undefined function raises RuntimeError."""
        source = "function main() { return unknown_function(); }"
        
        with self.assertRaises(RuntimeError) as context:
            self.interpret_source(source)
        
        self.assertIn("Undefined function", str(context.exception))
    
    def test_wrong_number_of_arguments(self):
        """Test that wrong number of function arguments raises RuntimeError."""
        source = """
        function add(a, b) {
            return a + b;
        }
        function main() {
            return add(1);
        }
        """
        
        with self.assertRaises(RuntimeError) as context:
            self.interpret_source(source)
        
        self.assertIn("expects", str(context.exception).lower())
    
    def test_unary_minus(self):
        """Test unary minus operator."""
        source = "function main() { return -5; }"
        result = self.interpret_source(source)
        # -5 in unsigned 32-bit wraps to 4294967291
        self.assertEqual(result, 4294967291)
    
    def test_complex_nested_structure(self):
        """Test complex nested structures."""
        source = """
        function main() {
            uint32 sum = 0;
            uint32 i;
            for (i = 0; i < 3; i++) {
                uint32 j;
                for (j = 0; j < 2; j++) {
                    if (i == j) {
                        sum = sum + 1;
                    } else {
                        sum = sum + 2;
                    }
                }
            }
            return sum;
        }
        """
        result = self.interpret_source(source)
        # i=0: j=0 (i==j, +1), j=1 (i!=j, +2) -> +3
        # i=1: j=0 (i!=j, +2), j=1 (i==j, +1) -> +3
        # i=2: j=0 (i!=j, +2), j=1 (i!=j, +2) -> +4
        # Total: 3 + 3 + 4 = 10
        self.assertEqual(result, 10)
    
    def test_hex_literal_basic(self):
        """Test basic hex literal execution."""
        source = "function main() { return 0xFF; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 255)  # 0xFF = 255
        
        source = "function main() { return 0x10; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 16)  # 0x10 = 16
    
    def test_hex_literal_variable(self):
        """Test hex literal in variable declaration and assignment."""
        source = "function main() { uint32 x = 0xFF; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 255)
        
        source = "function main() { uint32 x; x = 0xABCD; return x; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 43981)  # 0xABCD = 43981
    
    def test_hex_literal_expressions(self):
        """Test hex literals in expressions."""
        source = "function main() { return 0xFF + 0x01; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 256)  # 255 + 1 = 256
        
        source = "function main() { return 0x10 * 0x02; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 32)  # 16 * 2 = 32
        
        source = "function main() { return 0xFF & 0x0F; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 15)  # 255 & 15 = 15
        
        source = "function main() { return 0xAA | 0x55; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 255)  # 170 | 85 = 255
    
    def test_hex_literal_uppercase_prefix(self):
        """Test hex literal with uppercase prefix (0X)."""
        source = "function main() { return 0XFF; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 255)
    
    def test_hex_literal_mixed_case(self):
        """Test hex literal with mixed case digits."""
        source = "function main() { return 0xAbCd; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 43981)  # 0xAbCd = 43981
        
        source = "function main() { return 0XaBcD; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 43981)
    
    def test_hex_literal_boundary_values(self):
        """Test hex literal boundary values."""
        source = "function main() { return 0x0; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0)
        
        source = "function main() { return 0xFFFFFFFF; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 0xFFFFFFFF)  # Maximum uint32 value
    
    def test_hex_literal_in_loop(self):
        """Test hex literals in loop conditions."""
        source = """
        function main() {
            uint32 sum = 0;
            uint32 i;
            for (i = 0x00; i < 0x05; i++) {
                sum = sum + i;
            }
            return sum;
        }
        """
        result = self.interpret_source(source)
        # Sum of 0 + 1 + 2 + 3 + 4 = 10
        self.assertEqual(result, 10)
    
    def test_hex_literal_with_decimal(self):
        """Test mixing hex and decimal literals."""
        source = "function main() { return 0xFF + 1; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 256)  # 255 + 1 = 256
        
        source = "function main() { return 16 + 0x10; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 32)  # 16 + 16 = 32

    def test_asm_block_no_op(self):
        """Test that asm { ... } in interpreter is no-op and program runs normally."""
        source = "function main() { asm { mov r:0, r:1 }; return 42; }"
        result = self.interpret_source(source)
        self.assertEqual(result, 42)


if __name__ == '__main__':
    unittest.main()
