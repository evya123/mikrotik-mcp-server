#!/usr/bin/env python3
"""
Test connection to MikroTik device.

This script tests the connection to a MikroTik device and retrieves system information and logs.
"""
import os
import sys
import json
import asyncio
import pytest
from dotenv import load_dotenv

# Add parent directory to path to import from client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client.mikrotik import MikroTikClient
from types.models import MikroTikConfig


# Skip this integration test unless explicitly enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration test requires a real MikroTik device. Set RUN_INTEGRATION_TESTS=1 to enable.",
)


@pytest.mark.asyncio
async def test_connection():
    """Test connection to MikroTik device."""
    # Load environment variables from .env file
    load_dotenv()
    
    config = {
        "host": os.environ.get("MIKROTIK_HOST", "192.168.88.1"),
        "username": os.environ.get("MIKROTIK_USERNAME", "admin"),
        "password": os.environ.get("MIKROTIK_PASSWORD", ""),
        "port": int(os.environ.get("MIKROTIK_PORT")) if os.environ.get("MIKROTIK_PORT") else None,
        "useSSL": os.environ.get("MIKROTIK_USE_SSL") == "true",
    }
    
    if not config["password"]:
        print("Error: MIKROTIK_PASSWORD environment variable is required")
        sys.exit(1)
    
    print("Testing MikroTik connection...")
    print(f"Host: {config['host']}")
    print(f"Username: {config['username']}")
    print(f"Port: {config['port'] or (443 if config['useSSL'] else 80)}")
    print(f"SSL: {config['useSSL']}")
    
    try:
        client = MikroTikClient(config)
        
        # Test connection
        is_connected = await client.test_connection()
        if is_connected:
            print("✅ Connection successful!")
            
            # Get system info
            system_info = await client.get_system_info()
            print("System Information:", json.dumps(system_info, indent=2))
            
            # Get recent logs
            logs = await client.get_logs({"brief": True})
            print(f"Recent logs ({len(logs)} entries):")
            for i, log in enumerate(logs):
                print(f"{i + 1}. [{log.get('time', '')}] {log.get('topics', '')}: {log.get('message', '')}")
        else:
            print("❌ Connection failed!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_connection())
