"""
Debugger control panel for step-by-step debugging.
"""

import tkinter as tk
from tkinter import ttk


class DebuggerPanel(ttk.Frame):
    """Panel for debugger controls and current execution info."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Control buttons frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.step_button = ttk.Button(
            controls_frame,
            text="Step Over (F10)",
            width=15
        )
        self.step_button.pack(side=tk.LEFT, padx=2)
        
        self.continue_button = ttk.Button(
            controls_frame,
            text="Continue (F5)",
            width=15
        )
        self.continue_button.pack(side=tk.LEFT, padx=2)
        
        self.pause_button = ttk.Button(
            controls_frame,
            text="Pause",
            width=15
        )
        self.pause_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(
            controls_frame,
            text="Stop",
            width=15
        )
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # Current execution info
        info_frame = ttk.LabelFrame(self, text="Current Execution", padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.function_label = tk.Label(
            info_frame,
            text="Function: -",
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            anchor='w'
        )
        self.function_label.pack(fill=tk.X, pady=2)
        
        self.statement_label = tk.Label(
            info_frame,
            text="Statement: -",
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            anchor='w'
        )
        self.statement_label.pack(fill=tk.X, pady=2)
        
        self.index_label = tk.Label(
            info_frame,
            text="Index: -",
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            anchor='w'
        )
        self.index_label.pack(fill=tk.X, pady=2)
    
    def update_info(self, function_name: str, statement_type: str, index: int):
        """Update debugger info display."""
        self.function_label.config(text=f"Function: {function_name}")
        self.statement_label.config(text=f"Statement: {statement_type}")
        self.index_label.config(text=f"Index: {index}")
    
    def clear_info(self):
        """Clear debugger info."""
        self.function_label.config(text="Function: -")
        self.statement_label.config(text="Statement: -")
        self.index_label.config(text="Index: -")
    
    def set_debugging_state(self, is_debugging: bool):
        """Enable/disable debugger controls."""
        state = 'normal' if is_debugging else 'disabled'
        self.step_button.config(state=state)
        self.continue_button.config(state=state)
        self.pause_button.config(state=state)
        self.stop_button.config(state=state)
