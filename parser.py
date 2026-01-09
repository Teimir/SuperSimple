"""
Parser for Simple C-Style Language

This module builds an Abstract Syntax Tree (AST) from a stream of tokens.
The parser uses recursive descent parsing to construct the AST.

AST Node Types:
- Program: Root node containing all functions
- FunctionDef: Function definitions
- Statement nodes: VarDecl, Assignment, IfStmt, WhileStmt, ForStmt, ReturnStmt, Block
- Expression nodes: Literal, Identifier, BinaryOp, UnaryOp, FunctionCall

The parser handles operator precedence and associativity correctly.
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
    def __init__(self, name: str, initializer: Optional[Expression] = None, 
                 var_type: str = 'uint32', is_register: bool = False, 
                 is_volatile: bool = False, register_num: Optional[int] = None):
        self.name = name
        self.initializer = initializer
        self.var_type = var_type  # 'uint32' or 'int32'
        self.is_register = is_register
        self.is_volatile = is_volatile
        self.register_num = register_num  # For register variables: 0-31
    
    def __repr__(self):
        attrs = []
        if self.var_type != 'uint32':
            attrs.append(f"type={self.var_type}")
        if self.is_register:
            attrs.append(f"register={self.register_num}")
        if self.is_volatile:
            attrs.append("volatile")
        attr_str = ", " + ", ".join(attrs) if attrs else ""
        if self.initializer:
            return f"VarDecl({self.name}, {self.initializer}{attr_str})"
        return f"VarDecl({self.name}{attr_str})"


class Assignment(Statement):
    def __init__(self, name: str, value: Expression):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


class ArrayAssignment(Statement):
    """Array element assignment: arr[i] = value"""
    def __init__(self, name: str, index: Expression, value: Expression):
        self.name = name
        self.index = index
        self.value = value
    
    def __repr__(self):
        return f"ArrayAssignment({self.name}, {self.index}, {self.value})"


class PointerAssignment(Statement):
    """Pointer dereference assignment: *ptr = value"""
    def __init__(self, operand: Expression, value: Expression):
        self.operand = operand  # Expression that evaluates to an address
        self.value = value
    
    def __repr__(self):
        return f"PointerAssignment({self.operand}, {self.value})"


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
                 increment: Optional[Statement], body: Statement):
        self.init = init
        self.condition = condition
        self.increment = increment  # Can be Assignment, Increment, or Decrement
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


class Increment(Statement):
    """Increment statement (++x or x++)."""
    def __init__(self, name: str, is_prefix: bool):
        self.name = name
        self.is_prefix = is_prefix
    
    def __repr__(self):
        prefix_str = "prefix" if self.is_prefix else "postfix"
        return f"Increment({self.name}, {prefix_str})"


class Decrement(Statement):
    """Decrement statement (--x or x--)."""
    def __init__(self, name: str, is_prefix: bool):
        self.name = name
        self.is_prefix = is_prefix
    
    def __repr__(self):
        prefix_str = "prefix" if self.is_prefix else "postfix"
        return f"Decrement({self.name}, {prefix_str})"


class ArrayDecl(Statement):
    """Array declaration: uint32 arr[10]; or uint32 arr[5] = {1, 2, 3, 4, 5};"""
    def __init__(self, name: str, size: Expression, initializer: Optional[List[Expression]] = None,
                 is_register: bool = False, is_volatile: bool = False):
        self.name = name
        self.size = size  # Должно быть Literal (константа)
        self.initializer = initializer  # Список выражений для инициализации
        self.is_register = is_register
        self.is_volatile = is_volatile
    
    def __repr__(self):
        attrs = []
        if self.is_register:
            attrs.append("register")
        if self.is_volatile:
            attrs.append("volatile")
        attr_str = ", " + ", ".join(attrs) if attrs else ""
        if self.initializer:
            return f"ArrayDecl({self.name}, {self.size}, {self.initializer}{attr_str})"
        return f"ArrayDecl({self.name}, {self.size}{attr_str})"


class ArrayAccess(Expression):
    """Array element access: arr[index]"""
    def __init__(self, name: str, index: Expression):
        self.name = name
        self.index = index
    
    def __repr__(self):
        return f"ArrayAccess({self.name}, {self.index})"


class PointerDecl(Statement):
    """Pointer declaration: uint32* ptr;"""
    def __init__(self, name: str, initializer: Optional[Expression] = None,
                 is_register: bool = False, is_volatile: bool = False):
        self.name = name
        self.initializer = initializer  # Может быть AddressOf или другой указатель
        self.is_register = is_register
        self.is_volatile = is_volatile
    
    def __repr__(self):
        attrs = []
        if self.is_register:
            attrs.append("register")
        if self.is_volatile:
            attrs.append("volatile")
        attr_str = ", " + ", ".join(attrs) if attrs else ""
        if self.initializer:
            return f"PointerDecl({self.name}, {self.initializer}{attr_str})"
        return f"PointerDecl({self.name}{attr_str})"


class AddressOf(Expression):
    """Address-of operator: &x"""
    def __init__(self, operand: Expression):
        self.operand = operand  # Identifier, ArrayAccess, или Dereference
    
    def __repr__(self):
        return f"AddressOf({self.operand})"


class Dereference(Expression):
    """Pointer dereference: *ptr"""
    def __init__(self, operand: Expression):
        self.operand = operand  # Identifier (указатель) или AddressOf
    
    def __repr__(self):
        return f"Dereference({self.operand})"


class FunctionDef(ASTNode):
    def __init__(self, name: str, params: List[str], body: Block, is_interrupt: bool = False):
        self.name = name
        self.params = params
        self.body = body
        self.is_interrupt = is_interrupt
    
    def __repr__(self):
        interrupt_str = ", interrupt" if self.is_interrupt else ""
        return f"FunctionDef({self.name}, {self.params}, {self.body}{interrupt_str})"


class Program(ASTNode):
    def __init__(self, functions: List[FunctionDef], global_vars: List[VarDecl] = None):
        self.functions = functions
        self.global_vars = global_vars or []
    
    def __repr__(self):
        return f"Program({self.functions}, globals={self.global_vars})"


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
        global_vars = []
        
        while self.current_token() and self.current_token().type != TokenType.EOF:
            # Check for interrupt keyword before function
            if (self.current_token().type == TokenType.FUNCTION or 
                (self.current_token().type == TokenType.INTERRUPT and 
                 self.peek_token() and self.peek_token().type == TokenType.FUNCTION)):
                functions.append(self.parse_function())
            # Check for global variable declarations (uint32, int32, register, volatile)
            elif (self.current_token().type == TokenType.UINT32 or
                  self.current_token().type == TokenType.INT32 or
                  self.current_token().type == TokenType.REGISTER or
                  self.current_token().type == TokenType.VOLATILE):
                global_vars.append(self.parse_var_decl())
            else:
                raise SyntaxError(f"Unexpected token: {self.current_token()} at line {self.current_token().line}")
        
        if not any(f.name == 'main' for f in functions):
            raise SyntaxError("Program must have a 'main' function")
        
        # Store global variables in program (for interpreter to use)
        program = Program(functions)
        program.global_vars = global_vars
        return program
    
    def parse_function(self) -> FunctionDef:
        """Parse a function definition."""
        is_interrupt = False
        
        # Check for interrupt keyword before function
        if self.current_token() and self.current_token().type == TokenType.INTERRUPT:
            self.advance()
            is_interrupt = True
        
        self.expect(TokenType.FUNCTION)
        
        # If interrupt, function should be void with no parameters
        if is_interrupt:
            # Interrupt functions must be void (implicit) and have no parameters
            name_token = self.expect(TokenType.IDENTIFIER, "Expected function name")
            name = name_token.value
        else:
            name_token = self.expect(TokenType.IDENTIFIER, "Expected function name")
            name = name_token.value
        
        self.expect(TokenType.LPAREN)
        params = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            # Parse first parameter (could be uint32* ptr or just identifier)
            # For now, just parse identifier - parameters are implicitly uint32 or uint32*
            # The type info is not stored in FunctionDef (parameters are just names)
            # Check if it's a pointer type: uint32* param
            if self.current_token().type == TokenType.UINT32:
                self.advance()
                is_ptr_param = False
                if self.current_token() and self.current_token().type == TokenType.MULTIPLY:
                    self.advance()  # consume *
                    is_ptr_param = True
                param_name = self.expect(TokenType.IDENTIFIER, "Expected parameter name").value
                params.append(param_name)
            else:
                # Just identifier (backward compatibility - params are implicitly uint32)
                params.append(self.expect(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.current_token() and self.current_token().type == TokenType.COMMA:
                self.advance()
                # Parse next parameter
                if self.current_token().type == TokenType.UINT32:
                    self.advance()
                    is_ptr_param = False
                    if self.current_token() and self.current_token().type == TokenType.MULTIPLY:
                        self.advance()  # consume *
                        is_ptr_param = True
                    param_name = self.expect(TokenType.IDENTIFIER, "Expected parameter name").value
                    params.append(param_name)
                else:
                    params.append(self.expect(TokenType.IDENTIFIER, "Expected parameter name").value)
        self.expect(TokenType.RPAREN)
        
        # Interrupt functions cannot have parameters
        if is_interrupt and len(params) > 0:
            raise SyntaxError(f"Interrupt function '{name}' cannot have parameters at line {name_token.line}")
        
        body = self.parse_block()
        
        return FunctionDef(name, params, body, is_interrupt=is_interrupt)
    
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
        
        # Variable declaration (can start with register, volatile, uint32, or int32)
        if (token.type == TokenType.UINT32 or
            token.type == TokenType.INT32 or
            token.type == TokenType.REGISTER or 
            token.type == TokenType.VOLATILE):
            return self.parse_var_decl()
        
        # Prefix increment/decrement
        if token.type == TokenType.INCREMENT:
            return self.parse_prefix_increment()
        
        if token.type == TokenType.DECREMENT:
            return self.parse_prefix_decrement()
        
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
        
        # Assignment, function call, or postfix increment/decrement (all start with identifier)
        if token.type == TokenType.IDENTIFIER:
            next_token = self.peek_token()
            if next_token and next_token.type == TokenType.LPAREN:
                # Function call statement
                call = self.parse_expression()  # Will parse as function call
                self.expect(TokenType.SEMICOLON)
                # Create a statement wrapper for function calls
                # We'll use a special Statement type for this
                return FunctionCallStmt(call)
            elif next_token and next_token.type == TokenType.LBRACKET:
                # Could be array assignment: arr[i] = value
                # Check if after [index] there's an =
                peek2 = self.peek_token(2)  # Skip identifier and [
                # We need to find the = after the ]
                # For now, just try to parse as assignment - parse_assignment will handle it
                return self.parse_assignment()
            elif next_token and next_token.type == TokenType.ASSIGN:
                # Assignment
                return self.parse_assignment()
            elif next_token and next_token.type == TokenType.INCREMENT:
                # Postfix increment: x++
                name_token = self.expect(TokenType.IDENTIFIER)
                self.expect(TokenType.INCREMENT)
                self.expect(TokenType.SEMICOLON)
                return Increment(name_token.value, is_prefix=False)
            elif next_token and next_token.type == TokenType.DECREMENT:
                # Postfix decrement: x--
                name_token = self.expect(TokenType.IDENTIFIER)
                self.expect(TokenType.DECREMENT)
                self.expect(TokenType.SEMICOLON)
                return Decrement(name_token.value, is_prefix=False)
        
        # Check for pointer dereference assignment: *ptr = value
        if token.type == TokenType.MULTIPLY:
            next_token = self.peek_token()
            if next_token:
                # Could be *ptr = value
                return self.parse_assignment()
        
        raise SyntaxError(f"Unexpected token in statement: {token} at line {token.line}")
    
    def parse_var_decl(self):
        """Parse a variable declaration (can be VarDecl, ArrayDecl, or PointerDecl)."""
        # Check for register, volatile, or interrupt keywords
        is_register = False
        is_volatile = False
        register_num = None
        
        # Parse optional register/volatile keywords
        while self.current_token():
            if self.current_token().type == TokenType.REGISTER:
                self.advance()
                is_register = True
            elif self.current_token().type == TokenType.VOLATILE:
                self.advance()
                is_volatile = True
            elif self.current_token().type in [TokenType.UINT32, TokenType.INT32]:
                break
            else:
                break
        
        # Parse type (uint32 or int32)
        var_type = 'uint32'  # default
        if self.current_token().type == TokenType.UINT32:
            self.advance()
            var_type = 'uint32'
        elif self.current_token().type == TokenType.INT32:
            self.advance()
            var_type = 'int32'
        else:
            raise SyntaxError(f"Expected uint32 or int32, got {self.current_token()} at line {self.current_token().line if self.current_token() else '?'}")
        
        # Check for pointer type: uint32* ptr or int32* ptr
        is_pointer = False
        if self.current_token() and self.current_token().type == TokenType.MULTIPLY:
            self.advance()  # consume *
            is_pointer = True
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        
        # Check for array declaration: uint32 arr[10] or uint32* arr[10]
        if self.current_token() and self.current_token().type == TokenType.LBRACKET:
            self.advance()  # consume [
            size_expr = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            
            # Check for array initializer: uint32 arr[5] = {1, 2, 3, 4, 5};
            array_initializer = None
            if self.current_token() and self.current_token().type == TokenType.ASSIGN:
                self.advance()  # consume =
                self.expect(TokenType.LBRACE)  # expect {
                array_initializer = []
                if self.current_token() and self.current_token().type != TokenType.RBRACE:
                    # Parse first value
                    array_initializer.append(self.parse_expression())
                    # Parse remaining values
                    while self.current_token() and self.current_token().type == TokenType.COMMA:
                        self.advance()  # consume ,
                        array_initializer.append(self.parse_expression())
                self.expect(TokenType.RBRACE)  # expect }
            
            self.expect(TokenType.SEMICOLON)
            return ArrayDecl(name, size_expr, array_initializer, is_register=is_register, is_volatile=is_volatile)
        
        # If pointer type, return PointerDecl
        if is_pointer:
            initializer = None
            if self.current_token() and self.current_token().type == TokenType.ASSIGN:
                self.advance()
                initializer = self.parse_expression()
            
            self.expect(TokenType.SEMICOLON)
            return PointerDecl(name, initializer, is_register=is_register, is_volatile=is_volatile)
        
        # If register, parse register number from name (e.g., r0, r1, ..., r31)
        if is_register:
            if name.startswith('r') and len(name) > 1:
                try:
                    register_num = int(name[1:])
                    if register_num < 0 or register_num > 31:
                        raise SyntaxError(f"Register number must be 0-31, got {register_num} at line {name_token.line}")
                except ValueError:
                    raise SyntaxError(f"Invalid register name: {name} at line {name_token.line}")
            else:
                raise SyntaxError(f"Register variables must be named r0-r31, got {name} at line {name_token.line}")
        
        initializer = None
        if self.current_token() and self.current_token().type == TokenType.ASSIGN:
            self.advance()
            initializer = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        return VarDecl(name, initializer, var_type=var_type, is_register=is_register, is_volatile=is_volatile, register_num=register_num)
    
    def parse_assignment(self):
        """Parse an assignment statement (can be Assignment, ArrayAssignment, or PointerAssignment)."""
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of file in assignment")
        
        # Check if this is pointer dereference assignment: *ptr = value
        if token.type == TokenType.MULTIPLY:
            self.advance()  # consume *
            operand = self.parse_expression()  # Parse the pointer expression
            self.expect(TokenType.ASSIGN)
            value = self.parse_expression()
            self.expect(TokenType.SEMICOLON)
            return PointerAssignment(operand, value)
        
        # Check if this is array assignment: arr[i] = value
        if token.type == TokenType.IDENTIFIER:
            name_token = self.advance()
            name = name_token.value
            if self.current_token() and self.current_token().type == TokenType.LBRACKET:
                # Array assignment: arr[i] = value
                self.advance()  # consume [
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                return ArrayAssignment(name, index, value)
            else:
                # Regular assignment
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                return Assignment(name, value)
        else:
            raise SyntaxError(f"Expected identifier or * in assignment at line {token.line if token else '?'}")
    
    def parse_prefix_increment(self) -> Increment:
        """Parse a prefix increment statement (++x)."""
        self.expect(TokenType.INCREMENT)
        name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after ++")
        self.expect(TokenType.SEMICOLON)
        return Increment(name_token.value, is_prefix=True)
    
    def parse_prefix_decrement(self) -> Decrement:
        """Parse a prefix decrement statement (--x)."""
        self.expect(TokenType.DECREMENT)
        name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after --")
        self.expect(TokenType.SEMICOLON)
        return Decrement(name_token.value, is_prefix=True)
    
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
        if self.current_token() and self.current_token().type in [TokenType.UINT32, TokenType.INT32]:
            # Variable declaration in for loop
            var_type = 'uint32'
            if self.current_token().type == TokenType.UINT32:
                self.advance()
                var_type = 'uint32'
            elif self.current_token().type == TokenType.INT32:
                self.advance()
                var_type = 'int32'
            
            name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name")
            name = name_token.value
            
            initializer = None
            if self.current_token() and self.current_token().type == TokenType.ASSIGN:
                self.advance()
                initializer = self.parse_expression()
            
            init = VarDecl(name, initializer, var_type=var_type)
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
            # Check for prefix increment/decrement
            if self.current_token().type == TokenType.INCREMENT:
                self.advance()
                name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after ++")
                increment = Increment(name_token.value, is_prefix=True)
            elif self.current_token().type == TokenType.DECREMENT:
                self.advance()
                name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name after --")
                increment = Decrement(name_token.value, is_prefix=True)
            elif self.current_token().type == TokenType.IDENTIFIER:
                name = self.current_token().value
                self.advance()
                # Check for postfix increment/decrement
                if self.current_token() and self.current_token().type == TokenType.INCREMENT:
                    self.advance()
                    increment = Increment(name, is_prefix=False)
                elif self.current_token() and self.current_token().type == TokenType.DECREMENT:
                    self.advance()
                    increment = Decrement(name, is_prefix=False)
                elif self.current_token() and self.current_token().type == TokenType.ASSIGN:
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
        left = self.parse_bitwise_or()
        while self.current_token() and self.current_token().type == TokenType.AND:
            op = self.advance()
            right = self.parse_bitwise_or()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_bitwise_or(self) -> Expression:
        """Parse bitwise OR expression."""
        left = self.parse_bitwise_xor()
        while self.current_token() and self.current_token().type == TokenType.BITWISE_OR:
            op = self.advance()
            right = self.parse_bitwise_xor()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_bitwise_xor(self) -> Expression:
        """Parse bitwise XOR expression."""
        left = self.parse_bitwise_and()
        while self.current_token() and self.current_token().type == TokenType.BITWISE_XOR:
            op = self.advance()
            right = self.parse_bitwise_and()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_bitwise_and(self) -> Expression:
        """Parse bitwise AND expression."""
        left = self.parse_equality()
        while self.current_token() and self.current_token().type == TokenType.BITWISE_AND:
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
    
    def parse_shift(self) -> Expression:
        """Parse shift expressions (<<, >>)."""
        left = self.parse_additive()
        while self.current_token() and self.current_token().type in [TokenType.SHIFT_LEFT, TokenType.SHIFT_RIGHT]:
            op = self.advance()
            # #region agent log
            with open('e:\\aiproj\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write('{"id":"log_parser_shift","timestamp":' + str(int(__import__('time').time() * 1000)) + ',"location":"parser.py:608","message":"Parsing shift operator","data":{"operator":"' + op.value + '","tokenType":"' + op.type.name + '"},"sessionId":"debug-session","runId":"post-fix","hypothesisId":"C"}\n')
            # #endregion agent log
            right = self.parse_additive()
            left = BinaryOp(op.value, left, right)
        return left
    
    def parse_relational(self) -> Expression:
        """Parse relational expressions."""
        left = self.parse_shift()
        while self.current_token() and self.current_token().type in [
            TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL
        ]:
            op = self.advance()
            right = self.parse_shift()
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
        # Check for address-of (&) operator
        if self.current_token() and self.current_token().type == TokenType.BITWISE_AND:
            # &x - address-of operator
            self.advance()  # consume &
            operand = self.parse_unary()  # Recursively parse operand (supports &*ptr, etc.)
            return AddressOf(operand)
        
        # Check for dereference (*) operator
        if self.current_token() and self.current_token().type == TokenType.MULTIPLY:
            # *ptr - dereference operator
            self.advance()  # consume *
            operand = self.parse_unary()  # Recursively parse operand (supports **ptr, etc.)
            return Dereference(operand)
        
        if self.current_token() and self.current_token().type in [TokenType.NOT, TokenType.MINUS]:
            op = self.advance()
            operand = self.parse_unary()
            return UnaryOp(op.value, operand)
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expression:
        """Parse postfix expressions (array access, etc.)."""
        expr = self.parse_primary()
        
        # Handle postfix array access: arr[i]
        while self.current_token() and self.current_token().type == TokenType.LBRACKET:
            self.advance()  # consume [
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            if isinstance(expr, Identifier):
                expr = ArrayAccess(expr.name, index)
            elif isinstance(expr, ArrayAccess):
                # Nested array access or pointer arithmetic result
                # For now, treat as array access of the result
                # This will be handled properly when we add pointer support
                expr = ArrayAccess(expr.name, index)
            else:
                # This is for pointer arithmetic like (ptr + i)[j] or *ptr[i]
                # For now, raise an error - will be handled when we add full pointer support
                raise SyntaxError(f"Array access on non-identifier expression at line {self.current_token().line if self.current_token() else '?'}")
        
        return expr
    
    def parse_primary(self) -> Expression:
        """Parse primary expressions."""
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of file in expression")
        
        # Literal
        if token.type == TokenType.LITERAL:
            self.advance()
            try:
                # int(value, 0) auto-detects base: 0x for hex, no prefix for decimal
                return Literal(int(token.value, 0))
            except ValueError as e:
                raise SyntaxError(f"Invalid numeric literal: {token.value} at line {token.line}, column {token.column}")
        
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
