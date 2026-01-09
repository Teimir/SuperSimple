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

from typing import Dict, Optional, List, Any
from parser import (
    Program, FunctionDef, Statement, Expression,
    Literal, Identifier, BinaryOp, UnaryOp, FunctionCall,
    VarDecl, Assignment, Return, IfStmt, WhileStmt, ForStmt,
    Block, FunctionCallStmt, Increment, Decrement,
    ArrayDecl, ArrayAccess, PointerDecl, AddressOf, Dereference,
    ArrayAssignment, PointerAssignment
)


class RuntimeError(Exception):
    """Runtime error during program execution."""
    pass


class Environment:
    """Represents a scope/environment for variable bindings."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.vars: Dict[str, int] = {}  # Обычные переменные и указатели
        self.arrays: Dict[str, List[int]] = {}  # Массивы
        self.variable_addresses: Dict[str, int] = {}  # Адреса переменных (для &)
        self.array_addresses: Dict[str, int] = {}  # Адреса массивов (базовый адрес)
        self.next_address: int = 1000  # Начальный адрес для выделения памяти
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
        
        if decl.is_register:
            # Register variable - store in hardware register
            if decl.register_num is not None:
                self.registers[decl.register_num] = value & 0xFFFFFFFF
                self.register_map[decl.name] = decl.register_num
                # Also store in environment for lookup
                env.declare(decl.name, value)
        else:
            # Normal variable
            env.declare(decl.name, value)
    
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
        """Execute an assignment."""
        value = self.evaluate_expression(assignment.value, env)
        
        # Check if this is a register variable
        if assignment.name in self.register_map:
            reg_num = self.register_map[assignment.name]
            if reg_num == 31:
                raise RuntimeError("Cannot write to register r31 (instruction pointer)")
            self.registers[reg_num] = value & 0xFFFFFFFF
            # Also update in environment
            env.assign(assignment.name, value)
        else:
            env.assign(assignment.name, value)
    
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
                self.execute_statement(for_stmt.increment, for_env)
    
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
        if isinstance(expr, Literal):
            return expr.value & 0xFFFFFFFF
        
        elif isinstance(expr, Identifier):
            # Check if this is a register variable
            if expr.name in self.register_map:
                reg_num = self.register_map[expr.name]
                return self.registers[reg_num] & 0xFFFFFFFF
            return env.get(expr.name) & 0xFFFFFFFF
        
        elif isinstance(expr, ArrayAccess):
            return self.evaluate_array_access(expr, env)
        
        elif isinstance(expr, AddressOf):
            return self.evaluate_address_of(expr, env)
        
        elif isinstance(expr, Dereference):
            return self.evaluate_dereference(expr, env)
        
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
        
        result = op_map[op.op](left, right)
        return result & 0xFFFFFFFF
    
    def evaluate_unary_op(self, op: UnaryOp, env: Environment) -> int:
        """Evaluate a unary operation."""
        operand = self.evaluate_expression(op.operand, env)
        
        if op.op == '-':
            return (-operand) & 0xFFFFFFFF
        elif op.op == '!':
            return 0 if operand != 0 else 1
        elif op.op == '~':
            return (~operand) & 0xFFFFFFFF
        else:
            raise RuntimeError(f"Unknown unary operator: {op.op}")
    
    def evaluate_array_access(self, expr: ArrayAccess, env: Environment) -> int:
        """Evaluate array element access: arr[index]"""
        index = self.evaluate_expression(expr.index, env)
        return env.get_array_element(expr.name, index)
    
    def evaluate_address_of(self, expr: AddressOf, env: Environment) -> int:
        """Evaluate address-of operator: &x"""
        operand = expr.operand
        
        if isinstance(operand, Identifier):
            # &variable
            return env.get_address(operand.name)
        elif isinstance(operand, ArrayAccess):
            # &arr[i] - address of array element
            arr_name = operand.name
            index = self.evaluate_expression(operand.index, env)
            base_addr = env.get_address(arr_name)
            # Each element is 1 memory cell, so address = base + index
            return (base_addr + index) & 0xFFFFFFFF
        elif isinstance(operand, Dereference):
            # &*ptr - address that ptr points to (just the value of ptr)
            return self.evaluate_expression(operand.operand, env)
        else:
            raise RuntimeError(f"Cannot take address of {type(operand)}")
    
    def evaluate_dereference(self, expr: Dereference, env: Environment) -> int:
        """Evaluate pointer dereference: *ptr"""
        # Get the address (value of the pointer)
        address = self.evaluate_expression(expr.operand, env)
        # Get value at that address
        return env.get_value_at_address(address)
    
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
            self.uart_state["data"] = args[0] & 0xFF
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
