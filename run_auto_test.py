#!/usr/bin/env python3
"""
Convenience script to run automated vLLM testing.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_test_tool.auto_test import AutoTestRunner

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_auto_test.py <config_path> [output_dir]")
        print("Example: python run_auto_test.py model_deploy_scripts/vllm-v0.9.2/g6e.4xlarge/config.yaml")
        sys.exit(1)
    
    config_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "test_results"
    
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    print(f"Starting automated test with config: {config_path}")
    print(f"Results will be saved to: {output_dir}")
    
    runner = AutoTestRunner(config_path, output_dir)
    runner.run_all_tests()

if __name__ == "__main__":
    main()