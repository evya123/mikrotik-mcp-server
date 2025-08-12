#!/usr/bin/env python3
"""
Simple launcher for the MikroTik MCP Server

This script can be run from anywhere to start the MCP server.
Usage: python3 run_server.py
"""
from server.server import main

if __name__ == "__main__":
    main()
