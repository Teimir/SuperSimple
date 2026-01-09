"""
File management functionality for the GUI.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


class FileManager:
    """Manages file operations for the editor."""
    
    def __init__(self, editor, main_window):
        self.editor = editor
        self.main_window = main_window
        self.current_file = None
        self._initial_content = ""
    
    def new_file(self):
        """Create a new file."""
        if self._check_save_changes():
            self.editor.clear()
            self.current_file = None
            self._initial_content = ""
            self._update_title()
            return True
        return False
    
    def open_file(self):
        """Open a file."""
        if not self._check_save_changes():
            return False
        
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("SC Files", "*.sc"),
                ("All Files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.set_text(content)
                self.current_file = file_path
                self._initial_content = content
                self._update_title()
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
                return False
        return False
    
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            return self._save_to_file(self.current_file)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        """Save the file with a new name."""
        file_path = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".sc",
            filetypes=[
                ("SC Files", "*.sc"),
                ("All Files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if file_path:
            return self._save_to_file(file_path)
        return False
    
    def _save_to_file(self, file_path):
        """Save content to a file."""
        try:
            content = self.editor.get_text()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = file_path
            self._initial_content = content
            self.editor.set_modified(False)
            self._update_title()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
            return False
    
    def _check_save_changes(self):
        """Check if there are unsaved changes and prompt to save."""
        if self.editor.is_modified():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?"
            )
            
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                return self.save_file()
            else:  # No
                return True
        return True
    
    def _update_title(self):
        """Update the window title."""
        if hasattr(self.main_window, 'update_title'):
            self.main_window.update_title()
    
    def get_current_file(self):
        """Get the current file path."""
        return self.current_file
    
    def has_unsaved_changes(self):
        """Check if there are unsaved changes."""
        if not self.editor.is_modified():
            return False
        
        current_content = self.editor.get_text()
        return current_content != self._initial_content
    
    def reload_file(self):
        """Reload the current file from disk."""
        if self.current_file and os.path.exists(self.current_file):
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.set_text(content)
                self._initial_content = content
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reload file:\n{str(e)}")
                return False
        return False
