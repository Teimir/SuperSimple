"""
Output panel for displaying program execution results.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime


class OutputPanel(ttk.Frame):
    """Panel for displaying program output and messages."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Create notebook for tabs (optional - can be simplified to single text area)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Output tab
        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Output")
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#ffffff',
            state=tk.NORMAL
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Messages tab
        self.messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messages_frame, text="Messages")
        
        self.messages_text = scrolledtext.ScrolledText(
            self.messages_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            state=tk.NORMAL
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Error tab
        self.errors_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.errors_frame, text="Errors")
        
        self.errors_text = scrolledtext.ScrolledText(
            self.errors_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ff6b6b',
            state=tk.NORMAL
        )
        self.errors_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for different message types (after all text widgets are created)
        self._configure_tags()
    
    def _configure_tags(self):
        """Configure text tags for styling."""
        self.output_text.tag_config('success', foreground='#4ec9b0')
        self.output_text.tag_config('error', foreground='#f48771')
        self.output_text.tag_config('info', foreground='#569cd6')
        self.output_text.tag_config('timestamp', foreground='#808080', font=('Consolas', 9))
        
        self.messages_text.tag_config('info', foreground='#569cd6')
        self.messages_text.tag_config('success', foreground='#4ec9b0')
        self.messages_text.tag_config('timestamp', foreground='#808080', font=('Consolas', 9))
        
        self.errors_text.tag_config('error', foreground='#f48771')
        self.errors_text.tag_config('warning', foreground='#dcdcaa')
        self.errors_text.tag_config('timestamp', foreground='#808080', font=('Consolas', 9))
    
    def append_output(self, text, tag=None):
        """Append text to the output panel."""
        self.output_text.config(state=tk.NORMAL)
        if tag:
            self.output_text.insert(tk.END, text, tag)
        else:
            self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.update_idletasks()
    
    def append_message(self, text, tag='info'):
        """Append a message to the messages panel."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.messages_text.insert(tk.END, text + "\n", tag)
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.update_idletasks()
    
    def append_error(self, text, tag='error'):
        """Append an error to the errors panel."""
        if not text or text.strip() == "":
            text = "Unknown error occurred"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.errors_text.config(state=tk.NORMAL)
        self.errors_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Insert error text - handle multiline errors
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i == 0:
                self.errors_text.insert(tk.END, line, tag)
            else:
                self.errors_text.insert(tk.END, '\n' + line, tag)
        
        self.errors_text.insert(tk.END, "\n")
        self.errors_text.see(tk.END)
        self.errors_text.config(state=tk.NORMAL)
        self.errors_text.update_idletasks()
        
        # Also switch to errors tab
        self.notebook.select(self.errors_frame)
    
    def clear_output(self):
        """Clear the output panel."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state=tk.NORMAL)
    
    def clear_messages(self):
        """Clear the messages panel."""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete('1.0', tk.END)
        self.messages_text.config(state=tk.NORMAL)
    
    def clear_errors(self):
        """Clear the errors panel."""
        self.errors_text.config(state=tk.NORMAL)
        self.errors_text.delete('1.0', tk.END)
        self.errors_text.config(state=tk.NORMAL)
    
    def clear_all(self):
        """Clear all panels."""
        self.clear_output()
        self.clear_messages()
        self.clear_errors()
    
    def show_success(self, message):
        """Show a success message."""
        self.append_message(message, 'success')
        self.append_output(f"✓ {message}\n", 'success')
