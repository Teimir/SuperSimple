"""
Preprocessor for handling #include directives.

This module processes source files before lexing and parsing. It:
- Expands #include directives by inserting file contents
- Handles nested includes recursively
- Detects circular include dependencies
- Resolves file paths (relative and absolute)
- Adds debug comments to track included files

The preprocessor is the first stage in the compilation pipeline.
"""

import os
from typing import List, Set


class PreprocessingError(Exception):
    """Error during preprocessing."""
    pass


class Preprocessor:
    """Handles preprocessing of source files, including #include directives."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
        self.included_files: Set[str] = set()
    
    def resolve_path(self, filename: str, current_dir: str) -> str:
        """Resolve include file path relative to current directory."""
        # If filename is absolute, use it directly
        if os.path.isabs(filename):
            return filename
        
        # Try relative to current file's directory first
        if current_dir:
            path = os.path.join(current_dir, filename)
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # Try relative to base directory
        path = os.path.join(self.base_dir, filename)
        if os.path.exists(path):
            return os.path.abspath(path)
        
        # If still not found, try as-is (might be in current working directory)
        if os.path.exists(filename):
            return os.path.abspath(filename)
        
        raise PreprocessingError(f"Include file not found: {filename}")
    
    def process_file(self, filepath: str, included_from: str = None) -> str:
        """Process a source file, handling includes recursively."""
        # Resolve absolute path
        abs_path = os.path.abspath(filepath)
        
        # Check for circular includes
        if abs_path in self.included_files:
            raise PreprocessingError(f"Circular include detected: {abs_path}")
        
        # Check if file exists
        if not os.path.exists(abs_path):
            raise PreprocessingError(f"File not found: {abs_path}")
        
        # Read the file
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise PreprocessingError(f"Error reading file {abs_path}: {e}")
        
        # Add to included set
        self.included_files.add(abs_path)
        
        # Get directory for relative includes
        current_dir = os.path.dirname(abs_path)
        
        # Process includes in the content
        return self.process_content(content, current_dir)
    
    def process_content(self, content: str, current_dir: str = None) -> str:
        """Process source content, expanding #include directives."""
        lines = content.split('\n')
        result_lines = []
        
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Check for #include directive
            if stripped.startswith('#include'):
                # Parse #include "filename" or #include <filename>
                include_match = self.parse_include(stripped)
                if include_match:
                    filename = include_match
                    try:
                        # Resolve the include file path
                        include_path = self.resolve_path(filename, current_dir)
                        
                        # Process the included file
                        included_content = self.process_file(include_path, current_dir)
                        
                        # Add the included content
                        result_lines.append(f"// Included from: {filename}")
                        result_lines.extend(included_content.split('\n'))
                        result_lines.append(f"// End include: {filename}")
                        continue
                    except PreprocessingError as e:
                        raise PreprocessingError(f"Include error at line {line_num}: {e}")
                else:
                    raise PreprocessingError(
                        f"Invalid #include directive at line {line_num}: {stripped}"
                    )
            
            # Regular line, add as-is
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def parse_include(self, line: str) -> str:
        """Parse #include directive and return filename."""
        # Remove #include
        rest = line[8:].strip()
        
        # Check for quoted filename: #include "filename"
        if rest.startswith('"') and rest.endswith('"'):
            return rest[1:-1]
        
        # Check for angle brackets: #include <filename>
        if rest.startswith('<') and rest.endswith('>'):
            return rest[1:-1]
        
        return None
    
    def preprocess(self, filepath: str) -> str:
        """Main preprocessing entry point."""
        # Reset included files set for new preprocessing
        self.included_files.clear()
        
        # Set base directory to the directory of the main file
        self.base_dir = os.path.dirname(os.path.abspath(filepath))
        
        return self.process_file(filepath)
