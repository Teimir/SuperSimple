"""
Main window for the GUI application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys as sys_module

# Add project root to path for imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys_module.path:
    sys_module.path.insert(0, _project_root)

# Import GUI components (try relative first, then absolute)
try:
    from .code_editor import CodeEditor
    from .output_panel import OutputPanel
    from .file_manager import FileManager
    from .error_handler import ErrorHandler
    from .registers_panel import RegistersPanel
    from .debugger_panel import DebuggerPanel
    from .debugger import Debugger
except ImportError:
    from gui.code_editor import CodeEditor
    from gui.output_panel import OutputPanel
    from gui.file_manager import FileManager
    from gui.error_handler import ErrorHandler
    from gui.registers_panel import RegistersPanel
    from gui.debugger_panel import DebuggerPanel
    from gui.debugger import Debugger

# Import interpreter components
from lexer import Lexer, TokenType
from parser import Parser
from interpreter import Interpreter, RuntimeError
from preprocessor import Preprocessor, PreprocessingError


class MainWindow(tk.Tk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("SC Language Interpreter")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Create main content area first (needed for file_manager and error_handler)
        self._create_content()
        
        # Create status bar
        self._create_status_bar()
        
        # Initialize components (must be before menu and toolbar)
        self.file_manager = FileManager(self.editor, self)
        self.error_handler = ErrorHandler(self.editor, self.output_panel)
        
        # Debugger state
        self.debugger: Optional[Debugger] = None
        self.is_debug_mode = False
        
        # Create menu bar (after file_manager is initialized)
        self._create_menu()
        
        # Create toolbar (after file_manager is initialized)
        self._create_toolbar()
        
        # Track execution state
        self._is_running = False
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Update title
        self.update_title()
    
    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.file_manager.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.file_manager.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.file_manager.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.file_manager.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Program", command=self.run_program, accelerator="F5")
        run_menu.add_command(label="Debug", command=self.start_debug, accelerator="F9")
        run_menu.add_separator()
        run_menu.add_command(label="Clear Output", command=self.clear_output)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.bind('<Control-n>', lambda e: self.file_manager.new_file())
        self.bind('<Control-o>', lambda e: self.file_manager.open_file())
        self.bind('<Control-s>', lambda e: self.file_manager.save_file())
        self.bind('<Control-S>', lambda e: self.file_manager.save_file_as())
        self.bind('<F5>', lambda e: self.run_program())
        self.bind('<F9>', lambda e: self.start_debug())
        self.bind('<F10>', lambda e: self.debug_step() if self.is_debug_mode else None)
    
    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        ttk.Button(toolbar, text="Open", command=self.file_manager.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.file_manager.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Run (F5)", command=self.run_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Debug (F9)", command=self.start_debug).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=2)
    
    def _create_content(self):
        """Create the main content area."""
        # Main horizontal paned window: debug panels (left) and code/execution (right)
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side: Debug panels (hidden by default)
        left_frame = ttk.Frame(main_paned)
        # Don't add to paned window initially - will be added when debugging starts
        self.debug_paned = ttk.PanedWindow(left_frame, orient=tk.VERTICAL)
        self.debug_paned.pack(fill=tk.BOTH, expand=True)
        
        # Debugger control panel
        debugger_frame = ttk.Frame(self.debug_paned)
        self.debug_paned.add(debugger_frame, weight=1)
        self.debugger_panel = DebuggerPanel(debugger_frame)
        self.debugger_panel.pack(fill=tk.BOTH, expand=True)
        
        # Registers panel (larger size)
        registers_frame = ttk.Frame(self.debug_paned)
        self.debug_paned.add(registers_frame, weight=3)
        
        self.registers_panel = RegistersPanel(registers_frame)
        self.registers_panel.pack(fill=tk.BOTH, expand=True)
        
        # Store reference for showing/hiding
        self.debug_panels_frame = left_frame
        self.main_paned = main_paned
        self._debug_panel_added = False
        
        # Right side: Code editor and execution output (vertical split)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=1)
        
        # Top: Code editor (secondary - in notebook tab)
        editor_notebook = ttk.Notebook(right_paned)
        right_paned.add(editor_notebook, weight=1)
        
        editor_frame = ttk.Frame(editor_notebook)
        editor_notebook.add(editor_frame, text="Code Editor")
        
        self.editor = CodeEditor(editor_frame)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Bottom: Execution output (primary)
        output_frame = ttk.Frame(right_paned)
        right_paned.add(output_frame, weight=2)
        
        self.output_panel = OutputPanel(output_frame)
        self.output_panel.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        self.file_label = ttk.Label(self.status_bar, text="No file", relief=tk.SUNKEN, anchor=tk.E, width=30)
        self.file_label.pack(side=tk.RIGHT, padx=2, pady=2)
    
    def update_title(self):
        """Update the window title."""
        file_path = self.file_manager.get_current_file()
        if file_path:
            filename = os.path.basename(file_path)
            modified = "*" if self.file_manager.has_unsaved_changes() else ""
            self.title(f"SC Language Interpreter - {filename}{modified}")
            self.file_label.config(text=filename)
        else:
            modified = "*" if self.editor.is_modified() else ""
            self.title(f"SC Language Interpreter - Untitled{modified}")
            self.file_label.config(text="Untitled")
    
    def on_text_modified(self):
        """Callback when text is modified."""
        self.update_title()
    
    def run_program(self):
        """Run the current program."""
        if self._is_running:
            messagebox.showwarning("Warning", "Program is already running!")
            return
        
        # Clear previous errors
        self.error_handler.clear_errors()
        self.output_panel.clear_output()
        
        # Hide debug panels for normal run
        self._hide_debug_panels()
        
        # Get code from editor
        code = self.editor.get_text()
        
        if not code.strip():
            self.output_panel.append_error("No code to execute")
            return
        
        self._is_running = True
        self.status_label.config(text="Running...")
        self.output_panel.append_message("Starting program execution...")
        
        try:
            # Create a custom stdout capture
            class OutputCapture:
                def __init__(self, output_panel):
                    self.output_panel = output_panel
                    self.buffer = ""
                
                def write(self, text):
                    self.buffer += text
                    # Flush on newline or periodically
                    if '\n' in text or len(self.buffer) > 100:
                        self.output_panel.append_output(self.buffer)
                        self.buffer = ""
                
                def flush(self):
                    if self.buffer:
                        self.output_panel.append_output(self.buffer)
                        self.buffer = ""
            
            output_capture = OutputCapture(self.output_panel)
            
            # Save original stdout
            original_stdout = sys_module.stdout
            
            try:
                # Redirect stdout to our capture
                sys_module.stdout = output_capture
                
                # Preprocess
                self.output_panel.append_message("Step 1/4: Preprocessing...", 'info')
                preprocessor = Preprocessor()
                try:
                    # Use process_content for in-memory code
                    # Set current_dir to the directory of the current file, or project root
                    current_dir = None
                    if self.file_manager.get_current_file():
                        current_dir = os.path.dirname(os.path.abspath(self.file_manager.get_current_file()))
                    else:
                        current_dir = os.getcwd()
                    
                    source_code = preprocessor.process_content(code, current_dir)
                    self.output_panel.append_message("✓ Preprocessing completed", 'success')
                except PreprocessingError as e:
                    self.error_handler.handle_preprocessing_error(e)
                    return
                
                # Tokenize
                self.output_panel.append_message("Step 2/4: Lexical analysis...", 'info')
                lexer = Lexer(source_code)
                tokens = lexer.tokenize()
                
                # Check for lexer errors
                for token in tokens:
                    if token.type == TokenType.ERROR:
                        self.error_handler.handle_lexer_error(token)
                        return
                self.output_panel.append_message(f"✓ Lexical analysis completed ({len(tokens)} tokens)", 'success')
                
                # Parse
                self.output_panel.append_message("Step 3/4: Syntax analysis...", 'info')
                parser = Parser(tokens)
                try:
                    ast = parser.parse()
                    self.output_panel.append_message("✓ Syntax analysis completed", 'success')
                except SyntaxError as e:
                    self.error_handler.handle_syntax_error(e)
                    return
                
                # Interpret
                self.output_panel.append_message("Step 4/4: Execution...", 'info')
                interpreter = Interpreter(ast)
                try:
                    result = interpreter.interpret()
                    self.output_panel.append_message(f"✓ Program executed successfully. Return value: {result}", 'success')
                except RuntimeError as e:
                    self.error_handler.handle_runtime_error(e)
                    return
                
            finally:
                # Restore original stdout
                sys_module.stdout = original_stdout
                output_capture.flush()
        
        except Exception as e:
            self.error_handler.handle_general_error(e)
            import traceback
            self.output_panel.append_error(f"Unexpected error:\n{traceback.format_exc()}")
        
        finally:
            self._is_running = False
            self.status_label.config(text="Ready")
    
    def clear_output(self):
        """Clear the output panel."""
        self.output_panel.clear_all()
    
    def _show_debug_panels(self):
        """Show debug panels (registers and debugger)."""
        if not hasattr(self, 'debug_panels_frame'):
            return
        if not self._debug_panel_added:
            self.main_paned.add(self.debug_panels_frame, weight=2)  # Larger weight for registers
            self._debug_panel_added = True
    
    def _hide_debug_panels(self):
        """Hide debug panels."""
        if not hasattr(self, 'debug_panels_frame'):
            return
        if self._debug_panel_added:
            try:
                self.main_paned.forget(self.debug_panels_frame)
                self._debug_panel_added = False
            except:
                pass
    
    def start_debug(self):
        """Start debugging session."""
        if self._is_running:
            messagebox.showwarning("Warning", "Program is already running!")
            return
        
        # Clear previous errors
        self.error_handler.clear_errors()
        self.output_panel.clear_output()
        
        # Show debug panels
        self._show_debug_panels()
        self.is_debug_mode = True
        
        # Get code from editor
        code = self.editor.get_text()
        
        if not code.strip():
            self.output_panel.append_error("No code to execute")
            return
        
        self._is_running = True
        self.status_label.config(text="Debugging...")
        self.output_panel.append_message("Starting debug session...", 'info')
        
        try:
            # Create output capture
            class OutputCapture:
                def __init__(self, output_panel):
                    self.output_panel = output_panel
                    self.buffer = ""
                
                def write(self, text):
                    self.buffer += text
                    if '\n' in text or len(self.buffer) > 100:
                        self.output_panel.append_output(self.buffer)
                        self.buffer = ""
                
                def flush(self):
                    if self.buffer:
                        self.output_panel.append_output(self.buffer)
                        self.buffer = ""
            
            output_capture = OutputCapture(self.output_panel)
            original_stdout = sys_module.stdout
            
            try:
                sys_module.stdout = output_capture
                
                # Preprocess
                preprocessor = Preprocessor()
                current_dir = None
                if self.file_manager.get_current_file():
                    current_dir = os.path.dirname(os.path.abspath(self.file_manager.get_current_file()))
                else:
                    current_dir = os.getcwd()
                
                source_code = preprocessor.process_content(code, current_dir)
                
                # Tokenize
                lexer = Lexer(source_code)
                tokens = lexer.tokenize()
                
                for token in tokens:
                    if token.type == TokenType.ERROR:
                        self.error_handler.handle_lexer_error(token)
                        return
                
                # Parse
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Create interpreter and debugger
                interpreter = Interpreter(ast)
                self.debugger = Debugger(interpreter)
                self.debugger_interpreter = interpreter  # Keep reference
                
                # Setup debugger callbacks
                def on_step(stmt, func, index):
                    try:
                        # Update registers
                        if hasattr(self, 'debugger_interpreter') and self.debugger_interpreter:
                            try:
                                self.registers_panel.update_registers(self.debugger_interpreter.registers)
                            except Exception as e:
                                self.output_panel.append_error(f"Error updating registers: {e}")
                        
                        # Update debugger info
                        if stmt:
                            stmt_type = type(stmt).__name__
                        else:
                            stmt_type = "Unknown"
                        if func and hasattr(func, 'name'):
                            func_name = func.name
                        else:
                            func_name = "Unknown"
                        
                        try:
                            self.debugger_panel.update_info(func_name, stmt_type, index)
                        except Exception as e:
                            self.output_panel.append_error(f"Error updating debugger info: {e}")
                    except Exception as e:
                        # Don't crash on callback errors
                        import traceback
                        error_msg = f"Error in debugger callback: {e}"
                        self.output_panel.append_error(error_msg)
                        traceback.print_exc()
                
                self.debugger.set_step_callback(on_step)
                
                # Setup debugger panel buttons
                self.debugger_panel.step_button.config(command=self.debug_step)
                self.debugger_panel.continue_button.config(command=self.debug_continue)
                self.debugger_panel.pause_button.config(command=self.debug_pause)
                self.debugger_panel.stop_button.config(command=self.debug_stop)
                self.debugger_panel.set_debugging_state(True)
                
                # Start debugging
                if 'main' not in interpreter.functions:
                    raise RuntimeError("Program must have a 'main' function")
                
                main_func = interpreter.functions['main']
                self.debugger.start_debugging(main_func)
                
                # Update initial state
                self.registers_panel.update_registers(self.debugger_interpreter.registers)
                if main_func.body and hasattr(main_func.body, 'statements') and main_func.body.statements:
                    self.debugger_panel.update_info("main", type(main_func.body.statements[0]).__name__, 0)
                else:
                    self.debugger_panel.update_info("main", "No statements", 0)
                
                self.output_panel.append_message("Debug session started. Use Step Over to execute statements.", 'success')
                
            finally:
                sys_module.stdout = original_stdout
                output_capture.flush()
        
        except Exception as e:
            self.error_handler.handle_general_error(e)
            import traceback
            self.output_panel.append_error(f"Unexpected error:\n{traceback.format_exc()}")
            self.is_debug_mode = False
            self._hide_debug_panels()
        
        finally:
            if not self.is_debug_mode:
                self._is_running = False
                self.status_label.config(text="Ready")
    
    def debug_step(self):
        """Execute one step in debugger."""
        if not self.debugger or not self.is_debug_mode:
            return
        
        try:
            if self.debugger.step_over():
                # Step successful, state already updated by callback
                pass
            else:
                # Debugging finished
                self.output_panel.append_message("Debug session finished.", 'success')
                self.debug_stop()
        except RuntimeError as e:
            import traceback
            error_msg = f"Runtime error: {str(e)}\n{traceback.format_exc()}"
            self.output_panel.append_error(error_msg)
            # Don't stop debugging on runtime errors, just pause
            if self.debugger:
                self.debugger.pause()
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.output_panel.append_error(error_msg)
            # Don't stop debugging on other errors, just pause
            if self.debugger:
                self.debugger.pause()
    
    def debug_continue(self):
        """Continue execution in debugger."""
        if not self.debugger or not self.is_debug_mode:
            return
        
        # For now, just run to completion
        self.output_panel.append_message("Continuing execution...", 'info')
        try:
            # Run remaining steps
            while self.debugger.step_over():
                pass
            self.output_panel.append_message("Execution completed.", 'success')
            self.debug_stop()
        except Exception as e:
            self.error_handler.handle_general_error(e)
            self.debug_stop()
    
    def debug_pause(self):
        """Pause debugger execution."""
        if self.debugger:
            self.debugger.pause()
            self.output_panel.append_message("Debugging paused.", 'info')
    
    def debug_stop(self):
        """Stop debugging session."""
        if self.debugger:
            self.debugger.stop_debugging()
            self.debugger = None
        
        if hasattr(self, 'debugger_interpreter'):
            self.debugger_interpreter = None
        
        self.is_debug_mode = False
        self._is_running = False
        self.debugger_panel.set_debugging_state(False)
        self.debugger_panel.clear_info()
        self.registers_panel.clear_registers()
        self._hide_debug_panels()
        self.status_label.config(text="Ready")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "SC Language Interpreter GUI\n\n"
            "A simple GUI for the SC language interpreter.\n"
            "Version 1.0.0"
        )
    
    def on_closing(self):
        """Handle window closing."""
        if self.file_manager.has_unsaved_changes():
            if not self.file_manager._check_save_changes():
                return
        
        self.destroy()
