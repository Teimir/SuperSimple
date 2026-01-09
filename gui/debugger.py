"""
Debugger for step-by-step execution of programs.
"""

from typing import Optional, Callable, List, Tuple
from parser import Statement, FunctionDef, Block
from interpreter import Interpreter, Environment, ReturnException, BreakException, ContinueException


class Debugger:
    """Step-by-step debugger for the interpreter."""
    
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.is_debugging = False
        self.is_paused = False
        self.current_statement: Optional[Statement] = None
        self.current_function: Optional[FunctionDef] = None
        self.current_env: Optional[Environment] = None
        self.statement_index = 0
        self.call_stack: List[Tuple[FunctionDef, Environment, int]] = []
        self.step_callback: Optional[Callable] = None
        self.breakpoints: set = set()  # Set of line numbers
    
    def start_debugging(self, main_func: FunctionDef):
        """Start debugging session."""
        self.is_debugging = True
        self.is_paused = True
        self.current_function = main_func
        # Initialize global environment first
        for global_var in self.interpreter.program.global_vars:
            self.interpreter.execute_var_decl(global_var, self.interpreter.global_env)
        # Create environment for main function
        self.current_env = Environment(self.interpreter.global_env)
        self.statement_index = 0
        self.call_stack = [(main_func, self.current_env, 0)]
    
    def stop_debugging(self):
        """Stop debugging session."""
        self.is_debugging = False
        self.is_paused = False
        self.current_statement = None
        self.current_function = None
        self.current_env = None
        self.statement_index = 0
        self.call_stack = []
    
    def step_over(self) -> bool:
        """Execute one statement (step over)."""
        if not self.is_debugging or not self.is_paused:
            return False
        
        if not self.current_function or not self.current_env:
            return False
        
        body = self.current_function.body
        # body is a Block object, need to access .statements
        if not hasattr(body, 'statements'):
            # If body is not a Block, something is wrong
            self.stop_debugging()
            return False
        
        statements = body.statements
        if not statements or len(statements) == 0:
            # Empty function body
            self.stop_debugging()
            return False
        
        if self.statement_index >= len(statements):
            # Function finished
            if self.call_stack:
                self.call_stack.pop()
                if self.call_stack:
                    self.current_function, self.current_env, self.statement_index = self.call_stack[-1]
                    # Recursively check if we can continue
                    return self.step_over()
                else:
                    self.stop_debugging()
                    return False
            else:
                self.stop_debugging()
                return False
        
        # Get current statement
        if self.statement_index < 0 or self.statement_index >= len(statements):
            self.stop_debugging()
            return False
        
        self.current_statement = statements[self.statement_index]
        
        # Check for breakpoint
        # Note: We don't have line numbers in AST, so breakpoints would need to be implemented differently
        
        # Execute statement
        try:
            # Execute the statement - execute_statement handles all statement types
            self.interpreter.execute_statement(self.current_statement, self.current_env)
        except ReturnException:
            # Return statement is not an error - it's a normal way to exit a function
            # Move to next statement (which won't exist, so function will finish)
            self.statement_index = len(statements)  # Set to end to trigger function finish
            # Update call stack
            if self.call_stack:
                self.call_stack[-1] = (self.current_function, self.current_env, self.statement_index)
            # Call step callback if set
            if self.step_callback and self.current_statement:
                try:
                    self.step_callback(self.current_statement, self.current_function, self.statement_index)
                except Exception as e:
                    # Don't stop debugging if callback fails
                    import traceback
                    print(f"Debugger callback error: {e}")
                    traceback.print_exc()
            return True  # Continue to next iteration which will detect function finished
        except (BreakException, ContinueException):
            # Break and Continue are control flow exceptions, not errors
            # They should be handled by the loop constructs, but if they escape,
            # we'll just continue to next statement
            self.statement_index += 1
            # Update call stack
            if self.call_stack:
                self.call_stack[-1] = (self.current_function, self.current_env, self.statement_index)
            # Call step callback if set
            if self.step_callback and self.current_statement:
                try:
                    self.step_callback(self.current_statement, self.current_function, self.statement_index)
                except Exception as e:
                    import traceback
                    print(f"Debugger callback error: {e}")
                    traceback.print_exc()
            return True
        except Exception as e:
            # Error occurred - don't stop debugging, just raise the error
            # The caller (GUI) will handle displaying the error
            raise
        
        # Move to next statement
        self.statement_index += 1
        
        # Update call stack
        if self.call_stack:
            self.call_stack[-1] = (self.current_function, self.current_env, self.statement_index)
        
        # Call step callback if set
        if self.step_callback and self.current_statement:
            try:
                self.step_callback(self.current_statement, self.current_function, self.statement_index)
            except Exception as e:
                # Don't stop debugging if callback fails
                import traceback
                print(f"Debugger callback error: {e}")
                traceback.print_exc()
        
        return True
    
    def continue_execution(self):
        """Continue execution until next breakpoint or end."""
        self.is_paused = False
        # For now, just run to completion
        # In a full implementation, would continue until breakpoint
    
    def pause(self):
        """Pause execution."""
        self.is_paused = True
    
    def get_current_line_info(self) -> Optional[Tuple[str, int]]:
        """Get current function name and statement index."""
        if self.current_function:
            return (self.current_function.name, self.statement_index)
        return None
    
    def set_step_callback(self, callback: Callable):
        """Set callback to be called on each step."""
        self.step_callback = callback
