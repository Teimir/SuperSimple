"""
Error handling and display for the GUI.
"""

import re
from typing import Optional, Tuple


class ErrorHandler:
    """Handles parsing and display of errors from different stages."""
    
    def __init__(self, editor, output_panel):
        self.editor = editor
        self.output_panel = output_panel
    
    def handle_preprocessing_error(self, error):
        """Handle preprocessing errors."""
        error_msg = str(error)
        self.output_panel.append_error(f"Preprocessing error: {error_msg}")
        
        # Try to extract line number if available
        line_num = self._extract_line_number(error_msg)
        if line_num:
            self.highlight_error(line_num, error_msg)
    
    def handle_lexer_error(self, error_token):
        """Handle lexer errors."""
        error_msg = error_token.value if hasattr(error_token, 'value') else str(error_token)
        self.output_panel.append_error(f"Lexer error: {error_msg}")
        
        # Lexer errors might have position information
        line_num = self._extract_line_number(error_msg)
        if line_num:
            self.highlight_error(line_num, error_msg)
    
    def handle_syntax_error(self, error):
        """Handle syntax errors from parser."""
        error_msg = str(error)
        self.output_panel.append_error(f"Syntax error: {error_msg}")
        
        # Try to extract line number
        line_num = self._extract_line_number(error_msg)
        if line_num:
            self.highlight_error(line_num, error_msg)
    
    def handle_runtime_error(self, error):
        """Handle runtime errors."""
        error_msg = str(error)
        self.output_panel.append_error(f"Runtime error: {error_msg}")
        
        # Try to extract line number
        line_num = self._extract_line_number(error_msg)
        if line_num:
            self.highlight_error(line_num, error_msg)
    
    def handle_general_error(self, error):
        """Handle general/unexpected errors."""
        error_msg = str(error)
        self.output_panel.append_error(f"Error: {error_msg}")
        
        # Try to extract line number
        line_num = self._extract_line_number(error_msg)
        if line_num:
            self.highlight_error(line_num, error_msg)
    
    def _extract_line_number(self, error_msg: str) -> Optional[int]:
        """Extract line number from error message."""
        # Common patterns:
        # "line X: ..."
        # "at line X"
        # "Line X"
        # "line X, column Y"
        
        patterns = [
            r'line\s+(\d+)',
            r'Line\s+(\d+)',
            r'at\s+line\s+(\d+)',
            r'line\s+(\d+),\s+column',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_msg, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def highlight_error(self, line_num: int, error_msg: str):
        """Highlight error line in editor."""
        if line_num > 0:
            self.editor.clear_error_highlights()
            self.editor.highlight_error_line(line_num)
            self.editor.goto_line(line_num)
    
    def clear_errors(self):
        """Clear all error highlights."""
        self.editor.clear_error_highlights()
        self.output_panel.clear_errors()
