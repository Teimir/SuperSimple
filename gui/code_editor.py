"""
Code editor component with syntax highlighting for .sc language.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class CodeEditor(ttk.Frame):
    """Code editor with syntax highlighting and line numbers."""
    
    # Keywords for syntax highlighting
    KEYWORDS = {
        'function', 'return', 'if', 'else', 'while', 'for', 
        'int32', 'uint32', 'void', 'break', 'continue'
    }
    
    # Operators
    OPERATORS = {
        '+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=',
        '&&', '||', '&', '|', '^', '<<', '>>', '=', '!', '~'
    }
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Create paned window for line numbers and editor
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers frame
        self.line_numbers_frame = ttk.Frame(self.paned)
        self.paned.add(self.line_numbers_frame, weight=0)
        
        self.line_numbers = tk.Text(
            self.line_numbers_frame,
            width=4,
            padx=5,
            pady=5,
            state=tk.DISABLED,
            bg='#f0f0f0',
            fg='#666',
            font=('Consolas', 10),
            wrap=tk.NONE,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main editor
        self.editor = scrolledtext.ScrolledText(
            self.paned,
            wrap=tk.NONE,
            font=('Consolas', 10),
            padx=5,
            pady=5,
            undo=True,
            maxundo=50
        )
        self.paned.add(self.editor, weight=1)
        
        # Configure tags for syntax highlighting
        self._configure_tags()
        
        # Bind events
        self.editor.bind('<KeyRelease>', self._on_key_release)
        self.editor.bind('<Button-1>', self._on_click)
        self.editor.bind('<MouseWheel>', self._on_mousewheel)
        self.editor.bind('<Key>', self._on_key)
        
        # Track changes
        self._modified = False
        self.editor.bind('<<Modified>>', self._on_modified)
        
        # Initial line numbers
        self._update_line_numbers()
    
    def _configure_tags(self):
        """Configure syntax highlighting tags."""
        # Keywords
        self.editor.tag_config('keyword', foreground='#0000FF', font=('Consolas', 10, 'bold'))
        # Types
        self.editor.tag_config('type', foreground='#008080', font=('Consolas', 10, 'bold'))
        # Strings
        self.editor.tag_config('string', foreground='#008000')
        # Comments
        self.editor.tag_config('comment', foreground='#808080', font=('Consolas', 10, 'italic'))
        # Numbers
        self.editor.tag_config('number', foreground='#FF0000')
        # Operators
        self.editor.tag_config('operator', foreground='#800080')
        # Error line
        self.editor.tag_config('error_line', background='#FFE6E6')
    
    def _on_modified(self, event=None):
        """Handle text modification event."""
        if self.editor.edit_modified():
            self._modified = True
            self.editor.edit_modified(False)
            if hasattr(self.parent, 'on_text_modified'):
                self.parent.on_text_modified()
    
    def _on_key_release(self, event=None):
        """Handle key release for syntax highlighting."""
        self._highlight_syntax()
        self._update_line_numbers()
    
    def _on_click(self, event=None):
        """Handle click to sync line numbers."""
        self._update_line_numbers()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.delta:
            self.editor.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:
                self.editor.yview_scroll(-1, "units")
            elif event.num == 5:
                self.editor.yview_scroll(1, "units")
        self._update_line_numbers()
        return "break"
    
    def _on_key(self, event):
        """Handle key press for line number updates."""
        if event.keysym in ['Up', 'Down', 'Page_Up', 'Page_Down']:
            self.after_idle(self._update_line_numbers)
        return None
    
    def _update_line_numbers(self):
        """Update line numbers display."""
        # Get current line count
        content = self.editor.get('1.0', tk.END)
        line_count = content.count('\n')
        
        # Update line numbers
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        
        self.line_numbers.config(state=tk.DISABLED)
        
        # Sync scrolling
        self._sync_scroll()
    
    def _sync_scroll(self):
        """Sync editor and line numbers scrolling."""
        yview = self.editor.yview()
        self.line_numbers.yview_moveto(yview[0])
        
        # Bind scroll events
        def on_scroll(*args):
            self.line_numbers.yview_moveto(self.editor.yview()[0])
        
        self.editor.bind('<MouseWheel>', lambda e: self.after_idle(on_scroll))
        self.editor.bind('<Button-4>', lambda e: self.after_idle(on_scroll))
        self.editor.bind('<Button-5>', lambda e: self.after_idle(on_scroll))
    
    def _highlight_syntax(self):
        """Apply syntax highlighting to the code."""
        # Remove existing tags (except error_line)
        for tag in ['keyword', 'type', 'string', 'comment', 'number', 'operator']:
            self.editor.tag_remove(tag, '1.0', tk.END)
        
        content = self.editor.get('1.0', tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            start_pos = f"{line_num}.0"
            
            # Highlight comments
            comment_pos = line.find('//')
            if comment_pos != -1:
                end_pos = f"{line_num}.{len(line)}"
                self.editor.tag_add('comment', f"{line_num}.{comment_pos}", end_pos)
            
            # Highlight strings (simple approach - look for quotes)
            # This is simplified - full string parsing would be more complex
            
            # Highlight keywords and types
            words = line.split()
            col = 0
            for word in words:
                # Skip if inside comment
                if '//' in line and line.find('//') < line.find(word, col):
                    break
                
                word_start = line.find(word, col)
                if word_start != -1:
                    word_end = word_start + len(word)
                    col = word_end
                    
                    # Check if it's a keyword
                    if word in self.KEYWORDS:
                        if word in ['int32', 'uint32']:
                            self.editor.tag_add('type', f"{line_num}.{word_start}", f"{line_num}.{word_end}")
                        else:
                            self.editor.tag_add('keyword', f"{line_num}.{word_start}", f"{line_num}.{word_end}")
                    
                    # Check if it's a number
                    if word.isdigit() or (word.startswith('-') and word[1:].isdigit()):
                        self.editor.tag_add('number', f"{line_num}.{word_start}", f"{line_num}.{word_end}")
            
            # Highlight operators
            for op in sorted(self.OPERATORS, key=len, reverse=True):
                start = 0
                while True:
                    pos = line.find(op, start)
                    if pos == -1:
                        break
                    # Skip if inside comment
                    if '//' in line and line.find('//') < pos:
                        break
                    self.editor.tag_add('operator', f"{line_num}.{pos}", f"{line_num}.{pos + len(op)}")
                    start = pos + 1
    
    def get_text(self):
        """Get the current text content."""
        return self.editor.get('1.0', tk.END + '-1c')
    
    def set_text(self, text):
        """Set the text content."""
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', text)
        self._highlight_syntax()
        self._update_line_numbers()
        self._modified = False
    
    def clear(self):
        """Clear the editor."""
        self.editor.delete('1.0', tk.END)
        self._update_line_numbers()
        self._modified = False
    
    def is_modified(self):
        """Check if the text has been modified."""
        return self._modified
    
    def set_modified(self, modified):
        """Set the modified flag."""
        self._modified = modified
    
    def highlight_error_line(self, line_num):
        """Highlight a line with an error."""
        if line_num > 0:
            self.editor.tag_add('error_line', f"{line_num}.0", f"{line_num}.end")
    
    def clear_error_highlights(self):
        """Clear all error highlights."""
        self.editor.tag_remove('error_line', '1.0', tk.END)
    
    def goto_line(self, line_num):
        """Move cursor to specified line."""
        if line_num > 0:
            self.editor.mark_set(tk.INSERT, f"{line_num}.0")
            self.editor.see(f"{line_num}.0")
