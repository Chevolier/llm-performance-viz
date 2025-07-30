#!/usr/bin/env python3
"""
Startup script for the LLM Performance Visualization Server.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn

def main():
    parser = argparse.ArgumentParser(description="LLM Performance Visualization Server")
    parser.add_argument("--port", "-p", type=int, default=8000, 
                       help="Port to run the server on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                       help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--root-path", type=str, default="",
                       help="Root path for deployment under a subdomain (e.g., /viz)")
    
    args = parser.parse_args()
    
    # Set environment variable for root path so the FastAPI app can use it
    if args.root_path:
        os.environ['ROOT_PATH'] = args.root_path.rstrip('/')
    
    # Import app after setting environment variable
    from llm_test_tool.viz_server import app
    
    print(f"Starting LLM Performance Visualization Server...")
    if args.root_path:
        print(f"Root path: {args.root_path}")
        print(f"Access the visualization at: http://localhost:{args.port}{args.root_path}")
    else:
        print(f"Access the visualization at: http://localhost:{args.port}")
    
    uvicorn.run(app, host=args.host, port=args.port, root_path=args.root_path)

if __name__ == "__main__":
    main()