"""
Tests for MikroTik DHCP Client

This module contains tests for the MikroTik DHCP management functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock
from src.mcp_mikrotik.dhcp.client import MikroTikDHCPClient
from src.mcp_mikrotik.dhcp.models import MikroTikDHCPServer, MikroTikDHCPLease, GetDHCPServersArgs


@pytest.fixture
def dhcp_client():
    """Create a MikroTik DHCP client for testing."""
    config = {
        "host": "192.168.88.1",
        "username": "admin",
        "password": "password",
        "port": 443,
        "useSSL": True
    }
    return MikroTikDHCPClient(config)


@pytest.fixture
def sample_dhcp_servers():
    """Sample DHCP servers data for testing."""
    return [
        {
            "name": "main-pool",
            "interface": "ether2",
            "address_pool": "lan-pool",
            "lease_time": "3d",
            "disabled": False,
            "authoritative": True,
            "comment": "Main LAN DHCP Server"
        },
        {
            "name": "guest-pool",
            "interface": "ether3",
            "address_pool": "guest-pool",
            "lease_time": "1h",
            "disabled": False,
            "authoritative": True,
            "comment": "Guest Network DHCP Server"
        }
    ]


@pytest.fixture
def sample_dhcp_leases():
    """Sample DHCP leases data for testing."""
    return [
        {
            "address": "192.168.88.100",
            "mac_address": "00:0C:29:XX:XX:XX",
            "client_id": "client1",
            "host_name": "laptop-01",
            "active_address": "192.168.88.100",
            "active_mac_address": "00:0C:29:XX:XX:XX",
            "active_server": "main-pool",
            "expires_after": "2d",
            "comment": "Laptop User"
        },
        {
            "address": "192.168.88.101",
            "mac_address": "00:0C:29:YY:YY:YY",
            "client_id": "client2",
            "host_name": "desktop-01",
            "active_address": "192.168.88.101",
            "active_mac_address": "00:0C:29:YY:YY:YY",
            "active_server": "main-pool",
            "expires_after": "2d",
            "comment": "Desktop User"
        }
    ]


class TestMikroTikDHCPClient:
    """Test cases for MikroTik DHCP client."""
    
    @pytest.mark.asyncio
    async def test_get_dhcp_servers_success(self, dhcp_client, sample_dhcp_servers):
        """Test successful DHCP servers retrieval."""
        with patch.object(dhcp_client, '_make_request', return_value=sample_dhcp_servers):
            result = await dhcp_client.get_dhcp_servers()
            
            assert result == sample_dhcp_servers
            assert len(result) == 2
            assert result[0]["name"] == "main-pool"
            assert result[1]["name"] == "guest-pool"
    
    @pytest.mark.asyncio
    async def test_get_dhcp_servers_with_options(self, dhcp_client, sample_dhcp_servers):
        """Test DHCP servers retrieval with filtering options."""
        options = GetDHCPServersArgs(name="main-pool", disabled=False)
        
        with patch.object(dhcp_client, '_make_request', return_value=sample_dhcp_servers):
            with patch.object(dhcp_client, '_build_dhcp_servers_request_body') as mock_builder:
                mock_builder.return_value = {"name": "main-pool"}
                result = await dhcp_client.get_dhcp_servers(options)
                
                assert result == sample_dhcp_servers
                # Verify options were passed to request builder
                mock_builder.assert_called_once_with(options)
    
    @pytest.mark.asyncio
    async def test_get_dhcp_servers_dict_response(self, dhcp_client, sample_dhcp_servers):
        """Test handling of dict response with 'ret' key."""
        response = {"ret": sample_dhcp_servers}
        
        with patch.object(dhcp_client, '_make_request', return_value=response):
            result = await dhcp_client.get_dhcp_servers()
            
            assert result == sample_dhcp_servers
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_dhcp_servers_unexpected_response(self, dhcp_client):
        """Test handling of unexpected response format."""
        response = "unexpected"
        
        with patch.object(dhcp_client, '_make_request', return_value=response):
            with patch.object(dhcp_client, '_log_warning') as mock_warning:
                result = await dhcp_client.get_dhcp_servers()
                
                assert result == []
                mock_warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dhcp_servers_request_error(self, dhcp_client):
        """Test handling of request errors."""
        with patch.object(dhcp_client, '_make_request', side_effect=Exception("Connection error")):
            with patch.object(dhcp_client, '_log_error') as mock_error:
                with pytest.raises(Exception):
                    await dhcp_client.get_dhcp_servers()
                
                mock_error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dhcp_leases_success(self, dhcp_client, sample_dhcp_leases):
        """Test successful DHCP leases retrieval."""
        with patch.object(dhcp_client, '_make_request', return_value=sample_dhcp_leases):
            result = await dhcp_client.get_dhcp_leases()
            
            assert result == sample_dhcp_leases
            assert len(result) == 2
            assert result[0]["address"] == "192.168.88.100"
            assert result[1]["address"] == "192.168.88.101"
    
    @pytest.mark.asyncio
    async def test_get_dhcp_networks_success(self, dhcp_client):
        """Test successful DHCP networks retrieval."""
        sample_networks = [
            {"name": "lan-network", "address": "192.168.88.0/24", "gateway": "192.168.88.1"},
            {"name": "guest-network", "address": "192.168.89.0/24", "gateway": "192.168.89.1"}
        ]
        
        with patch.object(dhcp_client, '_make_request', return_value=sample_networks):
            result = await dhcp_client.get_dhcp_networks()
            
            assert result == sample_networks
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_dhcp_clients_success(self, dhcp_client):
        """Test successful DHCP clients retrieval."""
        sample_clients = [
            {"interface": "ether2", "disabled": False, "comment": "LAN DHCP Client"},
            {"interface": "ether3", "disabled": False, "comment": "Guest DHCP Client"}
        ]
        
        with patch.object(dhcp_client, '_make_request', return_value=sample_clients):
            result = await dhcp_client.get_dhcp_clients()
            
            assert result == sample_clients
            assert len(result) == 2
    
    def test_build_dhcp_servers_request_body(self, dhcp_client):
        """Test building request body for DHCP servers API calls."""
        options = GetDHCPServersArgs(
            name="main-pool",
            interface="ether2",
            address_pool="lan-pool",
            disabled=False,
            comment="Test Server"
        )
        
        result = dhcp_client._build_dhcp_servers_request_body(options)
        
        expected = {
            "name": "main-pool",
            "interface": "ether2",
            "address-pool": "lan-pool",
            "disabled": False,
            "comment": "Test Server"
        }
        
        assert result == expected
    
    def test_build_dhcp_servers_request_body_partial(self, dhcp_client):
        """Test building request body with partial options."""
        options = GetDHCPServersArgs(name="main-pool")
        
        result = dhcp_client._build_dhcp_servers_request_body(options)
        
        expected = {"name": "main-pool"}
        assert result == expected
    
    def test_build_dhcp_servers_request_body_none_values(self, dhcp_client):
        """Test building request body with None values."""
        options = GetDHCPServersArgs(
            name="main-pool",
            interface=None,
            address_pool=None
        )
        
        result = dhcp_client._build_dhcp_servers_request_body(options)
        
        expected = {"name": "main-pool"}
        assert result == expected
    
    def test_build_dhcp_servers_request_body_empty(self, dhcp_client):
        """Test building request body with empty options."""
        options = GetDHCPServersArgs()
        
        result = dhcp_client._build_dhcp_servers_request_body(options)
        
        assert result == {}
