"""
Entry point for running the package as a module.
"""

import sys
from .main import main
from .auto_test import main as auto_test_main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto-test":
        # Remove the auto-test argument and pass the rest to auto_test_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        auto_test_main()
    else:
        main()