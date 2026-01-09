"""
Interpreter for Simple C-Style Language

This module evaluates the AST and executes the program. The interpreter:
- Manages variable scoping through Environment objects
- Executes control flow statements (if, while, for)
- Handles function calls and recursion
- Provides built-in hardware functions (GPIO, UART, Timer)
- Simulates CPU registers (r0-r31)
- Supports interrupt service routines (ISRs)

Runtime State:
- global_env: Global variable environment
- functions: Dictionary of function definitions
- registers: Array of 32 CPU registers
- interrupt_handlers: Dictionary of ISR functions
- Hardware state: GPIO, UART, Timer simulation
"""

from typing import Dict, Optional, List, Any, Tuple
import os
import sys
from parser import (
    Program, FunctionDef, Statement, Expression,
    Literal, Identifier, BinaryOp, UnaryOp, FunctionCall,
    VarDecl, Assignment, Return, IfStmt, WhileStmt, ForStmt,
    Block, FunctionCallStmt, Increment, Decrement,
    ArrayDecl, ArrayAccess, PointerDecl, AddressOf, Dereference,
    ArrayAssignment, PointerAssignment, BreakStmt, ContinueStmt
)


class RuntimeError(Exception):
    """Runtime error during program execution."""
    pass


class BreakException(Exception):
    """Exception raised by break statement to exit loop."""
    pass


class ContinueException(Exception):
    """Exception raised by continue statement to skip to next iteration."""
    pass


class Environment:
    """Represents a scope/environment for variable bindings."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.vars: Dict[str, int] = {}  # Обычные переменные и указатели
        self.arrays: Dict[str, List[int]] = {}  # Массивы
        self.variable_addresses: Dict[str, int] = {}  # Адреса переменных (для &)
        self.array_addresses: Dict[str, int] = {}  # Адреса массивов (базовый адрес)
        self.next_address: int = 1000  # Начальный адрес для выделения памяти
        self.var_types: Dict[str, str] = {}  # Track variable types: 'uint32' or 'int32'
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
    
    def declare(self, name: str, value: Optional[int] = None, var_type: str = 'uint32'):
        """Declare a variable in the current scope."""
        if value is not None:
            self.vars[name] = value & 0xFFFFFFFF
        else:
            self.vars[name] = 0
        self.var_types[name] = var_type
    
    def get_type(self, name: str) -> str:
        """Get the type of a variable, checking parent scopes."""
        if name in self.var_types:
            return self.var_types[name]
        if self.parent:
            return self.parent.get_type(name)
        return 'uint32'  # Default type if not found
    
    def assign(self, name: str, value: int, var_type: Optional[str] = None) -> bool:
        """Assign to a variable, checking parent scopes."""
        if name in self.vars:
            self.vars[name] = value & 0xFFFFFFFF
            if var_type is not None:
                self.var_types[name] = var_type
            return True
        if self.parent:
            return self.parent.assign(name, value, var_type)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def declare_array(self, name: str, size: int) -> int:
        """Declare an array and return its base address."""
        if size <= 0:
            raise RuntimeError(f"Array size must be positive, got {size}")
        # Allocate array initialized with zeros
        self.arrays[name] = [0] * size
        # Assign base address
        base_addr = self.next_address
        self.array_addresses[name] = base_addr
        # Update next_address (each element is 1 memory cell = 4 bytes, but we address in cells)
        self.next_address += size
        return base_addr
    
    def get_array_element(self, name: str, index: int) -> int:
        """Get an array element with bounds checking."""
        if name in self.arrays:
            arr = self.arrays[name]
            if index < 0 or index >= len(arr):
                raise RuntimeError(f"Array index out of bounds: {name}[{index}], size={len(arr)}")
            return arr[index] & 0xFFFFFFFF
        if self.parent:
            return self.parent.get_array_element(name, index)
        raise RuntimeError(f"Undefined array: {name}")
    
    def set_array_element(self, name: str, index: int, value: int):
        """Set an array element with bounds checking."""
        if name in self.arrays:
            arr = self.arrays[name]
            if index < 0 or index >= len(arr):
                raise RuntimeError(f"Array index out of bounds: {name}[{index}], size={len(arr)}")
            arr[index] = value & 0xFFFFFFFF
            return
        if self.parent:
            self.parent.set_array_element(name, index, value)
            return
        raise RuntimeError(f"Undefined array: {name}")
    
    def get_address(self, name: str) -> int:
        """Get the address of a variable or array."""
        # Check for variable
        if name in self.vars:
            if name not in self.variable_addresses:
                # Assign address if not already assigned
                addr = self.next_address
                self.variable_addresses[name] = addr
                self.next_address += 1  # Each variable takes 1 memory cell
                return addr
            return self.variable_addresses[name]
        
        # Check for array
        if name in self.arrays:
            if name not in self.array_addresses:
                # Should not happen - arrays should have addresses assigned on declaration
                raise RuntimeError(f"Array {name} has no assigned address")
            return self.array_addresses[name]
        
        # Check parent scope
        if self.parent:
            return self.parent.get_address(name)
        
        raise RuntimeError(f"Undefined variable or array: {name}")
    
    def get_value_at_address(self, address: int) -> int:
        """Get value at a memory address."""
        # Search for variable at this address
        for name, addr in self.variable_addresses.items():
            if addr == address:
                return self.vars.get(name, 0) & 0xFFFFFFFF
        
        # Search for array element at this address
        for name, base_addr in self.array_addresses.items():
            if name in self.arrays:
                arr = self.arrays[name]
                if base_addr <= address < base_addr + len(arr):
                    index = address - base_addr
                    return arr[index] & 0xFFFFFFFF
        
        # Check parent scope
        if self.parent:
            return self.parent.get_value_at_address(address)
        
        raise RuntimeError(f"Invalid memory address: {address}")
    
    def set_value_at_address(self, address: int, value: int):
        """Set value at a memory address."""
        # Search for variable at this address
        for name, addr in self.variable_addresses.items():
            if addr == address:
                self.vars[name] = value & 0xFFFFFFFF
                return
        
        # Search for array element at this address
        for name, base_addr in self.array_addresses.items():
            if name in self.arrays:
                arr = self.arrays[name]
                if base_addr <= address < base_addr + len(arr):
                    index = address - base_addr
                    arr[index] = value & 0xFFFFFFFF
                    return
        
        # Check parent scope
        if self.parent:
            self.parent.set_value_at_address(address, value)
            return
        
        raise RuntimeError(f"Invalid memory address: {address}")


class Interpreter:
    """Interpreter for executing the AST."""
    
    def __init__(self, program: Program):
        self.program = program
        self.functions: Dict[str, FunctionDef] = {}
        self.global_env = Environment()
        
        # Hardware registers (r0-r31), r31 is instruction pointer (read-only in user code)
        self.registers: List[int] = [0] * 32
        
        # Hardware state for peripherals
        self.gpio_state: Dict[int, Dict[str, int]] = {}  # pin -> {direction, mode, value}
        self.uart_state: Dict[str, int] = {"baud_rate": 115200, "tx_ready": 1, "rx_ready": 0, "data": 0}
        self.timer_state: Dict[str, int] = {"mode": 0, "period": 0, "value": 0, "running": 0, "expired": 0}
        
        # Register mapping for variables
        self.register_map: Dict[str, int] = {}  # variable name -> register number
        
        # Register all functions
        for func in program.functions:
            self.functions[func.name] = func
    
    @staticmethod
    def uint32_to_int32(value: int) -> int:
        """Convert uint32 to int32 (interpret as signed).
        Values >= 2^31 are interpreted as negative using two's complement.
        """
        value = value & 0xFFFFFFFF
        if value >= 0x80000000:  # If MSB is set, it's negative
            return value - 0x100000000  # Convert to negative
        return value
    
    @staticmethod
    def int32_to_uint32(value: int) -> int:
        """Convert int32 to uint32 (preserve bit representation).
        Negative values are converted using two's complement.
        """
        return value & 0xFFFFFFFF
    
    @staticmethod
    def normalize_int32(value: int) -> int:
        """Normalize value to int32 range (-2^31 to 2^31-1)."""
        value = value & 0xFFFFFFFF
        if value >= 0x80000000:
            return value - 0x100000000
        return value
    
    @staticmethod
    def normalize_uint32(value: int) -> int:
        """Normalize value to uint32 range (0 to 2^32-1)."""
        return value & 0xFFFFFFFF
    
    def interpret(self) -> int:
        """Interpret the program, starting from main."""
        # Declare global variables first
        for global_var in self.program.global_vars:
            self.execute_var_decl(global_var, self.global_env)
        
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
        elif isinstance(stmt, ArrayDecl):
            self.execute_array_decl(stmt, env)
        elif isinstance(stmt, PointerDecl):
            self.execute_pointer_decl(stmt, env)
        elif isinstance(stmt, Assignment):
            self.execute_assignment(stmt, env)
        elif isinstance(stmt, ArrayAssignment):
            self.execute_array_assignment(stmt, env)
        elif isinstance(stmt, PointerAssignment):
            self.execute_pointer_assignment(stmt, env)
        elif isinstance(stmt, Increment):
            self.execute_increment(stmt, env)
        elif isinstance(stmt, Decrement):
            self.execute_decrement(stmt, env)
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
        elif isinstance(stmt, BreakStmt):
            self.execute_break(stmt, env)
        elif isinstance(stmt, ContinueStmt):
            self.execute_continue(stmt, env)
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
        var_type = getattr(decl, 'var_type', 'uint32')  # Default to uint32 for backward compatibility
        value = 0
        if decl.initializer:
            # Evaluate expression - we'll get the type from evaluate_expression later
            try:
                result = self.evaluate_expression_with_type(decl.initializer, env)
                value, expr_type = result
            except Exception as e:
                raise
            # Convert if needed: if target type is int32, convert the value appropriately
            if var_type == 'int32':
                if expr_type == 'uint32':
                    # Convert uint32 to int32 (interpret as signed)
                    value = self.normalize_int32(value)
                else:
                    # Already int32, just normalize
                    value = self.normalize_int32(value)
            else:
                # Target is uint32
                if expr_type == 'int32':
                    # Convert int32 to uint32 (preserve bits)
                    value = self.int32_to_uint32(value)
                else:
                    # Already uint32, just normalize
                    value = self.normalize_uint32(value)
        else:
            # No initializer, just normalize based on type
            if var_type == 'int32':
                value = self.normalize_int32(0)
            else:
                value = self.normalize_uint32(0)
        
        if decl.is_register:
            # Register variable - store in hardware register
            if decl.register_num is not None:
                self.registers[decl.register_num] = value & 0xFFFFFFFF
                self.register_map[decl.name] = decl.register_num
                # Also store in environment for lookup
                env.declare(decl.name, value, var_type=var_type)
        else:
            # Normal variable
            env.declare(decl.name, value, var_type=var_type)
    
    def execute_array_decl(self, decl: ArrayDecl, env: Environment):
        """Execute an array declaration."""
        # Evaluate size (must be a literal constant)
        if not isinstance(decl.size, Literal):
            raise RuntimeError(f"Array size must be a constant literal, got {type(decl.size)}")
        size = decl.size.value
        if size <= 0:
            raise RuntimeError(f"Array size must be positive, got {size}")
        
        # Declare array in environment
        env.declare_array(decl.name, size)
        
        # Initialize array with values if provided
        if decl.initializer:
            if len(decl.initializer) > size:
                raise RuntimeError(f"Too many initializers for array {decl.name}: got {len(decl.initializer)}, expected at most {size}")
            
            for i, init_expr in enumerate(decl.initializer):
                value = self.evaluate_expression(init_expr, env)
                env.set_array_element(decl.name, i, value)
    
    def execute_pointer_decl(self, decl: PointerDecl, env: Environment):
        """Execute a pointer declaration."""
        value = 0
        if decl.initializer:
            # Initializer should be AddressOf expression
            value = self.evaluate_expression(decl.initializer, env)
        
        # Store pointer value (address) as a regular variable
        env.declare(decl.name, value)
    
    def execute_assignment(self, assignment: Assignment, env: Environment):
        """Execute an assignment with automatic type conversion."""
        # Get expression value and type
        value, expr_type = self.evaluate_expression_with_type(assignment.value, env)
        
        # Get target variable type (default to uint32 if not found)
        target_type = env.get_type(assignment.name)
        
        # Perform type conversion if needed
        if target_type == 'int32':
            if expr_type == 'uint32':
                # Convert uint32 to int32 (interpret as signed)
                value = self.uint32_to_int32(value)
            value = self.normalize_int32(value)
        else:
            # Target is uint32
            if expr_type == 'int32':
                # Convert int32 to uint32 (preserve bit representation)
                value = self.int32_to_uint32(value)
            value = self.normalize_uint32(value)
        
        # Check if this is a register variable
        if assignment.name in self.register_map:
            reg_num = self.register_map[assignment.name]
            if reg_num == 31:
                raise RuntimeError("Cannot write to register r31 (instruction pointer)")
            self.registers[reg_num] = value & 0xFFFFFFFF
            # Also update in environment
            env.assign(assignment.name, value, var_type=target_type)
        else:
            env.assign(assignment.name, value, var_type=target_type)
    
    def execute_array_assignment(self, assignment: ArrayAssignment, env: Environment):
        """Execute an array element assignment: arr[i] = value"""
        index = self.evaluate_expression(assignment.index, env)
        value = self.evaluate_expression(assignment.value, env)
        env.set_array_element(assignment.name, index, value)
    
    def execute_pointer_assignment(self, assignment: PointerAssignment, env: Environment):
        """Execute a pointer dereference assignment: *ptr = value"""
        address = self.evaluate_expression(assignment.operand, env)
        value = self.evaluate_expression(assignment.value, env)
        env.set_value_at_address(address, value)
    
    def execute_increment(self, increment: Increment, env: Environment):
        """Execute an increment statement (++x or x++)."""
        current_value = env.get(increment.name)
        new_value = (current_value + 1) & 0xFFFFFFFF
        env.assign(increment.name, new_value)
    
    def execute_decrement(self, decrement: Decrement, env: Environment):
        """Execute a decrement statement (--x or x--)."""
        current_value = env.get(decrement.name)
        new_value = (current_value - 1) & 0xFFFFFFFF
        env.assign(decrement.name, new_value)
    
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
            try:
                self.execute_statement(while_stmt.body, env)
            except BreakException:
                break
            except ContinueException:
                continue
    
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
            try:
                self.execute_statement(for_stmt.body, for_env)
            except BreakException:
                break
            except ContinueException:
                # For continue, skip to increment
                if for_stmt.increment:
                    self.execute_statement(for_stmt.increment, for_env)
                continue
            
            # Increment
            if for_stmt.increment:
                self.execute_statement(for_stmt.increment, for_env)
    
    def execute_break(self, stmt: BreakStmt, env: Environment):
        """Execute a break statement."""
        raise BreakException()
    
    def execute_continue(self, stmt: ContinueStmt, env: Environment):
        """Execute a continue statement."""
        raise ContinueException()
    
    def execute_function_call(self, call: FunctionCall, env: Environment) -> int:
        """Execute a function call and return its value."""
        # Check if this is a hardware library function
        if self.is_hardware_function(call.name):
            return self.execute_hardware_function(call, env)
        
        if call.name not in self.functions:
            raise RuntimeError(f"Undefined function: {call.name}")
        
        func = self.functions[call.name]
        args = [self.evaluate_expression(arg, env) for arg in call.args]
        return self.execute_function(func, args, env)
    
    def evaluate_expression(self, expr: Expression, env: Environment) -> int:
        """Evaluate an expression and return its value."""
        value, _ = self.evaluate_expression_with_type(expr, env)
        return value
    
    def evaluate_expression_with_type(self, expr: Expression, env: Environment) -> Tuple[int, str]:
        """Evaluate an expression and return (value, type) where type is 'uint32' or 'int32'."""
        if isinstance(expr, Literal):
            value = expr.value & 0xFFFFFFFF
            # Literals are treated as uint32 by default (unless they're negative, but we don't support that in lexer)
            return value, 'uint32'
        
        elif isinstance(expr, Identifier):
            # Check if this is a register variable
            if expr.name in self.register_map:
                reg_num = self.register_map[expr.name]
                value = self.registers[reg_num] & 0xFFFFFFFF
                # Get type from environment if available, default to uint32
                var_type = env.get_type(expr.name) if hasattr(env, 'get_type') else 'uint32'
                return value, var_type
            value = env.get(expr.name) & 0xFFFFFFFF
            var_type = env.get_type(expr.name)
            return value, var_type
        
        elif isinstance(expr, ArrayAccess):
            result = self.evaluate_array_access(expr, env)
            return result
        
        elif isinstance(expr, AddressOf):
            result = self.evaluate_address_of(expr, env)
            return result
        
        elif isinstance(expr, Dereference):
            result = self.evaluate_dereference(expr, env)
            return result
        
        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op_with_type(expr, env)
        
        elif isinstance(expr, UnaryOp):
            return self.evaluate_unary_op_with_type(expr, env)
        
        elif isinstance(expr, FunctionCall):
            value = self.execute_function_call(expr, env)
            # Function calls return uint32 by default (unless we track return types, which we don't yet)
            return value, 'uint32'
        
        else:
            raise RuntimeError(f"Unknown expression type: {type(expr)}")
    
    def evaluate_binary_op(self, op: BinaryOp, env: Environment) -> int:
        """Evaluate a binary operation."""
        value, _ = self.evaluate_binary_op_with_type(op, env)
        return value
    
    def evaluate_binary_op_with_type(self, op: BinaryOp, env: Environment) -> Tuple[int, str]:
        """Evaluate a binary operation and return (value, type)."""
        left_val, left_type = self.evaluate_expression_with_type(op.left, env)
        right_val, right_type = self.evaluate_expression_with_type(op.right, env)
        
        # Determine result type based on operation and operand types
        # For comparisons and logical ops, result is always uint32 (0 or 1)
        comparison_ops = {'==', '!=', '<', '<=', '>', '>=', '&&', '||'}
        bitwise_ops = {'&', '|', '^', '<<', '>>'}
        arithmetic_ops = {'+', '-', '*', '/', '%'}
        
        # For comparisons and logical operations, convert both operands to same type before comparing
        if op.op in comparison_ops:
            # Convert both to int32 if either is int32 (for signed comparison)
            if left_type == 'int32' or right_type == 'int32':
                if left_type == 'uint32':
                    left_val = self.uint32_to_int32(left_val)
                if right_type == 'uint32':
                    right_val = self.uint32_to_int32(right_val)
                # For comparisons, result is always uint32 (0 or 1)
                result_type = 'uint32'
            else:
                result_type = 'uint32'
        elif op.op in arithmetic_ops:
            # Arithmetic operations: if any operand is int32, result is int32
            if left_type == 'int32' or right_type == 'int32':
                # Convert uint32 to int32 for signed arithmetic
                if left_type == 'uint32':
                    left_val = self.uint32_to_int32(left_val)
                if right_type == 'uint32':
                    right_val = self.uint32_to_int32(right_val)
                result_type = 'int32'
            else:
                result_type = 'uint32'
        elif op.op in bitwise_ops:
            # Bitwise operations preserve types - if any is int32, result is int32
            if left_type == 'int32' or right_type == 'int32':
                if left_type == 'uint32':
                    left_val = self.uint32_to_int32(left_val)
                if right_type == 'uint32':
                    right_val = self.uint32_to_int32(right_val)
                result_type = 'int32'
            else:
                result_type = 'uint32'
        else:
            result_type = 'uint32'  # Default
        
        # Perform the operation
        op_map = {
            '+': lambda l, r: (l + r) & 0xFFFFFFFF,
            '-': lambda l, r: (l - r) & 0xFFFFFFFF,
            '*': lambda l, r: (l * r) & 0xFFFFFFFF,
            '/': lambda l, r: (l // r) & 0xFFFFFFFF if r != 0 else self._error("Division by zero"),
            '%': lambda l, r: (l % r) & 0xFFFFFFFF if r != 0 else self._error("Modulo by zero"),
            '<<': lambda l, r: ((l << (r & 0x1F)) & 0xFFFFFFFF),  # Shift left, limit shift to 31 bits
            '>>': lambda l, r: ((l >> (r & 0x1F)) & 0xFFFFFFFF),  # Shift right, limit shift to 31 bits
            '==': lambda l, r: 1 if l == r else 0,
            '!=': lambda l, r: 1 if l != r else 0,
            '<': lambda l, r: 1 if l < r else 0,
            '<=': lambda l, r: 1 if l <= r else 0,
            '>': lambda l, r: 1 if l > r else 0,
            '>=': lambda l, r: 1 if l >= r else 0,
            '&&': lambda l, r: 1 if (l != 0 and r != 0) else 0,
            '||': lambda l, r: 1 if (l != 0 or r != 0) else 0,
            '&': lambda l, r: (l & r) & 0xFFFFFFFF,
            '|': lambda l, r: (l | r) & 0xFFFFFFFF,
            '^': lambda l, r: (l ^ r) & 0xFFFFFFFF,
        }
        
        if op.op not in op_map:
            raise RuntimeError(f"Unknown binary operator: {op.op}")
        
        result = op_map[op.op](left_val, right_val)
        
        # Normalize result based on type
        if result_type == 'int32':
            result = self.normalize_int32(result)
        else:
            result = self.normalize_uint32(result)
        
        return result, result_type
    
    def evaluate_unary_op(self, op: UnaryOp, env: Environment) -> int:
        """Evaluate a unary operation."""
        value, _ = self.evaluate_unary_op_with_type(op, env)
        return value
    
    def evaluate_unary_op_with_type(self, op: UnaryOp, env: Environment) -> Tuple[int, str]:
        """Evaluate a unary operation and return (value, type)."""
        operand_val, operand_type = self.evaluate_expression_with_type(op.operand, env)
        
        # For unary minus, result type is int32 (even if operand is uint32, we convert it)
        # For logical not, result is always uint32 (0 or 1)
        # For bitwise not, result type matches operand type
        if op.op == '-':
            # Unary minus: convert to int32 if needed, then negate
            if operand_type == 'uint32':
                operand_val = self.uint32_to_int32(operand_val)
            result = (-operand_val) & 0xFFFFFFFF
            result_type = 'int32'
            result = self.normalize_int32(result)
        elif op.op == '!':
            # Logical not: result is always uint32
            result = 0 if operand_val != 0 else 1
            result_type = 'uint32'
        elif op.op == '~':
            # Bitwise not: preserve type
            result = (~operand_val) & 0xFFFFFFFF
            result_type = operand_type
            if result_type == 'int32':
                result = self.normalize_int32(result)
            else:
                result = self.normalize_uint32(result)
        else:
            raise RuntimeError(f"Unknown unary operator: {op.op}")
        
        return result, result_type
    
    def evaluate_array_access(self, expr: ArrayAccess, env: Environment) -> Tuple[int, str]:
        """Evaluate array element access: arr[index]"""
        index = self.evaluate_expression(expr.index, env)
        value = env.get_array_element(expr.name, index)
        # Get array element type - default to 'uint32' if not explicitly stored
        # Arrays don't have explicit type tracking, so we use default 'uint32'
        element_type = 'uint32'
        return value, element_type
    
    def evaluate_address_of(self, expr: AddressOf, env: Environment) -> Tuple[int, str]:
        """Evaluate address-of operator: &x"""
        operand = expr.operand
        # Address-of always returns a uint32 (addresses are unsigned 32-bit)
        address_type = 'uint32'
        
        if isinstance(operand, Identifier):
            # &variable
            value = env.get_address(operand.name)
            return value, address_type
        elif isinstance(operand, ArrayAccess):
            # &arr[i] - address of array element
            arr_name = operand.name
            index = self.evaluate_expression(operand.index, env)
            base_addr = env.get_address(arr_name)
            # Each element is 1 memory cell, so address = base + index
            value = (base_addr + index) & 0xFFFFFFFF
            return value, address_type
        elif isinstance(operand, Dereference):
            # &*ptr - address that ptr points to (just the value of ptr)
            value = self.evaluate_expression(operand.operand, env)
            return value, address_type
        else:
            raise RuntimeError(f"Cannot take address of {type(operand)}")
    
    def evaluate_dereference(self, expr: Dereference, env: Environment) -> Tuple[int, str]:
        """Evaluate pointer dereference: *ptr"""
        # Get the address (value of the pointer)
        address = self.evaluate_expression(expr.operand, env)
        # Get value at that address
        value = env.get_value_at_address(address)
        # Determine the type of what's at the address
        # We try to find the variable/array element at this address to get its type
        deref_type = 'uint32'  # Default type
        # Search for variable at this address to get its type
        if hasattr(env, 'variable_addresses'):
            for name, addr in env.variable_addresses.items():
                if addr == address:
                    deref_type = env.get_type(name) if hasattr(env, 'get_type') else 'uint32'
                    break
        # If not found as variable, check if it's an array element
        if deref_type == 'uint32' and hasattr(env, 'array_addresses'):
            for name, base_addr in env.array_addresses.items():
                if name in env.arrays:
                    arr = env.arrays[name]
                    if base_addr <= address < base_addr + len(arr):
                        # Array elements don't have explicit types, default to 'uint32'
                        deref_type = 'uint32'
                        break
        return value, deref_type
    
    def _error(self, msg: str):
        """Raise a runtime error."""
        raise RuntimeError(msg)
    
    def is_hardware_function(self, name: str) -> bool:
        """Check if function name is a hardware library function."""
        hardware_functions = [
            'gpio_set', 'gpio_read', 'gpio_write',
            'uart_set_baud', 'uart_get_status', 'uart_read', 'uart_write',
            'timer_set_mode', 'timer_set_period', 'timer_start', 'timer_stop',
            'timer_reset', 'timer_get_value', 'timer_expired',
            'delay_ms', 'delay_us', 'delay_cycles',
            'enable_interrupts', 'disable_interrupts',
            'set_bit', 'clear_bit', 'toggle_bit', 'get_bit'
        ]
        return name in hardware_functions
    
    def execute_hardware_function(self, call: FunctionCall, env: Environment) -> int:
        """Execute a hardware library function."""
        name = call.name
        args = [self.evaluate_expression(arg, env) for arg in call.args]
        
        # GPIO functions
        if name == 'gpio_set':
            if len(args) != 3:
                raise RuntimeError(f"gpio_set expects 3 arguments, got {len(args)}")
            pin, direction, mode = args
            self.gpio_state[pin] = {"direction": direction, "mode": mode, "value": 0}
            return 0
        
        elif name == 'gpio_read':
            if len(args) != 1:
                raise RuntimeError(f"gpio_read expects 1 argument, got {len(args)}")
            pin = args[0]
            if pin not in self.gpio_state:
                raise RuntimeError(f"GPIO pin {pin} not configured")
            return self.gpio_state[pin].get("value", 0)
        
        elif name == 'gpio_write':
            if len(args) != 2:
                raise RuntimeError(f"gpio_write expects 2 arguments, got {len(args)}")
            pin, value = args
            if pin not in self.gpio_state:
                raise RuntimeError(f"GPIO pin {pin} not configured")
            self.gpio_state[pin]["value"] = value & 1
            return 0
        
        # UART functions
        elif name == 'uart_set_baud':
            if len(args) != 1:
                raise RuntimeError(f"uart_set_baud expects 1 argument, got {len(args)}")
            self.uart_state["baud_rate"] = args[0]
            return 0
        
        elif name == 'uart_get_status':
            return (self.uart_state["tx_ready"] | (self.uart_state["rx_ready"] << 1)) & 0xFFFFFFFF
        
        elif name == 'uart_read':
            if self.uart_state["rx_ready"] == 0:
                return 0
            self.uart_state["rx_ready"] = 0
            return self.uart_state["data"] & 0xFF
        
        elif name == 'uart_write':
            if len(args) != 1:
                raise RuntimeError(f"uart_write expects 1 argument, got {len(args)}")
            if self.uart_state["tx_ready"] == 0:
                raise RuntimeError("UART TX not ready")
            # Get byte value (lowest 8 bits)
            byte_value = args[0] & 0xFF
            # Output character to stdout
            try:
                sys.stdout.write(chr(byte_value))
                sys.stdout.flush()
            except (ValueError, OverflowError):
                # If byte_value is not a valid character, output as-is
                sys.stdout.buffer.write(bytes([byte_value]))
                sys.stdout.flush()
            self.uart_state["data"] = byte_value
            self.uart_state["tx_ready"] = 1
            return 0
        
        # Timer functions
        elif name == 'timer_set_mode':
            if len(args) != 1:
                raise RuntimeError(f"timer_set_mode expects 1 argument, got {len(args)}")
            self.timer_state["mode"] = args[0]
            return 0
        
        elif name == 'timer_set_period':
            if len(args) != 1:
                raise RuntimeError(f"timer_set_period expects 1 argument, got {len(args)}")
            self.timer_state["period"] = args[0]
            return 0
        
        elif name == 'timer_start':
            self.timer_state["running"] = 1
            self.timer_state["value"] = 0
            self.timer_state["expired"] = 0
            return 0
        
        elif name == 'timer_stop':
            self.timer_state["running"] = 0
            return 0
        
        elif name == 'timer_reset':
            self.timer_state["value"] = 0
            self.timer_state["expired"] = 0
            return 0
        
        elif name == 'timer_get_value':
            return self.timer_state["value"] & 0xFFFFFFFF
        
        elif name == 'timer_expired':
            # Simulate timer expiration for testing
            # In real hardware, this would be set by the timer interrupt
            if self.timer_state["running"] != 0 and self.timer_state["period"] > 0:
                # Simple simulation: expire after period microseconds (simplified)
                # For testing, we'll make it expire once per call if period > 0
                if self.timer_state["expired"] == 0:
                    self.timer_state["expired"] = 1
                    return 1
            return 0
        
        # Delay functions (simplified - just return 0, no actual delay in interpreter)
        elif name == 'delay_ms':
            return 0
        
        elif name == 'delay_us':
            return 0
        
        elif name == 'delay_cycles':
            return 0
        
        # Interrupt functions
        elif name == 'enable_interrupts':
            return 0
        
        elif name == 'disable_interrupts':
            return 0
        
        # Bit manipulation functions
        elif name == 'set_bit':
            if len(args) != 2:
                raise RuntimeError(f"set_bit expects 2 arguments, got {len(args)}")
            value, bit = args
            return (value | (1 << (bit & 0x1F))) & 0xFFFFFFFF
        
        elif name == 'clear_bit':
            if len(args) != 2:
                raise RuntimeError(f"clear_bit expects 2 arguments, got {len(args)}")
            value, bit = args
            return (value & ~(1 << (bit & 0x1F))) & 0xFFFFFFFF
        
        elif name == 'toggle_bit':
            if len(args) != 2:
                raise RuntimeError(f"toggle_bit expects 2 arguments, got {len(args)}")
            value, bit = args
            return (value ^ (1 << (bit & 0x1F))) & 0xFFFFFFFF
        
        elif name == 'get_bit':
            if len(args) != 2:
                raise RuntimeError(f"get_bit expects 2 arguments, got {len(args)}")
            value, bit = args
            return 1 if (value & (1 << (bit & 0x1F))) != 0 else 0
        
        else:
            raise RuntimeError(f"Unknown hardware function: {name}")


class ReturnException(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: int):
        self.value = value
        super().__init__()
