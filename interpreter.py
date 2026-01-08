"""
Interpreter for Simple C-Style Language
Evaluates the AST and executes the program.
"""

from typing import Dict, Optional, List, Any
from parser import (
    Program, FunctionDef, Statement, Expression,
    Literal, Identifier, BinaryOp, UnaryOp, FunctionCall,
    VarDecl, Assignment, Return, IfStmt, WhileStmt, ForStmt,
    Block, FunctionCallStmt
)


class RuntimeError(Exception):
    """Runtime error during program execution."""
    pass


class Environment:
    """Represents a scope/environment for variable bindings."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.vars: Dict[str, int] = {}
        self.parent = parent
    
    def get(self, name: str) -> int:
        """Get a variable value, checking parent scopes."""
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: int):
        """Set a variable in the current scope."""
        self.vars[name] = value & 0xFFFFFFFF  # Ensure 32-bit unsigned
    
    def declare(self, name: str, value: Optional[int] = None):
        """Declare a variable in the current scope."""
        if value is not None:
            self.vars[name] = value & 0xFFFFFFFF
        else:
            self.vars[name] = 0
    
    def assign(self, name: str, value: int) -> bool:
        """Assign to a variable, checking parent scopes."""
        if name in self.vars:
            self.vars[name] = value & 0xFFFFFFFF
            return True
        if self.parent:
            return self.parent.assign(name, value)
        raise RuntimeError(f"Undefined variable: {name}")


class Interpreter:
    """Interpreter for executing the AST."""
    
    def __init__(self, program: Program):
        self.program = program
        self.functions: Dict[str, FunctionDef] = {}
        self.global_env = Environment()
        
        # Register all functions
        for func in program.functions:
            self.functions[func.name] = func
    
    def interpret(self) -> int:
        """Interpret the program, starting from main."""
        if 'main' not in self.functions:
            raise RuntimeError("Program must have a 'main' function")
        
        main_func = self.functions['main']
        if len(main_func.params) != 0:
            raise RuntimeError("'main' function must take no parameters")
        
        return self.execute_function(main_func, [], self.global_env)
    
    def execute_function(self, func: FunctionDef, args: List[int], 
                        caller_env: Environment) -> int:
        """Execute a function call."""
        if len(args) != len(func.params):
            raise RuntimeError(
                f"Function '{func.name}' expects {len(func.params)} arguments, "
                f"got {len(args)}"
            )
        
        # Create new environment for function (with caller as parent for closures if needed)
        env = Environment(caller_env)
        
        # Bind parameters
        for param, arg_value in zip(func.params, args):
            env.declare(param, arg_value & 0xFFFFFFFF)
        
        # Execute function body
        try:
            self.execute_block(func.body, env)
            return 0  # Default return value if no return statement
        except ReturnException as e:
            return e.value & 0xFFFFFFFF
    
    def execute_statement(self, stmt: Statement, env: Environment):
        """Execute a statement."""
        if isinstance(stmt, VarDecl):
            self.execute_var_decl(stmt, env)
        elif isinstance(stmt, Assignment):
            self.execute_assignment(stmt, env)
        elif isinstance(stmt, Return):
            self.execute_return(stmt, env)
        elif isinstance(stmt, IfStmt):
            self.execute_if(stmt, env)
        elif isinstance(stmt, WhileStmt):
            self.execute_while(stmt, env)
        elif isinstance(stmt, ForStmt):
            self.execute_for(stmt, env)
        elif isinstance(stmt, Block):
            self.execute_block(stmt, env)
        elif isinstance(stmt, FunctionCallStmt):
            self.execute_function_call(stmt.call, env)
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")
    
    def execute_block(self, block: Block, env: Environment):
        """Execute a block of statements."""
        # Create new scope for block
        block_env = Environment(env)
        for stmt in block.statements:
            self.execute_statement(stmt, block_env)
    
    def execute_var_decl(self, decl: VarDecl, env: Environment):
        """Execute a variable declaration."""
        value = 0
        if decl.initializer:
            value = self.evaluate_expression(decl.initializer, env)
        env.declare(decl.name, value)
    
    def execute_assignment(self, assignment: Assignment, env: Environment):
        """Execute an assignment."""
        value = self.evaluate_expression(assignment.value, env)
        env.assign(assignment.name, value)
    
    def execute_return(self, ret: Return, env: Environment):
        """Execute a return statement."""
        value = 0
        if ret.value:
            value = self.evaluate_expression(ret.value, env)
        raise ReturnException(value)
    
    def execute_if(self, if_stmt: IfStmt, env: Environment):
        """Execute an if statement."""
        condition = self.evaluate_expression(if_stmt.condition, env)
        if condition != 0:  # Non-zero is truthy
            self.execute_statement(if_stmt.then_stmt, env)
        elif if_stmt.else_stmt:
            self.execute_statement(if_stmt.else_stmt, env)
    
    def execute_while(self, while_stmt: WhileStmt, env: Environment):
        """Execute a while loop."""
        while True:
            condition = self.evaluate_expression(while_stmt.condition, env)
            if condition == 0:  # Zero is falsy
                break
            self.execute_statement(while_stmt.body, env)
    
    def execute_for(self, for_stmt: ForStmt, env: Environment):
        """Execute a for loop."""
        # Create scope for for loop
        for_env = Environment(env)
        
        # Initialize
        if for_stmt.init:
            if isinstance(for_stmt.init, VarDecl):
                self.execute_var_decl(for_stmt.init, for_env)
            elif isinstance(for_stmt.init, Assignment):
                self.execute_assignment(for_stmt.init, for_env)
        
        # Loop condition and body
        while True:
            if for_stmt.condition:
                condition = self.evaluate_expression(for_stmt.condition, for_env)
                if condition == 0:  # Zero is falsy
                    break
            
            # Execute body
            self.execute_statement(for_stmt.body, for_env)
            
            # Increment
            if for_stmt.increment:
                self.execute_assignment(for_stmt.increment, for_env)
    
    def execute_function_call(self, call: FunctionCall, env: Environment) -> int:
        """Execute a function call and return its value."""
        if call.name not in self.functions:
            raise RuntimeError(f"Undefined function: {call.name}")
        
        func = self.functions[call.name]
        args = [self.evaluate_expression(arg, env) for arg in call.args]
        return self.execute_function(func, args, env)
    
    def evaluate_expression(self, expr: Expression, env: Environment) -> int:
        """Evaluate an expression and return its value."""
        if isinstance(expr, Literal):
            return expr.value & 0xFFFFFFFF
        
        elif isinstance(expr, Identifier):
            return env.get(expr.name) & 0xFFFFFFFF
        
        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr, env)
        
        elif isinstance(expr, UnaryOp):
            return self.evaluate_unary_op(expr, env)
        
        elif isinstance(expr, FunctionCall):
            return self.execute_function_call(expr, env)
        
        else:
            raise RuntimeError(f"Unknown expression type: {type(expr)}")
    
    def evaluate_binary_op(self, op: BinaryOp, env: Environment) -> int:
        """Evaluate a binary operation."""
        left = self.evaluate_expression(op.left, env)
        right = self.evaluate_expression(op.right, env)
        
        op_map = {
            '+': lambda l, r: (l + r) & 0xFFFFFFFF,
            '-': lambda l, r: (l - r) & 0xFFFFFFFF,
            '*': lambda l, r: (l * r) & 0xFFFFFFFF,
            '/': lambda l, r: (l // r) & 0xFFFFFFFF if r != 0 else self._error("Division by zero"),
            '%': lambda l, r: (l % r) & 0xFFFFFFFF if r != 0 else self._error("Modulo by zero"),
            '==': lambda l, r: 1 if l == r else 0,
            '!=': lambda l, r: 1 if l != r else 0,
            '<': lambda l, r: 1 if l < r else 0,
            '<=': lambda l, r: 1 if l <= r else 0,
            '>': lambda l, r: 1 if l > r else 0,
            '>=': lambda l, r: 1 if l >= r else 0,
            '&&': lambda l, r: 1 if (l != 0 and r != 0) else 0,
            '||': lambda l, r: 1 if (l != 0 or r != 0) else 0,
        }
        
        if op.op not in op_map:
            raise RuntimeError(f"Unknown binary operator: {op.op}")
        
        result = op_map[op.op](left, right)
        return result & 0xFFFFFFFF
    
    def evaluate_unary_op(self, op: UnaryOp, env: Environment) -> int:
        """Evaluate a unary operation."""
        operand = self.evaluate_expression(op.operand, env)
        
        if op.op == '-':
            return (-operand) & 0xFFFFFFFF
        elif op.op == '!':
            return 0 if operand != 0 else 1
        else:
            raise RuntimeError(f"Unknown unary operator: {op.op}")
    
    def _error(self, msg: str):
        """Raise a runtime error."""
        raise RuntimeError(msg)


class ReturnException(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: int):
        self.value = value
        super().__init__()
