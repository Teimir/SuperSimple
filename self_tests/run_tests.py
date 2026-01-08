"""
Test runner for all unit tests.
"""

import unittest
import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Run all unit tests."""
    # Discover and load all test modules
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules from self_tests directory
    suite.addTests(loader.loadTestsFromName('self_tests.test_lexer'))
    suite.addTests(loader.loadTestsFromName('self_tests.test_parser'))
    suite.addTests(loader.loadTestsFromName('self_tests.test_interpreter'))
    suite.addTests(loader.loadTestsFromName('self_tests.test_preprocessor'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
