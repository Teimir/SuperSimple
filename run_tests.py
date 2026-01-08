"""
Test runner for all unit tests.
"""

import unittest
import sys

def run_tests():
    """Run all unit tests."""
    # Discover and load all test modules
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    suite.addTests(loader.loadTestsFromName('test_lexer'))
    suite.addTests(loader.loadTestsFromName('test_parser'))
    suite.addTests(loader.loadTestsFromName('test_interpreter'))
    suite.addTests(loader.loadTestsFromName('test_preprocessor'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
