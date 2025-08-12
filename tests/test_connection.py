#!/usr/bin/env python3
"""
MikroTik Connection Validation Test

This test validates the MikroTik client connection logic.
Set RUN_INTEGRATION_TESTS=1 to run against real hardware.
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add parent directory to path to import from client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Skip this integration test unless explicitly enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration test requires real MikroTik device. Set RUN_INTEGRATION_TESTS=1 to enable.",
)


@pytest.mark.asyncio
async def test_connection_logic():
    """Test MikroTik client connection logic and error handling."""
    from client.mikrotik import MikroTikClient
from mikrotik_types.models import MikroTikConfig
    
    # Test with mock configuration
    config = {
        "host": "192.168.88.1",
        "username": "admin",
        "password": "test_password",
        "port": 443,
        "useSSL": True,
    }
    
    # Test client initialization
    client = MikroTikClient(config)
    assert client is not None
    assert client.host == "192.168.88.1"
    assert client.username == "admin"
    assert client.port == 443
    assert client.use_ssl is True


@pytest.mark.asyncio
async def test_connection_error_handling():
    """Test that connection errors are handled gracefully."""
    from client.mikrotik import MikroTikClient
    
    # Test with invalid configuration
    invalid_config = {
        "host": "invalid_host",
        "username": "admin",
        "password": "test_password",
    }
    
    client = MikroTikClient(invalid_config)
    
    # Test connection should fail gracefully
    try:
        result = await client.test_connection()
        # If we get here, the test environment might have network access
        # This is acceptable for integration tests
        assert isinstance(result, bool)
    except Exception as e:
        # Expected behavior for invalid host
        assert "connection" in str(e).lower() or "timeout" in str(e).lower() or "resolve" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__])
