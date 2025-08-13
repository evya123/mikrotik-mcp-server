"""
Pytest configuration and fixtures for MikroTik MCP tests.
"""
import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.mcp_mikrotik import MikroTikClient
from src.mcp_mikrotik.models import MikroTikConfig


@pytest.fixture
def mock_config():
    """Provide a mock MikroTik configuration for testing."""
    return {
        "host": "192.168.1.1",
        "username": "admin",
        "password": "test_password",
        "port": 443,
        "useSSL": True
    }


@pytest.fixture
def mock_mikrotik_client(mock_config):
    """Provide a mock MikroTik client for testing."""
    client = MikroTikClient(mock_config)
    
    # Mock the base client methods
    client._make_request = Mock()
    client.test_connection = AsyncMock(return_value=True)
    
    # Mock specialized client methods
    client.logs.get_logs = AsyncMock()
    client.logs.get_debug_logs = AsyncMock()
    client.logs.get_error_logs = AsyncMock()
    client.logs.get_warning_logs = AsyncMock()
    client.logs.get_info_logs = AsyncMock()
    client.logs.get_logs_from_buffer = AsyncMock()
    client.logs.get_logs_with_extra_info = AsyncMock()
    
    client.system.get_system_info = AsyncMock()
    client.system.get_system_resources = AsyncMock()
    client.system.get_system_health = AsyncMock()
    
    client.ip.get_ip_addresses = AsyncMock()
    client.ip.get_ip_routes = AsyncMock()
    client.ip.get_ip_pools = AsyncMock()
    client.ip.get_network_summary = AsyncMock()
    
    return client


@pytest.fixture
def sample_log_entries():
    """Provide sample log entries for testing."""
    return [
        {
            "time": "2024-01-01 12:00:00",
            "topics": "system,info",
            "message": "System started",
            "level": "info"
        },
        {
            "time": "2024-01-01 12:01:00",
            "topics": "dhcp,info",
            "message": "DHCP server started",
            "level": "info"
        },
        {
            "time": "2024-01-01 12:02:00",
            "topics": "system,warning",
            "message": "High memory usage",
            "level": "warning"
        }
    ]


@pytest.fixture
def sample_system_info():
    """Provide sample system information for testing."""
    return {
        "uptime": "1d 12:00:00",
        "version": "6.49.7",
        "board_name": "RB450G",
        "cpu_count": 4,
        "cpu_frequency": 600,
        "cpu_load": 15,
        "free_hdd_space": 1073741824,
        "total_hdd_space": 2147483648,
        "free_memory": 536870912,
        "total_memory": 1073741824,
        "architecture_name": "mipsbe",
        "platform": "MikroTik"
    }


@pytest.fixture
def sample_ip_addresses():
    """Provide sample IP addresses for testing."""
    return [
        {
            "address": "192.168.1.1/24",
            "network": "192.168.1.0",
            "interface": "ether1",
            "comment": "LAN interface"
        },
        {
            "address": "10.0.0.1/24",
            "network": "10.0.0.0",
            "interface": "ether2",
            "comment": "WAN interface"
        }
    ]


@pytest.fixture
def sample_ip_routes():
    """Provide sample IP routes for testing."""
    return [
        {
            "dst_address": "0.0.0.0/0",
            "gateway": "10.0.0.1",
            "distance": 1,
            "comment": "Default route"
        },
        {
            "dst_address": "192.168.1.0/24",
            "gateway": "0.0.0.0",
            "distance": 0,
            "comment": "Local network"
        }
    ]


@pytest.fixture
def sample_ip_pools():
    """Provide sample IP pools for testing."""
    return [
        {
            "name": "lan_pool",
            "ranges": "192.168.1.10-192.168.1.100",
            "comment": "LAN DHCP pool"
        },
        {
            "name": "guest_pool",
            "ranges": "192.168.2.10-192.168.2.50",
            "comment": "Guest network pool"
        }
    ]
