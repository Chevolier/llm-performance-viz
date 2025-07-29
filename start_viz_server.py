#!/usr/bin/env python3
"""
Startup script for the LLM Performance Visualization Server.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_test_tool.viz_server import main

if __name__ == "__main__":
    main()