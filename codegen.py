"""
Code Generator for Simple C-Style Language
Generates FASM assembly code from AST.

This module converts an Abstract Syntax Tree (AST) into FASM assembly code
that can be compiled using the FASM assembler. It handles:
- Function definitions and calls
- Variable declarations and assignments
- Control flow (if, while, for)
- Arithmetic and logical operations
- Array and pointer operations
- Hardware function calls (UART, GPIO)
"""

import os
from typing import Dict, List, Optional, Set, Tuple
from parser import (
    Program, FunctionDef, Statement, Expression,
    Literal, Identifier, BinaryOp, UnaryOp, FunctionCall,
    VarDecl, Assignment, Return, IfStmt, WhileStmt, ForStmt,
    Block, FunctionCallStmt, Increment, Decrement,
    ArrayDecl, ArrayAccess, PointerDecl, AddressOf, Dereference,
    ArrayAssignment, PointerAssignment, BreakStmt, ContinueStmt
)


class LoopContext:
    """Context for a loop (while or for) to support break/continue."""
    def __init__(self, start_label: str, end_label: str, loop_type: str, increment_label: Optional[str] = None):
        self.start_label = start_label
        self.end_label = end_label
        self.loop_type = loop_type  # "while" or "for"
        self.increment_label = increment_label  # Only for for loops


class RegisterAllocator:
    """
    Simple register allocator using fixed register allocation.
    
    Register allocation strategy:
    - r0: Reserved for function return value
    - r1-r10: Temporary registers (for expression evaluation)
    - r11-r25: Local variables
    - r26-r30: Function parameters
    - r31: Instruction pointer (not allocatable)
    """
    
    def __init__(self):
        # r0-r30 are available for variables (r31 is instruction pointer)
        # We'll use r0-r10 for temporaries, r11-r25 for local variables, r26-r30 for parameters
        self.available_registers = list(range(0, 31))  # r0 to r30
        self.allocated: Dict[str, int] = {}  # variable name -> register number
        self.temp_counter = 0
        self.next_temp = 1  # Start with r1 for temporaries (r0 reserved for return value)
        
    def allocate(self, name: str) -> int:
        """Allocate a register for a variable."""
        if name in self.allocated:
            return self.allocated[name]
        
        # Use registers starting from r11 for variables
        reg_num = 11 + len(self.allocated)
        if reg_num > 30:
            raise RuntimeError(f"Code generation error: Too many variables (register allocation failed for '{name}' in function '{self.current_function}')")
        
        self.allocated[name] = reg_num
        return reg_num
    
    def get_register(self, name: str) -> Optional[int]:
        """Get register number for a variable, or None if not allocated."""
        if name in self.allocated:
            return self.allocated[name]
        return None
    
    def get_temp_register(self) -> int:
        """Get a temporary register."""
        # Use r1-r10 for temporaries (r0 is reserved for function return value)
        reg = self.next_temp
        self.next_temp = (self.next_temp + 1) % 10  # Cycle through r1-r10
        if reg == 0:
            reg = 1  # Skip r0, start from r1
        return reg
    
    def free_temp(self, reg: int):
        """Free a temporary register (does nothing in simple allocator)."""
        pass


class CodeGenerator:
    """Generates FASM assembly code from AST."""
    
    def __init__(self, program: Program):
        self.program = program
        self.reg_allocator = RegisterAllocator()
        self.label_counter = 0
        self.code: List[str] = []
        self.function_labels: Dict[str, str] = {}
        self.current_function: Optional[str] = None
        self._has_explicit_return = False  # Track if current function has explicit return
        
        # Loop context stack for break/continue support
        self.loop_stack: List[LoopContext] = []
        
        # Memory management
        self.array_addresses: Dict[str, str] = {}  # array name -> label name (all arrays in memory)
        self.array_sizes: Dict[str, int] = {}  # array name -> size
        self.variable_addresses: Dict[str, int] = {}  # var name -> address (stack offset or label)
        self.stack_offset: int = 0  # Current offset from base stack address (r30) - only for variables, not arrays
        self.data_section: List[str] = []  # Global data section
        self.global_data_labels: Dict[str, str] = {}  # Global variable/array name -> label
        
    def generate_label(self, prefix: str = "L") -> str:
        """Generate a unique label."""
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, instruction: str):
        """Emit an assembly instruction."""
        self.code.append(f"\t{instruction}")
    
    def emit_label(self, label: str):
        """Emit a label."""
        # In FASM with ISA.inc, labels need 'addr' prefix for addresses
        # But for code labels (for jumps), we can use labels directly
        self.code.append(f"{label}:")
    
    def emit_comment(self, comment: str):
        """Emit a comment."""
        self.code.append(f"\t; {comment}")
    
    def get_register_name(self, reg_num: int) -> str:
        """Convert register number to FASM format."""
        # FASM ISA.inc uses format r:0, r:1, etc. (with colon)
        return f"r:{reg_num}"
    
    def generate(self, output_file: str = None) -> str:
        """Generate complete assembly program."""
        self.code = []
        
        # Add commented format binary (as in calc.asm)
        # format binary is already in ISA.inc, so we comment it out
        self.code.append(";format binary")
        self.code.append("")
        
        # Include ISA.inc from int_pack directory (it contains "format binary")
        # Calculate path relative to output file location
        if output_file:
            # Get absolute paths
            output_abs = os.path.abspath(output_file)
            output_dir = os.path.dirname(output_abs)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            int_pack_isa = os.path.join(script_dir, "int_pack", "ISA.inc")
            
            # Try to find relative path from output directory to int_pack
            try:
                rel_path = os.path.relpath(int_pack_isa, output_dir)
                # Use forward slashes for FASM (works on Windows too)
                rel_path = rel_path.replace('\\', '/')
                self.code.append(f'include "{rel_path}"')
            except ValueError:
                # If relative path fails (different drives on Windows), use absolute path
                # Use forward slashes
                int_pack_isa_normalized = int_pack_isa.replace('\\', '/')
                self.code.append(f'include "{int_pack_isa_normalized}"')
        else:
            # Default: assume int_pack is relative to project root
            self.code.append('include "../int_pack/ISA.inc"')
        
        # Include macros.inc for entry macro (if main function exists)
        if output_file:
            output_abs = os.path.abspath(output_file)
            output_dir = os.path.dirname(output_abs)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            int_pack_macros = os.path.join(script_dir, "int_pack", "macros.inc")
            
            try:
                rel_path = os.path.relpath(int_pack_macros, output_dir)
                rel_path = rel_path.replace('\\', '/')
                # Only include if main function exists
                if any(f.name == 'main' for f in self.program.functions):
                    self.code.append(f'include "{rel_path}"')
            except ValueError:
                int_pack_macros_normalized = int_pack_macros.replace('\\', '/')
                if any(f.name == 'main' for f in self.program.functions):
                    self.code.append(f'include "{int_pack_macros_normalized}"')
        
        self.code.append("")
        
        # Generate function labels
        for func in self.program.functions:
            # Main function uses just "main:" label, others use "func_name:"
            if func.name == 'main':
                self.function_labels[func.name] = "main"
            else:
                self.function_labels[func.name] = f"func_{func.name}"
        
        # Generate global variables and arrays first
        for global_var in self.program.global_vars:
            if isinstance(global_var, ArrayDecl):
                self.generate_array_decl(global_var)
            elif isinstance(global_var, PointerDecl):
                self.generate_pointer_decl(global_var)
            elif isinstance(global_var, VarDecl):
                self.generate_var_decl(global_var)
        
        # Generate main function first (entry point)
        main_func = None
        other_funcs = []
        for func in self.program.functions:
            if func.name == 'main':
                main_func = func
            else:
                other_funcs.append(func)
        
        # Generate entry point for main (using entry macro from macros.inc)
        if main_func:
            self.code.append("entry main")
            self.code.append("")
        
        # Generate main first (entry point)
        if main_func:
            self.generate_function(main_func)
        
        # Generate other functions
        for func in other_funcs:
            self.generate_function(func)
        
        # Generate data section for global arrays and variables
        if self.data_section:
            self.code.append("")
            self.code.append("; Data section")
            self.code.extend(self.data_section)
        
        return "\n".join(self.code)
    
    def generate_function(self, func: FunctionDef) -> None:
        """Generate assembly code for a function."""
        old_func = self.current_function
        self.current_function = func.name
        old_allocator = self.reg_allocator
        self.reg_allocator = RegisterAllocator()
        
        # Save and reset stack offset for this function
        old_stack_offset = self.stack_offset
        self.stack_offset = 0
        
        # Function label
        self.code.append("")
        self.emit_label(self.function_labels[func.name])
        self.emit_comment(f"Function: {func.name}")
        
        # Function entry: return address and parameters are on stack (pushed by caller)
        # r:30 is the stack pointer (initialized to 4096 by entry macro)
        # Stack layout: [return_addr][param0][param1]...[paramN] (r:30 points to return_addr)
        # We need to account for return address + parameters in stack offset tracking
        if func.name != 'main':
            self.stack_offset += 1  # Account for return address on stack
            self.stack_offset += len(func.params)  # Account for parameters on stack
        
        # Load parameters from stack
        # Parameters are on stack in order: first parameter on top (after return address)
        # Stack layout: [return_addr][param0][param1]...[paramN] (r:30 points to return_addr)
        # We need to pop return address first, then load parameters
        param_regs = []
        temp_reg = self.reg_allocator.get_temp_register()
        
        # First, pop return address (it's already accounted for in stack_offset)
        # Parameters start at [r:30+1], [r:30+2], etc.
        for i, param in enumerate(func.params):
            # Allocate a register for the parameter
            param_reg = self.reg_allocator.allocate(param)
            param_regs.append(param_reg)
            
            # Load parameter from stack: [r:30 + 1 + i]
            # We need to calculate address: r:30 + 1 + i
            addr_reg = self.reg_allocator.get_temp_register()
            offset = 1 + i  # +1 for return address, +i for parameter index
            self.emit(f"mov {self.get_register_name(addr_reg)}, r:30")
            if offset > 0:
                offset_reg = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(offset_reg)}, {offset}")
                self.emit(f"add {self.get_register_name(addr_reg)}, {self.get_register_name(addr_reg)}, {self.get_register_name(offset_reg)}")
                self.reg_allocator.free_temp(offset_reg)
            self.emit(f"lds {self.get_register_name(param_reg)}, [{self.get_register_name(addr_reg)}]")
            self.reg_allocator.free_temp(addr_reg)
            # #region agent log
            import json
            with open(r'e:\aiproj\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"codegen.py:280","message":"Parameter loaded from stack","data":{"func":func.name,"param":param,"param_reg":param_reg,"stack_offset":offset},"timestamp":0,"sessionId":"debug-session","hypothesisId":"H3"}) + '\n')
            # #endregion
        
        self.reg_allocator.free_temp(temp_reg)
        
        # Track if function has explicit return
        # We'll set this flag when we encounter a return statement
        self._has_explicit_return = False
        
        # Generate function body
        self.generate_statement(func.body)
        
        # Function return (if no explicit return, return 0)
        # Return value should be in r:0 by convention
        # Note: If function has explicit return, it already generated the return code
        # so we don't need to generate it again here
        if not self._has_explicit_return:
            self.emit_comment("Implicit return 0")
            self.emit("mov r:0, 0")
            
            # Return from function
            if func.name == 'main':
                # Main function ends the program
                self.emit("hlt")
            else:
                # Restore return address from stack and return
                # r:30 currently points to where we saved the return address
                # Read return address into r:29 (NOT r:0, which contains return value!)
                self.emit(f"lds r:29, [r:30]")  # Read return address into r:29
                self.emit(f"add r:30, r:30, 1")  # Restore stack pointer (pop return address)
                # Return to caller by jumping to return address
                self.emit(f"mov r:31, r:29")
        
        # Reset flag
        self._has_explicit_return = False

        self.current_function = old_func
        self.reg_allocator = old_allocator
        self.stack_offset = old_stack_offset
    
    def generate_statement(self, stmt: Statement) -> None:
        """Generate assembly code for a statement."""
        if isinstance(stmt, VarDecl):
            self.generate_var_decl(stmt)
        elif isinstance(stmt, ArrayDecl):
            self.generate_array_decl(stmt)
        elif isinstance(stmt, PointerDecl):
            self.generate_pointer_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, ArrayAssignment):
            self.generate_array_assignment(stmt)
        elif isinstance(stmt, PointerAssignment):
            self.generate_pointer_assignment(stmt)
        elif isinstance(stmt, Return):
            self.generate_return(stmt)
        elif isinstance(stmt, IfStmt):
            self.generate_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self.generate_while(stmt)
        elif isinstance(stmt, ForStmt):
            self.generate_for(stmt)
        elif isinstance(stmt, Block):
            self.generate_block(stmt)
        elif isinstance(stmt, FunctionCallStmt):
            # FunctionCallStmt wraps a FunctionCall - just ignore return value
            # Check if it's a hardware function - if so, generate without result register
            if stmt.call.name not in self.function_labels:
                # Hardware function - generate code without allocating result register
                args = [self.generate_expression(arg) for arg in stmt.call.args]
                if stmt.call.name == 'uart_write':
                    if len(args) != 1:
                        raise RuntimeError(f"Code generation error: uart_write expects 1 argument, got {len(args)}")
                    data_reg = args[0]
                    self.emit(f"outu {self.get_register_name(data_reg)}")
                    self.reg_allocator.free_temp(data_reg)
                else:
                    # For other hardware functions, still need result register (but ignore it)
                    result_reg = self.generate_function_call(stmt.call)
                    if result_reg != 0:
                        self.reg_allocator.free_temp(result_reg)
            else:
                # Regular function call - generate normally but ignore result
                result_reg = self.generate_function_call(stmt.call)
                if result_reg != 0:
                    self.reg_allocator.free_temp(result_reg)
        elif isinstance(stmt, Increment):
            self.generate_increment(stmt)
        elif isinstance(stmt, Decrement):
            self.generate_decrement(stmt)
        elif isinstance(stmt, BreakStmt):
            self.generate_break(stmt)
        elif isinstance(stmt, ContinueStmt):
            self.generate_continue(stmt)
        else:
            raise RuntimeError(f"Code generation error: Unknown statement type '{type(stmt).__name__}' in function '{self.current_function}'")
    
    def generate_var_decl(self, decl: VarDecl) -> None:
        """Generate code for variable declaration."""
        # Check if this is a global variable
        is_global = (self.current_function is None)
        
        if decl.is_register:
            # Register variable - just allocate it
            reg_num = int(decl.name[1:])  # Extract number from "r0", "r1", etc.
            if reg_num < 0 or reg_num > 30:
                raise RuntimeError(f"Code generation error: Invalid register name '{decl.name}' (must be r0-r31)")
            self.reg_allocator.allocated[decl.name] = reg_num
            # Initialize if needed
            if decl.initializer:
                value_reg = self.generate_expression(decl.initializer)
                if value_reg != reg_num:
                    self.emit(f"mov {self.get_register_name(reg_num)}, {self.get_register_name(value_reg)}")
                    self.reg_allocator.free_temp(value_reg)
            return
        
        if is_global:
            # Global variable - allocate in data section
            label = f"var_{decl.name}"
            self.global_data_labels[decl.name] = label
            self.data_section.append(f"{label}:")
            if decl.initializer:
                if isinstance(decl.initializer, Literal):
                    self.data_section.append(f"\tdd {decl.initializer.value}")
                else:
                    # For non-constant initializers, we'd need runtime initialization
                    # For now, just initialize to 0
                    self.data_section.append(f"\tdd 0")
            else:
                self.data_section.append(f"\tdd 0")
            self.variable_addresses[decl.name] = label
        else:
            # Local variable - allocate register
            reg_num = self.reg_allocator.allocate(decl.name)
            
            # Track address (stack offset)
            self.variable_addresses[decl.name] = self.stack_offset
            self.stack_offset += 1
            
            # Initialize if needed
            if decl.initializer:
                value_reg = self.generate_expression(decl.initializer)
                if value_reg != reg_num:
                    self.emit(f"mov {self.get_register_name(reg_num)}, {self.get_register_name(value_reg)}")
                    self.reg_allocator.free_temp(value_reg)
            else:
                # Initialize to 0
                self.emit(f"mov {self.get_register_name(reg_num)}, 0")
    
    def generate_assignment(self, assign: Assignment) -> None:
        """Generate code for assignment."""
        # Evaluate expression
        value_reg = self.generate_expression(assign.value)
        
        # Check if this is a global variable
        if assign.name in self.global_data_labels:
            # Global variable - store to memory
            label = self.global_data_labels[assign.name]
            # Allocate address register, making sure it's different from value_reg
            addr_reg = self.reg_allocator.get_temp_register()
            while addr_reg == value_reg:
                self.reg_allocator.free_temp(addr_reg)
                addr_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(addr_reg)}, {label} addr")
            self.emit(f"lds [{self.get_register_name(addr_reg)}], {self.get_register_name(value_reg)}")
            self.reg_allocator.free_temp(addr_reg)
            self.reg_allocator.free_temp(value_reg)
        else:
            # Local variable - store in register
            target_reg = self.reg_allocator.get_register(assign.name)
            if target_reg is None:
                if assign.name.startswith('r') and assign.name[1:].isdigit():
                    # Direct register access
                    target_reg = int(assign.name[1:])
                else:
                    # Allocate new register
                    target_reg = self.reg_allocator.allocate(assign.name)
            
            # Move value to target
            if value_reg != target_reg:
                self.emit(f"mov {self.get_register_name(target_reg)}, {self.get_register_name(value_reg)}")
            
            self.reg_allocator.free_temp(value_reg)
    
    def generate_expression(self, expr: Expression) -> int:
        """Generate code for expression and return register containing result."""
        if isinstance(expr, Literal):
            return self.generate_literal(expr)
        elif isinstance(expr, Identifier):
            return self.generate_identifier(expr)
        elif isinstance(expr, ArrayAccess):
            return self.generate_array_access(expr)
        elif isinstance(expr, AddressOf):
            return self.generate_address_of(expr)
        elif isinstance(expr, Dereference):
            return self.generate_dereference(expr)
        elif isinstance(expr, BinaryOp):
            return self.generate_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            return self.generate_unary_op(expr)
        elif isinstance(expr, FunctionCall):
            return self.generate_function_call(expr)
        else:
            raise RuntimeError(f"Code generation error: Unknown expression type '{type(expr).__name__}' in function '{self.current_function}'")
    
    def generate_literal(self, lit: Literal) -> int:
        """Generate code for literal and return register with value.
        
        Args:
            lit: Literal expression node containing the value
            
        Returns:
            Register number containing the literal value
        """
        temp_reg = self.reg_allocator.get_temp_register()
        # For now, use mov with immediate (if ISA supports it)
        # Otherwise, we'd need to load from memory
        # Assuming ISA supports: mov r0, 42 (immediate in op2)
        value = lit.value & 0xFFFFFFFF
        self.emit(f"mov {self.get_register_name(temp_reg)}, {value}")
        return temp_reg
    
    def generate_identifier(self, ident: Identifier) -> int:
        """Generate code for identifier access."""
        # Check if this is a global variable
        if ident.name in self.global_data_labels:
            # Global variable - load from memory
            label = self.global_data_labels[ident.name]
            result_reg = self.reg_allocator.get_temp_register()
            addr_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(addr_reg)}, {label} addr")
            self.emit(f"lds {self.get_register_name(result_reg)}, [{self.get_register_name(addr_reg)}]")
            self.reg_allocator.free_temp(addr_reg)
            return result_reg
        
        # Local variable - get from register
        reg = self.reg_allocator.get_register(ident.name)
        if reg is None:
            if ident.name.startswith('r') and ident.name[1:].isdigit():
                reg = int(ident.name[1:])
            else:
                raise RuntimeError(f"Code generation error: Undefined variable '{ident.name}' in function '{self.current_function}'")
        
        # If it's already in a register, return it
        return reg
    
    def generate_binary_op(self, op: BinaryOp) -> int:
        """Generate code for binary operation.
        
        Args:
            op: BinaryOp expression node with operator and left/right operands
            
        Returns:
            Register number containing the result of the operation
            
        Supported operators: +, -, *, /, %, &, |, ^, <<, >>, ==, !=, <, <=, >, >=, &&, ||
        """
        left_reg = self.generate_expression(op.left)
        right_reg = self.generate_expression(op.right)
        result_reg = self.reg_allocator.get_temp_register()
        
        op_map = {
            '+': 'add',
            '-': 'sub',
            '&': 'and',
            '|': 'or',
            '^': 'xor',
            '<<': 'shl',
            '>>': 'shr',
        }
        
        if op.op in op_map:
            # Three-operand instruction: result = left op right
            self.emit(f"{op_map[op.op]} {self.get_register_name(result_reg)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
        elif op.op == '*':
            # Multiplication: use repeated addition
            # Copy operands to temporary registers to avoid modifying originals
            left_temp = self.reg_allocator.get_temp_register()
            right_temp = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(left_temp)}, {self.get_register_name(left_reg)}")
            self.emit(f"mov {self.get_register_name(right_temp)}, {self.get_register_name(right_reg)}")
            
            # result = 0
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
            loop_label = self.generate_label("mul_loop")
            end_label = self.generate_label("mul_end")
            
            self.emit_label(loop_label)
            # Check if right_temp == 0, if so exit
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            self.emit(f"cmovz r:31, {self.get_register_name(right_temp)}, {end_label} addr")
            
            # Add left_temp to result
            self.emit(f"add {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(left_temp)}")
            # Decrement right_temp
            one_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(one_reg)}, 1")
            self.emit(f"sub {self.get_register_name(right_temp)}, {self.get_register_name(right_temp)}, {self.get_register_name(one_reg)}")
            
            # Jump back to loop
            self.emit(f"mov r:31, {loop_label} addr")
            self.emit_label(end_label)
            
            self.reg_allocator.free_temp(left_temp)
            self.reg_allocator.free_temp(right_temp)
            self.reg_allocator.free_temp(zero_reg)
            self.reg_allocator.free_temp(one_reg)
        elif op.op == '/':
            # Division: use repeated subtraction
            # Copy operands to temporary registers to avoid modifying originals
            left_temp = self.reg_allocator.get_temp_register()
            right_temp = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(left_temp)}, {self.get_register_name(left_reg)}")
            self.emit(f"mov {self.get_register_name(right_temp)}, {self.get_register_name(right_reg)}")
            
            # result = 0
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
            loop_label = self.generate_label("div_loop")
            end_label = self.generate_label("div_end")
            
            # Check for division by zero
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            error_label = self.generate_label("div_error")
            self.emit(f"cmovz r:31, {self.get_register_name(right_temp)}, {error_label} addr")
            
            self.emit_label(loop_label)
            # Check if left_temp < right_temp, if so exit
            # cmpb returns -1 if left < right, 0 if left >= right
            temp_cmp = self.reg_allocator.get_temp_register()
            self.emit(f"cmpb {self.get_register_name(temp_cmp)}, {self.get_register_name(left_temp)}, {self.get_register_name(right_temp)}")
            # If temp_cmp != 0 (i.e., == -1, meaning left < right), jump to end
            zero_reg2 = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg2)}, 0")
            self.emit(f"cmovnz r:31, {self.get_register_name(temp_cmp)}, {end_label} addr")
            
            # Subtract right_temp from left_temp
            self.emit(f"sub {self.get_register_name(left_temp)}, {self.get_register_name(left_temp)}, {self.get_register_name(right_temp)}")
            # Increment result
            one_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(one_reg)}, 1")
            self.emit(f"add {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(one_reg)}")
            
            # Jump back to loop
            self.emit(f"mov r:31, {loop_label} addr")
            self.emit_label(end_label)
            
            # Jump over error label to avoid executing it
            skip_error_label = self.generate_label("div_skip_error")
            self.emit(f"mov r:31, {skip_error_label} addr")
            
            # Error label (division by zero)
            self.emit_label(error_label)
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
            
            self.emit_label(skip_error_label)
            
            self.reg_allocator.free_temp(zero_reg2)
            
            self.reg_allocator.free_temp(left_temp)
            self.reg_allocator.free_temp(right_temp)
            self.reg_allocator.free_temp(zero_reg)
            self.reg_allocator.free_temp(temp_cmp)
            self.reg_allocator.free_temp(one_reg)
            self.reg_allocator.free_temp(zero_reg2)
        elif op.op == '%':
            # Modulo: use repeated subtraction, return remainder
            # Copy operands to temporary registers to avoid modifying originals
            remainder_reg = self.reg_allocator.get_temp_register()
            right_temp = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(remainder_reg)}, {self.get_register_name(left_reg)}")
            self.emit(f"mov {self.get_register_name(right_temp)}, {self.get_register_name(right_reg)}")
            
            loop_label = self.generate_label("mod_loop")
            end_label = self.generate_label("mod_end")
            
            # Check for modulo by zero
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            error_label = self.generate_label("mod_error")
            self.emit(f"cmovz r:31, {self.get_register_name(right_temp)}, {error_label} addr")
            
            self.emit_label(loop_label)
            # Check if remainder_reg < right_temp, if so exit
            # cmpb returns -1 if remainder < right, 0 if remainder >= right
            temp_cmp = self.reg_allocator.get_temp_register()
            self.emit(f"cmpb {self.get_register_name(temp_cmp)}, {self.get_register_name(remainder_reg)}, {self.get_register_name(right_temp)}")
            # If temp_cmp != 0 (i.e., == -1, meaning remainder < right), jump to end
            zero_reg2 = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg2)}, 0")
            self.emit(f"cmovnz r:31, {self.get_register_name(temp_cmp)}, {end_label} addr")
            
            # Subtract right_temp from remainder_reg
            self.emit(f"sub {self.get_register_name(remainder_reg)}, {self.get_register_name(remainder_reg)}, {self.get_register_name(right_temp)}")
            
            # Jump back to loop
            self.emit(f"mov r:31, {loop_label} addr")
            self.emit_label(end_label)
            
            # Move remainder to result
            self.emit(f"mov {self.get_register_name(result_reg)}, {self.get_register_name(remainder_reg)}")
            
            # Jump over error label to avoid executing it
            skip_error_label = self.generate_label("mod_skip_error")
            self.emit(f"mov r:31, {skip_error_label} addr")
            
            # Error label (modulo by zero)
            self.emit_label(error_label)
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
            
            self.emit_label(skip_error_label)
            
            self.reg_allocator.free_temp(zero_reg2)
            
            self.reg_allocator.free_temp(remainder_reg)
            self.reg_allocator.free_temp(right_temp)
            self.reg_allocator.free_temp(zero_reg)
            self.reg_allocator.free_temp(temp_cmp)
            self.reg_allocator.free_temp(zero_reg2)
        elif op.op == '==':
            # Equality comparison: use cmpe
            # Check if result_reg conflicts with left_reg or right_reg
            if result_reg == left_reg or result_reg == right_reg:
                temp_cmp = self.reg_allocator.get_temp_register()
                self.emit(f"cmpe {self.get_register_name(temp_cmp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # Convert -1 (equal) to 1, 0 (not equal) to 0
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(temp_cmp)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
                self.reg_allocator.free_temp(temp_cmp)
            else:
                self.emit(f"cmpe {self.get_register_name(result_reg)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # Convert -1 (equal) to 1, 0 (not equal) to 0
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
        elif op.op == '!=':
            # Not equal: use cmpe and invert
            # Check if result_reg conflicts with left_reg or right_reg
            if result_reg == left_reg or result_reg == right_reg:
                temp_cmp = self.reg_allocator.get_temp_register()
                self.emit(f"cmpe {self.get_register_name(temp_cmp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # Convert 0 (equal) to 0, -1 (not equal) to 1
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovnz {self.get_register_name(result_reg)}, {self.get_register_name(temp_cmp)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
                self.reg_allocator.free_temp(temp_cmp)
            else:
                self.emit(f"cmpe {self.get_register_name(result_reg)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # Convert 0 (equal) to 0, -1 (not equal) to 1
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovnz {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
        elif op.op == '<':
            # Less than: use cmpb
            # Check if result_reg conflicts with left_reg or right_reg
            if result_reg == left_reg or result_reg == right_reg:
                temp_cmp = self.reg_allocator.get_temp_register()
                self.emit(f"cmpb {self.get_register_name(temp_cmp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # Convert -1 (less) to 1, 0 (not less) to 0
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(temp_cmp)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
                self.reg_allocator.free_temp(temp_cmp)
            else:
                self.emit(f"cmpb {self.get_register_name(result_reg)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # Convert -1 (less) to 1, 0 (not less) to 0
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
        elif op.op == '>':
            # Greater than: use cmpa
            # Check if result_reg conflicts with left_reg or right_reg
            if result_reg == left_reg or result_reg == right_reg:
                temp_cmp = self.reg_allocator.get_temp_register()
                self.emit(f"cmpa {self.get_register_name(temp_cmp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(temp_cmp)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
                self.reg_allocator.free_temp(temp_cmp)
            else:
                self.emit(f"cmpa {self.get_register_name(result_reg)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                temp = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(temp)}, -1")
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
                self.reg_allocator.free_temp(temp)
        elif op.op == '<=':
            # Less than or equal: (a <= b) means !(a > b)
            # Use cmpa to check if a > b, then invert
            temp = self.reg_allocator.get_temp_register()
            self.emit(f"cmpa {self.get_register_name(temp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
            # temp is -1 if a > b, 0 if a <= b
            # We want result_reg = 1 if a <= b, 0 if a > b
            # So: result_reg = 1 if temp == 0, else 0
            one_reg = self.reg_allocator.get_temp_register()
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(one_reg)}, 1")
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            # If temp == 0 (a <= b), set result_reg = 1, else 0
            self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(temp)}, {self.get_register_name(one_reg)}")
            self.emit(f"cmovnz {self.get_register_name(result_reg)}, {self.get_register_name(temp)}, {self.get_register_name(zero_reg)}")
            self.reg_allocator.free_temp(temp)
            self.reg_allocator.free_temp(one_reg)
            self.reg_allocator.free_temp(zero_reg)
        elif op.op == '>=':
            # Greater than or equal: (a >= b) == (a > b) || (a == b)
            # Use cmpa to check if a > b: if true, result = 1; if false, check if a == b
            # Check if result_reg conflicts with left_reg or right_reg
            if result_reg == left_reg or result_reg == right_reg:
                temp_cmp = self.reg_allocator.get_temp_register()
                while temp_cmp == left_reg or temp_cmp == right_reg:
                    self.reg_allocator.free_temp(temp_cmp)
                    temp_cmp = self.reg_allocator.get_temp_register()
                # For a >= b: use cmpb to check a < b, then invert
                # cmpb returns -1 if a < b, 0 if a >= b
                self.emit(f"cmpb {self.get_register_name(temp_cmp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # temp_cmp is -1 if a < b, 0 if a >= b
                # We want result_reg = 1 if a >= b, 0 if a < b
                # So: result_reg = 1 if temp_cmp == 0, else 0
                one_reg = self.reg_allocator.get_temp_register()
                while one_reg == left_reg or one_reg == right_reg or one_reg == result_reg or one_reg == temp_cmp:
                    self.reg_allocator.free_temp(one_reg)
                    one_reg = self.reg_allocator.get_temp_register()
                # Initialize result_reg to 0 first, then set to 1 if condition is true
                self.emit(f"mov {self.get_register_name(result_reg)}, 0")
                self.emit(f"mov {self.get_register_name(one_reg)}, 1")
                # If temp_cmp == 0 (a >= b), set result_reg = 1
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(temp_cmp)}, {self.get_register_name(one_reg)}")
                self.reg_allocator.free_temp(temp_cmp)
                self.reg_allocator.free_temp(one_reg)
            else:
                # For a >= b: use cmpb to check a < b, then invert
                # cmpb returns -1 if a < b, 0 if a >= b
                temp = self.reg_allocator.get_temp_register()
                while temp == left_reg or temp == right_reg:
                    self.reg_allocator.free_temp(temp)
                    temp = self.reg_allocator.get_temp_register()
                self.emit(f"cmpb {self.get_register_name(temp)}, {self.get_register_name(left_reg)}, {self.get_register_name(right_reg)}")
                # temp is -1 if a < b, 0 if a >= b
                # We want result_reg = 1 if a >= b, 0 if a < b
                # So: result_reg = 1 if temp == 0, else 0
                one_reg = self.reg_allocator.get_temp_register()
                while one_reg == left_reg or one_reg == right_reg or one_reg == result_reg or one_reg == temp:
                    self.reg_allocator.free_temp(one_reg)
                    one_reg = self.reg_allocator.get_temp_register()
                # Initialize result_reg to 0 first, then set to 1 if condition is true
                self.emit(f"mov {self.get_register_name(result_reg)}, 0")
                self.emit(f"mov {self.get_register_name(one_reg)}, 1")
                # If temp == 0 (a >= b), set result_reg = 1
                self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(temp)}, {self.get_register_name(one_reg)}")
                self.reg_allocator.free_temp(temp)
                self.reg_allocator.free_temp(one_reg)
        elif op.op == '&&':
            # Logical AND: both non-zero
            # result = 1 if (left != 0) && (right != 0), else 0
            # Simple approach: if left == 0, result = 0; else if right == 0, result = 0; else result = 1
            zero_reg = self.reg_allocator.get_temp_register()
            while zero_reg == left_reg or zero_reg == right_reg or zero_reg == result_reg:
                self.reg_allocator.free_temp(zero_reg)
                zero_reg = self.reg_allocator.get_temp_register()
            
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
            
            # Check if left == 0, if so jump to end (result = 0)
            end_label = self.generate_label("and_end")
            temp_cmp = self.reg_allocator.get_temp_register()
            while temp_cmp == left_reg or temp_cmp == right_reg or temp_cmp == result_reg or temp_cmp == zero_reg:
                self.reg_allocator.free_temp(temp_cmp)
                temp_cmp = self.reg_allocator.get_temp_register()
            self.emit(f"cmpe {self.get_register_name(temp_cmp)}, {self.get_register_name(left_reg)}, {self.get_register_name(zero_reg)}")
            # temp_cmp is -1 if left == 0, 0 if left != 0
            # If left == 0 (temp_cmp == -1), jump to end using cmovnz (checks for -1)
            self.emit(f"cmovnz r:31, {self.get_register_name(temp_cmp)}, {end_label} addr")
            
            # Check if right == 0, if so jump to end (result = 0)
            temp_cmp2 = self.reg_allocator.get_temp_register()
            while temp_cmp2 == left_reg or temp_cmp2 == right_reg or temp_cmp2 == result_reg or temp_cmp2 == zero_reg or temp_cmp2 == temp_cmp:
                self.reg_allocator.free_temp(temp_cmp2)
                temp_cmp2 = self.reg_allocator.get_temp_register()
            self.emit(f"cmpe {self.get_register_name(temp_cmp2)}, {self.get_register_name(right_reg)}, {self.get_register_name(zero_reg)}")
            # If right == 0 (temp_cmp2 == -1), jump to end using cmovnz (checks for -1)
            self.emit(f"cmovnz r:31, {self.get_register_name(temp_cmp2)}, {end_label} addr")
            
            # Both are non-zero, set result to 1
            one_reg = self.reg_allocator.get_temp_register()
            while one_reg == left_reg or one_reg == right_reg or one_reg == result_reg or one_reg == zero_reg or one_reg == temp_cmp or one_reg == temp_cmp2:
                self.reg_allocator.free_temp(one_reg)
                one_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(one_reg)}, 1")
            self.emit(f"mov {self.get_register_name(result_reg)}, 1")
            # Jump to end to avoid falling through
            self.emit(f"mov r:31, {end_label} addr")
            
            self.emit_label(end_label)
            
            self.reg_allocator.free_temp(zero_reg)
            self.reg_allocator.free_temp(one_reg)
            self.reg_allocator.free_temp(temp_cmp)
            self.reg_allocator.free_temp(temp_cmp2)
        elif op.op == '||':
            # Logical OR: either non-zero
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            self.emit(f"cmpe {self.get_register_name(result_reg)}, {self.get_register_name(left_reg)}, {self.get_register_name(zero_reg)}")
            temp = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(temp)}, 1")
            self.emit(f"cmovnz {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
            self.emit(f"cmpe {self.get_register_name(temp)}, {self.get_register_name(right_reg)}, {self.get_register_name(zero_reg)}")
            self.emit(f"cmovnz {self.get_register_name(result_reg)}, {self.get_register_name(temp)}, {self.get_register_name(result_reg)}")
            self.reg_allocator.free_temp(temp)
            self.reg_allocator.free_temp(zero_reg)
        else:
            raise RuntimeError(f"Code generation error: Unknown binary operator '{op.op}' in function '{self.current_function}'")
        
        self.reg_allocator.free_temp(left_reg)
        self.reg_allocator.free_temp(right_reg)
        return result_reg
    
    def generate_unary_op(self, op: UnaryOp) -> int:
        """Generate code for unary operation.
        
        Args:
            op: UnaryOp expression node with operator and operand
            
        Returns:
            Register number containing the result of the operation
            
        Supported operators: !, ~, - (unary minus)
        """
        operand_reg = self.generate_expression(op.operand)
        result_reg = self.reg_allocator.get_temp_register()
        
        if op.op == '!':
            # Logical NOT: convert 0 to 1, non-zero to 0
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            self.emit(f"cmpe {self.get_register_name(result_reg)}, {self.get_register_name(operand_reg)}, {self.get_register_name(zero_reg)}")
            # result_reg is -1 if equal (operand was 0), 0 if not equal
            # Convert -1 to 1, 0 to 0
            temp = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(temp)}, -1")
            self.emit(f"cmovz {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
            self.emit(f"xor {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(temp)}")
            self.reg_allocator.free_temp(temp)
            self.reg_allocator.free_temp(zero_reg)
        elif op.op == '~':
            # Bitwise NOT
            self.emit(f"not {self.get_register_name(result_reg)}, {self.get_register_name(operand_reg)}")
        elif op.op == '-':
            # Unary minus: 0 - operand
            zero_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
            self.emit(f"sub {self.get_register_name(result_reg)}, {self.get_register_name(zero_reg)}, {self.get_register_name(operand_reg)}")
            self.reg_allocator.free_temp(zero_reg)
        else:
            raise RuntimeError(f"Code generation error: Unknown unary operator '{op.op}' in function '{self.current_function}'")
        
        self.reg_allocator.free_temp(operand_reg)
        return result_reg
    
    def generate_function_call(self, call: FunctionCall) -> int:
        """Generate code for function call.
        
        Args:
            call: FunctionCall expression node with function name and arguments
            
        Returns:
            Register number containing the return value (r:0 after function call)
            
        Note:
            Parameters are passed in registers r26-r30 (max 5 parameters).
            Return value is expected in r:0.
            Return address is pushed onto stack (r:30 is stack pointer).
        """
        # Check if it's a built-in hardware function
        if call.name not in self.function_labels:
            return self.generate_hardware_function(call)
        
        # Pass parameters through stack (in reverse order: last parameter first)
        # This way first parameter will be on top of stack
        temp_reg = self.reg_allocator.get_temp_register()
        for i in range(len(call.args) - 1, -1, -1):  # Reverse order
            arg = call.args[i]
            arg_reg = self.generate_expression(arg)
            # Push parameter onto stack
            if arg_reg != temp_reg:
                self.emit(f"mov {self.get_register_name(temp_reg)}, {self.get_register_name(arg_reg)}")
            self.emit(f"sub r:30, r:30, 1")  # Decrement stack pointer
            self.emit(f"lds [r:30], {self.get_register_name(temp_reg)}")  # Push parameter onto stack
            self.reg_allocator.free_temp(arg_reg)
            # #region agent log
            import json
            with open(r'e:\aiproj\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"codegen.py:975","message":"Parameter pushed to stack","data":{"param_index":i,"arg_reg":arg_reg,"arg_value":str(arg)},"timestamp":0,"sessionId":"debug-session","hypothesisId":"H2"}) + '\n')
            # #endregion
        
        # Generate return address label
        return_addr_label = self.generate_label("ret_addr")
        
        # Push return address onto stack: decrement r:30 (stack pointer), then store return address
        # r:30 is the stack pointer (initialized to 4096 by entry macro)
        self.emit(f"mov {self.get_register_name(temp_reg)}, {return_addr_label} addr")  # Get return address
        self.emit(f"sub r:30, r:30, 1")  # Decrement stack pointer
        self.emit(f"lds [r:30], {self.get_register_name(temp_reg)}")  # Push return address onto stack
        self.reg_allocator.free_temp(temp_reg)
        
        # Jump to function by setting r:31 (instruction pointer) to function label
        func_label = self.function_labels[call.name]
        self.emit(f"mov r:31, {func_label} addr")
        
        # Return address label - execution continues here after function returns
        self.emit_label(return_addr_label)
        
        # Clean up parameters from stack (they were pushed before return address)
        # Stack layout: [param0][param1]...[paramN][return_addr] (r:30 points to return_addr after return)
        # We need to pop parameters: add r:30, r:30, num_params
        if len(call.args) > 0:
            cleanup_reg = self.reg_allocator.get_temp_register()
            self.emit(f"mov {self.get_register_name(cleanup_reg)}, {len(call.args)}")
            self.emit(f"add r:30, r:30, {self.get_register_name(cleanup_reg)}")  # Pop parameters from stack
            self.reg_allocator.free_temp(cleanup_reg)
        
        # After function call, return value should be in r:0
        # Get return value
        result_reg = self.reg_allocator.get_temp_register()
        if result_reg != 0:
            self.emit(f"mov {self.get_register_name(result_reg)}, r:0")
        
        return result_reg
    
    def generate_hardware_function(self, call: FunctionCall) -> int:
        """Generate code for hardware function calls.
        
        Args:
            call: FunctionCall expression node with hardware function name and arguments
            
        Returns:
            Register number containing the result (if any)
            
        Supported hardware functions:
            - GPIO: gpio_set, gpio_read, gpio_write
            - UART: uart_set_baud, uart_read, uart_write
            - Timer: timer_set_mode, timer_start, timer_stop, etc.
        """
        result_reg = self.reg_allocator.get_temp_register()
        
        if call.name == 'gpio_set':
            if len(call.args) != 3:
                raise RuntimeError(f"gpio_set expects 3 arguments, got {len(call.args)}")
            pin_reg = self.generate_expression(call.args[0])
            dir_reg = self.generate_expression(call.args[1])
            mode_reg = self.generate_expression(call.args[2])
            # Pack into one value: (pin << 16) | (dir << 8) | mode
            temp = self.reg_allocator.get_temp_register()
            self.emit(f"shl {self.get_register_name(temp)}, {self.get_register_name(pin_reg)}, 16")
            temp2 = self.reg_allocator.get_temp_register()
            self.emit(f"shl {self.get_register_name(temp2)}, {self.get_register_name(dir_reg)}, 8")
            self.emit(f"or {self.get_register_name(temp)}, {self.get_register_name(temp)}, {self.get_register_name(temp2)}")
            self.emit(f"or {self.get_register_name(temp)}, {self.get_register_name(temp)}, {self.get_register_name(mode_reg)}")
            self.emit(f"setg {self.get_register_name(temp)}")
            self.reg_allocator.free_temp(pin_reg)
            self.reg_allocator.free_temp(dir_reg)
            self.reg_allocator.free_temp(mode_reg)
            self.reg_allocator.free_temp(temp)
            self.reg_allocator.free_temp(temp2)
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
        elif call.name == 'gpio_read':
            if len(call.args) != 1:
                raise RuntimeError(f"gpio_read expects 1 argument, got {len(call.args)}")
            pin_reg = self.generate_expression(call.args[0])
            self.emit(f"getg {self.get_register_name(result_reg)}")
            self.reg_allocator.free_temp(pin_reg)
        elif call.name == 'gpio_write':
            if len(call.args) != 2:
                raise RuntimeError(f"gpio_write expects 2 arguments, got {len(call.args)}")
            pin_reg = self.generate_expression(call.args[0])
            value_reg = self.generate_expression(call.args[1])
            # Pack: (pin << 8) | value
            temp = self.reg_allocator.get_temp_register()
            self.emit(f"shl {self.get_register_name(temp)}, {self.get_register_name(pin_reg)}, 8")
            self.emit(f"or {self.get_register_name(temp)}, {self.get_register_name(temp)}, {self.get_register_name(value_reg)}")
            self.emit(f"outg {self.get_register_name(temp)}")
            self.reg_allocator.free_temp(pin_reg)
            self.reg_allocator.free_temp(value_reg)
            self.reg_allocator.free_temp(temp)
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
        elif call.name == 'uart_set_baud':
            if len(call.args) != 1:
                raise RuntimeError(f"uart_set_baud expects 1 argument, got {len(call.args)}")
            baud_reg = self.generate_expression(call.args[0])
            self.emit(f"setu {self.get_register_name(baud_reg)}")
            self.reg_allocator.free_temp(baud_reg)
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
        elif call.name == 'uart_read':
            if len(call.args) != 0:
                raise RuntimeError(f"uart_read expects 0 arguments, got {len(call.args)}")
            self.emit(f"inu {self.get_register_name(result_reg)}")
        elif call.name == 'uart_write':
            if len(call.args) != 1:
                raise RuntimeError(f"uart_write expects 1 argument, got {len(call.args)}")
            data_reg = self.generate_expression(call.args[0])
            self.emit(f"outu {self.get_register_name(data_reg)}")
            self.reg_allocator.free_temp(data_reg)
            self.emit(f"mov {self.get_register_name(result_reg)}, 0")
        else:
            raise RuntimeError(f"Code generation error: Unknown hardware function '{call.name}' in function '{self.current_function}'")
        
        return result_reg
    
    def generate_return(self, stmt: Return) -> None:
        """Generate code for return statement."""
        # Mark that we have an explicit return
        self._has_explicit_return = True
        
        if stmt.value:
            value_reg = self.generate_expression(stmt.value)
            # Return value in r:0 by convention
            if value_reg != 0:
                self.emit(f"mov r:0, {self.get_register_name(value_reg)}")
            self.reg_allocator.free_temp(value_reg)
        else:
            self.emit("mov r:0, 0")
        
        # Return from function by restoring instruction pointer from link register
        if self.current_function == 'main':
            # Main function ends the program
            self.emit("hlt")
        else:
            # Restore return address from stack and return
            # r:30 currently points to where we saved the return address
            # Read return address into a temp register (NOT r:0, which contains return value!)
            # Use r:29 as temp for return address (r:0 contains function result)
            self.emit(f"lds r:29, [r:30]")  # Read return address into r:29
            self.emit(f"add r:30, r:30, 1")  # Restore stack pointer (pop return address)
            # Return to caller by jumping to return address
            self.emit(f"mov r:31, r:29")
    
    def generate_if(self, stmt: IfStmt) -> None:
        """Generate code for if statement."""
        condition_reg = self.generate_expression(stmt.condition)
        else_label = self.generate_label("else")
        end_label = self.generate_label("endif")
        
        # Test condition: if condition == 0 (false), jump to else/end
        zero_reg = self.reg_allocator.get_temp_register()
        self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
        
        # Conditional jump: if condition == 0 (false), jump to else/end
        # cmovz r:31, condition_reg, label addr means: if condition_reg == 0, set r:31 to label address (jump)
        if stmt.else_stmt:
            self.emit(f"cmovz r:31, {self.get_register_name(condition_reg)}, {else_label} addr")
        else:
            self.emit(f"cmovz r:31, {self.get_register_name(condition_reg)}, {end_label} addr")
        
        self.reg_allocator.free_temp(zero_reg)
        self.reg_allocator.free_temp(condition_reg)
        
        # Then branch
        self.generate_statement(stmt.then_stmt)
        
        # Unconditional jump to end (skip else branch)
        if stmt.else_stmt:
            self.emit(f"mov r:31, {end_label} addr")
        
        # Else branch
        if stmt.else_stmt:
            self.emit_label(else_label)
            self.generate_statement(stmt.else_stmt)
        
        self.emit_label(end_label)
    
    def generate_while(self, stmt: WhileStmt) -> None:
        """Generate code for while loop."""
        start_label = self.generate_label("while_start")
        end_label = self.generate_label("while_end")
        
        # Create loop context and push to stack
        loop_context = LoopContext(start_label, end_label, "while")
        self.loop_stack.append(loop_context)
        
        try:
            self.emit_label(start_label)
            
            # Evaluate condition
            condition_reg = self.generate_expression(stmt.condition)
            
            # Conditional jump: if condition == 0 (false), exit loop
            # cmovz r:31, condition_reg, end_label addr means: if condition_reg == 0, set r:31 to end_label address (jump)
            self.emit(f"cmovz r:31, {self.get_register_name(condition_reg)}, {end_label} addr")
            
            if condition_reg != 10:
                # Only free if we allocated it
                self.reg_allocator.free_temp(condition_reg)
            
            # Loop body
            self.generate_statement(stmt.body)
            
            # Unconditional jump back to start
            self.emit(f"mov r:31, {start_label} addr")
            
            self.emit_label(end_label)
        finally:
            # Remove loop context from stack
            self.loop_stack.pop()
    
    def generate_for(self, stmt: ForStmt) -> None:
        """Generate code for for loop."""
        # Initialize
        if stmt.init:
            self.generate_statement(stmt.init)
        
        start_label = self.generate_label("for_start")
        increment_label = self.generate_label("for_increment") if stmt.increment else None
        end_label = self.generate_label("for_end")
        
        # Create loop context and push to stack
        loop_context = LoopContext(start_label, end_label, "for", increment_label)
        self.loop_stack.append(loop_context)
        
        try:
            self.emit_label(start_label)
            
            # Condition check
            if stmt.condition:
                condition_reg = self.generate_expression(stmt.condition)
                zero_reg = self.reg_allocator.get_temp_register()
                self.emit(f"mov {self.get_register_name(zero_reg)}, 0")
                
                # Conditional jump: if condition == 0 (false), exit loop
                # cmovz r:31, condition_reg, end_label addr means: if condition_reg == 0, set r:31 to end_label address (jump)
                self.emit(f"cmovz r:31, {self.get_register_name(condition_reg)}, {end_label} addr")
                
                self.reg_allocator.free_temp(zero_reg)
                self.reg_allocator.free_temp(condition_reg)
            
            # Loop body
            self.generate_statement(stmt.body)
            
            # Increment section (with label for continue)
            if stmt.increment:
                self.emit_label(increment_label)
                self.generate_statement(stmt.increment)
            
            # Unconditional jump back to start
            self.emit(f"mov r:31, {start_label} addr")
            
            self.emit_label(end_label)
        finally:
            # Remove loop context from stack
            self.loop_stack.pop()
    
    def generate_block(self, block: Block) -> None:
        """Generate code for block."""
        for stmt in block.statements:
            self.generate_statement(stmt)
    
    def generate_break(self, stmt: BreakStmt) -> None:
        """Generate code for break statement."""
        if not self.loop_stack:
            raise RuntimeError("break statement outside of loop")
        
        loop_context = self.loop_stack[-1]
        # Jump to end of loop
        self.emit(f"mov r:31, {loop_context.end_label} addr")
    
    def generate_continue(self, stmt: ContinueStmt) -> None:
        """Generate code for continue statement."""
        if not self.loop_stack:
            raise RuntimeError("continue statement outside of loop")
        
        loop_context = self.loop_stack[-1]
        # For for loops, jump to increment section; for while loops, jump to start
        if loop_context.loop_type == "for" and loop_context.increment_label:
            self.emit(f"mov r:31, {loop_context.increment_label} addr")
        else:
            self.emit(f"mov r:31, {loop_context.start_label} addr")
    
    def generate_array_decl(self, decl: ArrayDecl) -> None:
        """Generate code for array declaration."""
        # Evaluate size (must be a literal constant)
        if not isinstance(decl.size, Literal):
            raise RuntimeError(f"Array size must be a constant literal, got {type(decl.size)}")
        size = decl.size.value
        if size <= 0:
            raise RuntimeError(f"Array size must be positive, got {size}")
        
        # Check if this is a global array (declared outside functions)
        is_global = (self.current_function is None)
        
        if is_global:
            # Global array - allocate in data section
            label = f"array_{decl.name}"
            self.global_data_labels[decl.name] = label
            self.data_section.append(f"{label}:")
            # Initialize with values or zeros
            if decl.initializer:
                # Initialize with provided values
                for i, init_expr in enumerate(decl.initializer):
                    if isinstance(init_expr, Literal):
                        self.data_section.append(f"\tdd {init_expr.value}")
                    else:
                        # For non-constant initializers, use 0 (would need runtime init)
                        self.data_section.append(f"\tdd 0")
                # Fill remaining elements with zeros
                for _ in range(size - len(decl.initializer)):
                    self.data_section.append(f"\tdd 0")
            else:
                # Initialize with zeros
                for _ in range(size):
                    self.data_section.append(f"\tdd 0")
            self.array_addresses[decl.name] = label  # Store label name for address calculation
        else:
            # Local array - allocate in memory (data section), not on stack
            # r:30 is used as stack pointer for variables only
            # Arrays are allocated in memory with unique labels
            label = f"array_{self.current_function}_{decl.name}_{self.label_counter}"
            self.label_counter += 1
            self.data_section.append(f"{label}:")
            
            # Initialize with values or zeros
            if decl.initializer:
                # Initialize with provided values
                for i, init_expr in enumerate(decl.initializer):
                    if isinstance(init_expr, Literal):
                        self.data_section.append(f"\tdd {init_expr.value}")
                    else:
                        # For non-constant initializers, we need to generate code to initialize at runtime
                        # For now, use 0 and generate initialization code
                        self.data_section.append(f"\tdd 0")
                        # Generate runtime initialization code
                        value_reg = self.generate_expression(init_expr)
                        addr_reg = self.reg_allocator.get_temp_register()
                        self.emit(f"mov {self.get_register_name(addr_reg)}, {label} addr")
                        index_reg = self.reg_allocator.get_temp_register()
                        self.emit(f"mov {self.get_register_name(index_reg)}, {i}")
                        self.emit(f"add {self.get_register_name(addr_reg)}, {self.get_register_name(addr_reg)}, {self.get_register_name(index_reg)}")
                        self.emit(f"lds [{self.get_register_name(addr_reg)}], {self.get_register_name(value_reg)}")
                        self.reg_allocator.free_temp(addr_reg)
                        self.reg_allocator.free_temp(index_reg)
                        self.reg_allocator.free_temp(value_reg)
                # Fill remaining elements with zeros
                for _ in range(size - len(decl.initializer)):
                    self.data_section.append(f"\tdd 0")
            else:
                # Initialize with zeros
                for _ in range(size):
                    self.data_section.append(f"\tdd 0")
            
            # Store label name for address calculation
            self.array_addresses[decl.name] = label
            self.array_sizes[decl.name] = size
    
    def generate_pointer_decl(self, decl: PointerDecl) -> None:
        """Generate code for pointer declaration."""
        # Allocate register for pointer (stores address)
        reg_num = self.reg_allocator.allocate(decl.name)
        
        if decl.initializer:
            # Evaluate initializer (should be AddressOf expression)
            addr_reg = self.generate_expression(decl.initializer)
            if addr_reg != reg_num:
                self.emit(f"mov {self.get_register_name(reg_num)}, {self.get_register_name(addr_reg)}")
                self.reg_allocator.free_temp(addr_reg)
        else:
            # Initialize to 0 (null pointer)
            self.emit(f"mov {self.get_register_name(reg_num)}, 0")
    
    def generate_array_access(self, expr: ArrayAccess) -> int:
        """Generate code for array element access: arr[index]"""
        # Evaluate index
        index_reg = self.generate_expression(expr.index)
        
        # Get base address
        if expr.name in self.array_addresses:
            base_addr = self.array_addresses[expr.name]
            result_reg = self.reg_allocator.get_temp_register()
            addr_reg = self.reg_allocator.get_temp_register()
            
            # Calculate address: base + index (each element = 1 memory cell)
            # All arrays (global and local) are now in memory with labels
            if isinstance(base_addr, str):
                # Array in memory - use label address
                self.emit(f"mov {self.get_register_name(addr_reg)}, {base_addr} addr")
            else:
                # This should not happen anymore - all arrays should have string labels
                raise RuntimeError(f"Array {expr.name} has invalid address type: {type(base_addr)}")
            
            # Add index
            self.emit(f"add {self.get_register_name(addr_reg)}, {self.get_register_name(addr_reg)}, {self.get_register_name(index_reg)}")
            
            # Load value: lds result_reg, [addr_reg]
            self.emit(f"lds {self.get_register_name(result_reg)}, [{self.get_register_name(addr_reg)}]")
            
            self.reg_allocator.free_temp(addr_reg)
            self.reg_allocator.free_temp(index_reg)
            return result_reg
        else:
            raise RuntimeError(f"Array {expr.name} not found")
    
    def generate_address_of(self, expr: AddressOf) -> int:
        """Generate code for address-of operator: &x"""
        operand = expr.operand
        result_reg = self.reg_allocator.get_temp_register()
        
        if isinstance(operand, Identifier):
            # &variable
            if operand.name in self.variable_addresses:
                addr = self.variable_addresses[operand.name]
                if isinstance(addr, str):
                    # Global variable - use label
                    self.emit(f"mov {self.get_register_name(result_reg)}, {addr} addr")
                else:
                    # Local variable - calculate address from r30
                    self.emit(f"mov {self.get_register_name(result_reg)}, r:30")
                    if addr > 0:
                        offset_reg = self.reg_allocator.get_temp_register()
                        self.emit(f"mov {self.get_register_name(offset_reg)}, {addr}")
                        self.emit(f"add {self.get_register_name(result_reg)}, {self.get_register_name(result_reg)}, {self.get_register_name(offset_reg)}")
                        self.reg_allocator.free_temp(offset_reg)
            elif operand.name in self.array_addresses:
                # &array (base address)
                # All arrays (global and local) are now in memory with labels
                base_addr = self.array_addresses[operand.name]
                if isinstance(base_addr, str):
                    self.emit(f"mov {self.get_register_name(result_reg)}, {base_addr} addr")
                else:
                    # This should not happen anymore - all arrays should have string labels
                    raise RuntimeError(f"Code generation error: Array '{operand.name}' has invalid address type '{type(base_addr).__name__}' in function '{self.current_function}'")
            else:
                raise RuntimeError(f"Variable or array {operand.name} not found for address-of")
        elif isinstance(operand, ArrayAccess):
            # &arr[i] - address of array element
            arr_name = operand.name
            index_reg = self.generate_expression(operand.index)
            
            if arr_name in self.array_addresses:
                base_addr = self.array_addresses[arr_name]
                addr_reg = self.reg_allocator.get_temp_register()
                
                # Calculate base address
                # All arrays (global and local) are now in memory with labels
                if isinstance(base_addr, str):
                    self.emit(f"mov {self.get_register_name(addr_reg)}, {base_addr} addr")
                else:
                    # This should not happen anymore - all arrays should have string labels
                    raise RuntimeError(f"Array {arr_name} has invalid address type: {type(base_addr)}")
                
                # Add index
                self.emit(f"add {self.get_register_name(addr_reg)}, {self.get_register_name(addr_reg)}, {self.get_register_name(index_reg)}")
                self.emit(f"mov {self.get_register_name(result_reg)}, {self.get_register_name(addr_reg)}")
                
                self.reg_allocator.free_temp(addr_reg)
                self.reg_allocator.free_temp(index_reg)
            else:
                raise RuntimeError(f"Array {arr_name} not found")
        elif isinstance(operand, Dereference):
            # &*ptr - just the value of ptr (address it points to)
            return self.generate_expression(operand.operand)
        else:
            raise RuntimeError(f"Code generation error: Cannot take address of '{type(operand).__name__}' in function '{self.current_function}'")
        
        return result_reg
    
    def generate_dereference(self, expr: Dereference) -> int:
        """Generate code for pointer dereference: *ptr"""
        # Evaluate operand to get address
        addr_reg = self.generate_expression(expr.operand)
        
        # Load value from address: lds result_reg, [addr_reg]
        result_reg = self.reg_allocator.get_temp_register()
        self.emit(f"lds {self.get_register_name(result_reg)}, [{self.get_register_name(addr_reg)}]")
        
        self.reg_allocator.free_temp(addr_reg)
        return result_reg
    
    def generate_array_assignment(self, assign: ArrayAssignment) -> None:
        """Generate code for array element assignment: arr[i] = value"""
        # Evaluate index and value
        index_reg = self.generate_expression(assign.index)
        value_reg = self.generate_expression(assign.value)
        
        # Get base address
        if assign.name in self.array_addresses:
            base_addr = self.array_addresses[assign.name]
            addr_reg = self.reg_allocator.get_temp_register()
            
            # Calculate address: base + index
            # All arrays (global and local) are now in memory with labels
            if isinstance(base_addr, str):
                # Array in memory - use label address
                self.emit(f"mov {self.get_register_name(addr_reg)}, {base_addr} addr")
            else:
                # This should not happen anymore - all arrays should have string labels
                raise RuntimeError(f"Code generation error: Array '{assign.name}' has invalid address type '{type(base_addr).__name__}' in function '{self.current_function}'")
            
            # Add index
            self.emit(f"add {self.get_register_name(addr_reg)}, {self.get_register_name(addr_reg)}, {self.get_register_name(index_reg)}")
            
            # Store value: lds [addr_reg], value_reg
            self.emit(f"lds [{self.get_register_name(addr_reg)}], {self.get_register_name(value_reg)}")
            
            self.reg_allocator.free_temp(addr_reg)
            self.reg_allocator.free_temp(index_reg)
            self.reg_allocator.free_temp(value_reg)
        else:
            raise RuntimeError(f"Array {assign.name} not found")
    
    def generate_pointer_assignment(self, assign: PointerAssignment) -> None:
        """Generate code for pointer dereference assignment: *ptr = value"""
        # Evaluate address (value of pointer)
        addr_reg = self.generate_expression(assign.operand)
        # Evaluate value
        value_reg = self.generate_expression(assign.value)
        
        # Store value at address: lds [addr_reg], value_reg
        self.emit(f"lds [{self.get_register_name(addr_reg)}], {self.get_register_name(value_reg)}")
        
        self.reg_allocator.free_temp(addr_reg)
        self.reg_allocator.free_temp(value_reg)
    
    def generate_increment(self, stmt: Increment):
        """Generate code for increment statement."""
        reg = self.reg_allocator.get_register(stmt.name)
        if reg is None:
            if stmt.name.startswith('r') and stmt.name[1:].isdigit():
                reg = int(stmt.name[1:])
            else:
                raise RuntimeError(f"Undefined variable: {stmt.name}")
        
        one_reg = self.reg_allocator.get_temp_register()
        self.emit(f"mov {self.get_register_name(one_reg)}, 1")
        self.emit(f"add {self.get_register_name(reg)}, {self.get_register_name(reg)}, {self.get_register_name(one_reg)}")
        self.reg_allocator.free_temp(one_reg)
    
    def generate_decrement(self, stmt: Decrement):
        """Generate code for decrement statement."""
        reg = self.reg_allocator.get_register(stmt.name)
        if reg is None:
            if stmt.name.startswith('r') and stmt.name[1:].isdigit():
                reg = int(stmt.name[1:])
            else:
                raise RuntimeError(f"Undefined variable: {stmt.name}")
        
        one_reg = self.reg_allocator.get_temp_register()
        self.emit(f"mov {self.get_register_name(one_reg)}, 1")
        self.emit(f"sub {self.get_register_name(reg)}, {self.get_register_name(reg)}, {self.get_register_name(one_reg)}")
        self.reg_allocator.free_temp(one_reg)
