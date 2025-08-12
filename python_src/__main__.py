#!/usr/bin/env python3
"""
MikroTik MCP Server Main Entry Point

This module provides the main entry point for running the MikroTik MCP server.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from python_src.server.server import main

if __name__ == "__main__":
    main()
