"""
Registers panel for displaying CPU register values.
"""

import tkinter as tk
from tkinter import ttk


class RegistersPanel(ttk.Frame):
    """Panel for displaying CPU registers (r0-r31)."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Create scrollable frame
        canvas = tk.Canvas(self, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            self.scrollable_frame,
            text="CPU Registers (r0-r31)",
            font=('Consolas', 9, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        title_label.pack(pady=2)
        
        # Create register display
        self.register_labels = {}
        self.register_values = {}
        
        # Create two columns for registers
        columns_frame = tk.Frame(self.scrollable_frame, bg='#1e1e1e')
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Left column (r0-r15)
        left_column = tk.Frame(columns_frame, bg='#1e1e1e')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        # Right column (r16-r31)
        right_column = tk.Frame(columns_frame, bg='#1e1e1e')
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        # Create headers for both columns
        for col_frame, col_name in [(left_column, "r0-r15"), (right_column, "r16-r31")]:
            header_frame = tk.Frame(col_frame, bg='#1e1e1e')
            header_frame.pack(fill=tk.X, pady=(0, 2))
            
            tk.Label(header_frame, text="Reg", font=('Consolas', 7, 'bold'), bg='#1e1e1e', fg='#ffffff', width=5).pack(side=tk.LEFT, padx=1)
            tk.Label(header_frame, text="Hex", font=('Consolas', 7, 'bold'), bg='#1e1e1e', fg='#ffffff', width=10).pack(side=tk.LEFT, padx=1)
            tk.Label(header_frame, text="Dec", font=('Consolas', 7, 'bold'), bg='#1e1e1e', fg='#ffffff', width=10).pack(side=tk.LEFT, padx=1)
        
        # Create register rows in two columns
        for i in range(32):
            # Choose column
            if i < 16:
                col_frame = left_column
            else:
                col_frame = right_column
            
            reg_frame = tk.Frame(col_frame, bg='#1e1e1e')
            reg_frame.pack(fill=tk.X, pady=0)
            
            # Register name
            reg_name = f"r{i}"
            if i == 31:
                reg_name = "r31(IP)"
            
            name_label = tk.Label(
                reg_frame,
                text=reg_name,
                font=('Consolas', 7, 'bold'),
                bg='#1e1e1e',
                fg='#569cd6',
                width=5,
                anchor='w',
                relief=tk.FLAT,
                padx=1,
                pady=0
            )
            name_label.pack(side=tk.LEFT, padx=1)
            
            # Hex value
            hex_label = tk.Label(
                reg_frame,
                text="0x00000000",
                font=('Consolas', 7, 'bold'),
                bg='#252526',
                fg='#4ec9b0',
                width=10,
                anchor='w',
                relief=tk.FLAT,
                padx=1,
                pady=0
            )
            hex_label.pack(side=tk.LEFT, padx=1)
            
            # Decimal value (unsigned) - compact
            dec_label = tk.Label(
                reg_frame,
                text="0",
                font=('Consolas', 7),
                bg='#252526',
                fg='#d4d4d4',
                width=10,
                anchor='w',
                relief=tk.FLAT,
                padx=1,
                pady=0
            )
            dec_label.pack(side=tk.LEFT, padx=1)
            
            # Store references
            self.register_labels[i] = {
                'hex': hex_label,
                'decimal': dec_label,
                'signed': None  # Removed signed column to save space
            }
            self.register_values[i] = 0
    
    def update_registers(self, registers):
        """Update register display with new values."""
        for i, value in enumerate(registers):
            if i >= 32:
                break
            
            # Normalize to 32-bit
            value = value & 0xFFFFFFFF
            
            # Update stored value
            self.register_values[i] = value
            
            # Update hex display
            hex_str = f"0x{value:08X}"
            self.register_labels[i]['hex'].config(text=hex_str)
            
            # Update decimal display (unsigned)
            self.register_labels[i]['decimal'].config(text=str(value))
            
            # Signed value removed to save space (can be calculated from decimal if needed)
            
            # Highlight changed registers (optional - could add change detection)
    
    def clear_registers(self):
        """Clear all registers to zero."""
        for i in range(32):
            self.register_labels[i]['hex'].config(text="0x00000000")
            self.register_labels[i]['decimal'].config(text="0")
            self.register_values[i] = 0
