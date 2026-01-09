"""
GUI entry point for the SC Language Interpreter.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """Main entry point for GUI application."""
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    main()
