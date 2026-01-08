"""
Unit tests for the preprocessor.
"""

import unittest
import os
import tempfile
import shutil
from preprocessor import Preprocessor, PreprocessingError


class TestPreprocessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.preprocessor = Preprocessor(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def write_file(self, filename, content):
        """Helper to write a test file."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_simple_include(self):
        """Test simple include directive."""
        # Create utility file
        utils_content = "function add(a, b) { return a + b; }"
        self.write_file("utils.sc", utils_content)
        
        # Create main file with include
        main_content = '#include "utils.sc"\nfunction main() { return add(1, 2); }'
        main_file = self.write_file("main.sc", main_content)
        
        # Process
        result = self.preprocessor.preprocess(main_file)
        
        # Should contain both files
        self.assertIn("function add", result)
        self.assertIn("function main", result)
    
    def test_nested_include(self):
        """Test nested includes."""
        # Create nested files
        self.write_file("base.sc", "function base() { return 1; }")
        self.write_file("middle.sc", '#include "base.sc"\nfunction middle() { return 2; }')
        main_content = '#include "middle.sc"\nfunction main() { return 3; }'
        main_file = self.write_file("main.sc", main_content)
        
        # Process
        result = self.preprocessor.preprocess(main_file)
        
        # Should contain all functions
        self.assertIn("function base", result)
        self.assertIn("function middle", result)
        self.assertIn("function main", result)
    
    def test_circular_include(self):
        """Test that circular includes are detected."""
        # Create circular includes
        self.write_file("a.sc", '#include "b.sc"\nfunction a() { return 1; }')
        self.write_file("b.sc", '#include "a.sc"\nfunction b() { return 2; }')
        main_file = self.write_file("main.sc", '#include "a.sc"\nfunction main() { return 0; }')
        
        # Should raise error
        with self.assertRaises(PreprocessingError) as context:
            self.preprocessor.preprocess(main_file)
        
        self.assertIn("Circular include", str(context.exception))
    
    def test_include_not_found(self):
        """Test that missing include file raises error."""
        main_content = '#include "nonexistent.sc"\nfunction main() { return 0; }'
        main_file = self.write_file("main.sc", main_content)
        
        with self.assertRaises(PreprocessingError) as context:
            self.preprocessor.preprocess(main_file)
        
        self.assertIn("not found", str(context.exception))
    
    def test_include_with_angle_brackets(self):
        """Test include with angle brackets."""
        self.write_file("header.sc", "function test() { return 42; }")
        main_content = '#include <header.sc>\nfunction main() { return 0; }'
        main_file = self.write_file("main.sc", main_content)
        
        result = self.preprocessor.preprocess(main_file)
        self.assertIn("function test", result)
    
    def test_invalid_include_directive(self):
        """Test that invalid include directive raises error."""
        main_content = '#include\nfunction main() { return 0; }'
        main_file = self.write_file("main.sc", main_content)
        
        with self.assertRaises(PreprocessingError) as context:
            self.preprocessor.preprocess(main_file)
        
        self.assertIn("Invalid #include", str(context.exception))
    
    def test_include_path_resolution(self):
        """Test that relative paths are resolved correctly."""
        # Create subdirectory
        subdir = os.path.join(self.test_dir, "lib")
        os.makedirs(subdir)
        
        # Create file in subdirectory
        lib_file = os.path.join(subdir, "library.sc")
        with open(lib_file, 'w') as f:
            f.write("function lib_func() { return 100; }")
        
        # Create main file that includes from subdirectory
        main_content = '#include "lib/library.sc"\nfunction main() { return 0; }'
        main_file = self.write_file("main.sc", main_content)
        
        result = self.preprocessor.preprocess(main_file)
        self.assertIn("function lib_func", result)
    
    def test_multiple_includes(self):
        """Test multiple includes in one file."""
        self.write_file("a.sc", "function a() { return 1; }")
        self.write_file("b.sc", "function b() { return 2; }")
        main_content = '#include "a.sc"\n#include "b.sc"\nfunction main() { return 0; }'
        main_file = self.write_file("main.sc", main_content)
        
        result = self.preprocessor.preprocess(main_file)
        self.assertIn("function a", result)
        self.assertIn("function b", result)
        self.assertIn("function main", result)


if __name__ == '__main__':
    unittest.main()
