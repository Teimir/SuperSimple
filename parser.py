"""
Parser for Simple C-Style Language
Builds an Abstract Syntax Tree (AST) from tokens.
"""

from typing import List, Optional, Union
from lexer import Token, TokenType


class ASTNode:
    """Base class for all AST nodes."""
    pass


# Expression nodes
class Expression(ASTNode):
    pass


class Literal(Expression):
    def __init__(self, value: int):
        self.value = value
    
    def __repr__(self):
        return f"Literal({self.value})"


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"


class BinaryOp(Expression):
    def __init__(self, op: str, left: Expression, right: Expression):
        self.op = op
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"


class UnaryOp(Expression):
    def __init__(self, op: str, operand: Expression):
        self.op = op
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


class FunctionCall(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"


# Statement nodes
class Statement(ASTNode):
    pass


class VarDecl(Statement):
    def __init__(self, name: str, initializer: Optional[Expression] = None):
        self.name = name
        self.initializer = initializer
    
    def __repr__(self):
        if self.initializer:
            return f"VarDecl({self.name}, {self.initializer})"
        return f"VarDecl({self.name})"


class Assignment(Statement):
    def __init__(self, name: str, value: Expression):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


class Return(Statement):
    def __init__(self, value: Optional[Expression] = None):
        self.value = value
    
    def __repr__(self):
        return f"Return({self.value})"


class IfStmt(Statement):
    def __init__(self, condition: Expression, then_stmt: Statement, else_stmt: Optional[Statement] = None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
    
    def __repr__(self):
        return f"IfStmt({self.condition}, {self.then_stmt}, {self.else_stmt})"


class WhileStmt(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStmt({self.condition}, {self.body})"


class ForStmt(Statement):
    def __init__(self, init: Optional[Statement], condition: Optional[Expression], 
                 increment: Optional[Assignment], body: Statement):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body
    
    def __repr__(self):
        return f"ForStmt({self.init}, {self.condition}, {self.increment}, {self.body})"


class Block(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements
    
    def __repr__(self):
        return f"Block({self.statements})"


class FunctionCallStmt(Statement):
    """Statement wrapper for function calls."""
    def __init__(self, call: FunctionCall):
        self.call = call
    
    def __repr__(self):
        return f"FunctionCallStmt({self.call})"


class FunctionDef(ASTNode):
    def __init__(self, name: str, params: List[str], body: Block):
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"FunctionDef({self.name}, {self.params}, {self.body})"


class Program(ASTNode):
    def __init__(self, functions: List[FunctionDef]):
        self.functions = functions
    
    def __repr__(self):
        return f"Program({self.functions})"


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Optional[Token]:
        """Get the current token, or None if at EOF."""
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 1) -> Optional[Token]:
        """Peek ahead by offset tokens."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.tokens):
            return None
        return self.tokens[peek_pos]
    
    def advance(self) -> Token:
        """Move to the next token and return it."""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.tokens[-1]  # Return EOF token
    
    def expect(self, token_type: TokenType, error_msg: str = None) -> Token:
        """Expect a specific token type, raise error if not found."""
        token = self.current_token()
        if not token or token.type != token_type:
            msg = error_msg or f"Expected {token_type.name}, got {token.type.name if token else 'EOF'}"
            raise SyntaxError(f"{msg} at line {token.line if token else '?'}, column {token.column if token else '?'}")
        return self.advance()
    
    def parse(self) -> Program:
        """Parse the entire program."""
        functions = []
        while self.current_token() and self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.FUNCTION:
                functions.append(self.parse_function())
            else:
                raise SyntaxError(f"Unexpected token: {self.current_token()} at line {self.current_token().line}")
        
        if not any(f.name == 'main' for f in functions):
            raise SyntaxError("Program must have a 'main' function")
        
        return Program(functions)
    
    def parse_function(self) -> FunctionDef:
        """Parse a function definition."""
        self.expect(TokenType.FUNCTION)
        name_token = self.expect(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value
        
        self.expect(TokenType.LPAREN)
        params = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.current_token() and self.current_token().type == TokenType.COMMA:
                self.advance()
                params.append(self.expect(TokenType.IDENTIFIER, "Expected parameter name").value)
        self.expect(TokenType.RPAREN)
        
        body = self.parse_block()
        
        return FunctionDef(name, params, body)
    
    def parse_block(self) -> Block:
        """Parse a block of statements."""
        self.expect(TokenType.LBRACE)
        statements = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            statements.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_statement(self) -> Statement:
        """Parse a statement."""
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of file")
        
        # Variable declaration
        if token.type == TokenType.UINT32:
            return self.parse_var_decl()
        
        # Return statement
        if token.type == TokenType.RETURN:
            return self.parse_return()
        
        # If statement
        if token.type == TokenType.IF:
            return self.parse_if()
        
        # While statement
        if token.type == TokenType.WHILE:
            return self.parse_while()
        
        # For statement
        if token.type == TokenType.FOR:
            return self.parse_for()
        
        # Block
        if token.type == TokenType.LBRACE:
            return self.parse_block()
        
        # Assignment or function call (both start with identifier)
        if token.type == TokenType.IDENTIFIER:
            next_token = self.peek_token()
            if next_token and next_token.type == TokenType.LPAREN:
                # Function call statement
                call = self.parse_expression()  # Will parse as function call
                self.expect(TokenType.SEMICOLON)
                # Create a statement wrapper for function calls
                # We'll use a special Statement type for this
                return FunctionCallStmt(call)
            elif next_token and next_token.type == TokenType.ASSIGN:
                # Assignment
                return self.parse_assignment()
        
        raise SyntaxError(f"Unexpected token in statement: {token} at line {token.line}")
    
    def parse_var_decl(self) -> VarDecl:
        """Parse a variable declaration."""
        self.expect(TokenType.UINT32)
        name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        
        initializer = None
        if self.current_token() and self.current_token().type == TokenType.ASSIGN:
            self.advance()
            initializer = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        return VarDecl(name, initializer)
    
    def parse_assignment(self) -> Assignment:
        """Parse an assignment statement."""
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return Assignment(name, value)
    
    def parse_return(self) -> Return:
        """Parse a return statement."""
        self.expect(TokenType.RETURN)
        value = None
        if self.current_token() and self.current_token().type != TokenType.SEMICOLON:
            value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return Return(value)
    
    def parse_if(self) -> IfStmt:
        """Parse an if statement."""
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        then_stmt = self.parse_statement()
        
        else_stmt = None
        if self.current_token() and self.current_token().type == TokenType.ELSE:
            self.advance()
            else_stmt = self.parse_statement()
        
        return IfStmt(condition, then_stmt, else_stmt)
    
    def parse_while(self) -> WhileStmt:
        """Parse a while statement."""
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        return WhileStmt(condition, body)
    
    def parse_for(self) -> ForStmt:
        """Parse a for statement."""
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)
        
        # Initialization (optional)
        init = None
        if self.current_token() and self.current_token().type == TokenType.UINT32:
            # Variable declaration in for loop
            self.expect(TokenType.UINT32)
            name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name")
            name = name_token.value
            
            initializer = None
            if self.current_token() and self.current_token().type == TokenType.ASSIGN:
                self.advance()
                initializer = self.parse_expression()
            
            init = VarDecl(name, initializer)
        elif self.current_token() and self.current_token().type == TokenType.IDENTIFIER:
            # Could be assignment
            if self.peek_token() and self.peek_token().type == TokenType.ASSIGN:
                name_token = self.current_token()
                self.advance()
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                init = Assignment(name_token.value, value)
        
        self.expect(TokenType.SEMICOLON)
        
        # Condition (optional)
        condition = None
        if self.current_token() and self.current_token().type != TokenType.SEMICOLON:
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        # Increment (optional)
        increment = None
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            if self.current_token().type == TokenType.IDENTIFIER:
                name = self.current_token().value
                self.advance()
                if self.current_token() and self.current_token().type == TokenType.ASSIGN:
                    self.advance()
                    value = self.parse_expression()
                    increment = Assignment(name, value)
        
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        
        return ForStmt(init, condition, increment, body)
    
    def parse_expression(self) -> Expression:
        """Parse an expression (lowest precedence)."""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression."""
        left = self.parse_logical_and()
        while self.current_token() and self.current_token().type == TokenType.OR:
            op = self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression."""
        left = self.parse_equality()
        while self.current_token() and self.current_token().type == TokenType.AND:
            op = self.advance()
            right = self.parse_equality()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_equality(self) -> Expression:
        """Parse equality expressions."""
        left = self.parse_relational()
        while self.current_token() and self.current_token().type in [TokenType.EQUAL, TokenType.NOT_EQUAL]:
            op = self.advance()
            right = self.parse_relational()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_relational(self) -> Expression:
        """Parse relational expressions."""
        left = self.parse_additive()
        while self.current_token() and self.current_token().type in [
            TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL
        ]:
            op = self.advance()
            right = self.parse_additive()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_additive(self) -> Expression:
        """Parse additive expressions."""
        left = self.parse_multiplicative()
        while self.current_token() and self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative expressions."""
        left = self.parse_unary()
        while self.current_token() and self.current_token().type in [
            TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO
        ]:
            op = self.advance()
            right = self.parse_unary()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary expressions."""
        if self.current_token() and self.current_token().type in [TokenType.NOT, TokenType.MINUS]:
            op = self.advance()
            operand = self.parse_unary()
            return UnaryOp(op.value, operand)
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parse primary expressions."""
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of file in expression")
        
        # Literal
        if token.type == TokenType.LITERAL:
            self.advance()
            return Literal(int(token.value))
        
        # Identifier or function call
        if token.type == TokenType.IDENTIFIER:
            name = token.value
            self.advance()
            if self.current_token() and self.current_token().type == TokenType.LPAREN:
                # Function call
                self.advance()
                args = []
                if self.current_token() and self.current_token().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    while self.current_token() and self.current_token().type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, args)
            else:
                # Identifier
                return Identifier(name)
        
        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        raise SyntaxError(f"Unexpected token in expression: {token} at line {token.line}")
