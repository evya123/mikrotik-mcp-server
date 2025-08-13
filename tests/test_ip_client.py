"""
Tests for MikroTik IP Client

This module tests the IP client functionality including IP address management,
routing, and network configuration.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.mcp_mikrotik.ip.client import MikroTikIPClient
from src.mcp_mikrotik.ip.models import GetIPAddressesArgs, GetIPRoutesArgs


class TestMikroTikIPClient:
    """Test cases for MikroTikIPClient."""
    
    @pytest.fixture
    def client(self):
        """Create an IP client instance for testing."""
        config = {
            "host": "192.168.1.1",
            "username": "admin",
            "password": "test_password",
            "port": 443,
            "useSSL": True
        }
        return MikroTikIPClient(config)
    
    @pytest.fixture
    def sample_ip_addresses(self):
        """Sample IP addresses for testing."""
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
    def sample_ip_routes(self):
        """Sample IP routes for testing."""
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
    def sample_ip_pools(self):
        """Sample IP pools for testing."""
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
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_no_options(self, client, sample_ip_addresses):
        """Test IP addresses retrieval without options."""
        with patch.object(client, '_make_request', return_value=sample_ip_addresses):
            result = await client.get_ip_addresses()
            assert result == sample_ip_addresses
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_with_interface_filter(self, client, sample_ip_addresses):
        """Test IP addresses retrieval with interface filter."""
        with patch.object(client, '_make_request', return_value=sample_ip_addresses):
            result = await client.get_ip_addresses({"interface": "ether1"})
            assert result == sample_ip_addresses
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_with_network_filter(self, client, sample_ip_addresses):
        """Test IP addresses retrieval with network filter."""
        with patch.object(client, '_make_request', return_value=sample_ip_addresses):
            result = await client.get_ip_addresses({"network": "192.168.1.0"})
            assert result == sample_ip_addresses
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_dict_response(self, client, sample_ip_addresses):
        """Test IP addresses retrieval with dict response containing 'ret' key."""
        with patch.object(client, '_make_request', return_value={"ret": sample_ip_addresses}):
            result = await client.get_ip_addresses()
            assert result == sample_ip_addresses
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_unexpected_response(self, client):
        """Test IP addresses retrieval with unexpected response type."""
        with patch.object(client, '_make_request', return_value="unexpected"):
            result = await client.get_ip_addresses()
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_request_error(self, client):
        """Test IP addresses retrieval with request error."""
        with patch.object(client, '_make_request', side_effect=Exception("Request failed")):
            with pytest.raises(Exception, match="Request failed"):
                await client.get_ip_addresses()
    
    @pytest.mark.asyncio
    async def test_get_ip_routes_no_options(self, client, sample_ip_routes):
        """Test IP routes retrieval without options."""
        with patch.object(client, '_make_request', return_value=sample_ip_routes):
            result = await client.get_ip_routes()
            assert result == sample_ip_routes
    
    @pytest.mark.asyncio
    async def test_get_ip_routes_with_destination_filter(self, client, sample_ip_routes):
        """Test IP routes retrieval with destination address filter."""
        with patch.object(client, '_make_request', return_value=sample_ip_routes):
            result = await client.get_ip_routes({"dst_address": "0.0.0.0/0"})
            assert result == sample_ip_routes
    
    @pytest.mark.asyncio
    async def test_get_ip_routes_with_gateway_filter(self, client, sample_ip_routes):
        """Test IP routes retrieval with gateway filter."""
        with patch.object(client, '_make_request', return_value=sample_ip_routes):
            result = await client.get_ip_routes({"gateway": "10.0.0.1"})
            assert result == sample_ip_routes
    
    @pytest.mark.asyncio
    async def test_get_ip_routes_dict_response(self, client, sample_ip_routes):
        """Test IP routes retrieval with dict response containing 'ret' key."""
        with patch.object(client, '_make_request', return_value={"ret": sample_ip_routes}):
            result = await client.get_ip_routes()
            assert result == sample_ip_routes
    
    @pytest.mark.asyncio
    async def test_get_ip_routes_unexpected_response(self, client):
        """Test IP routes retrieval with unexpected response type."""
        with patch.object(client, '_make_request', return_value="unexpected"):
            result = await client.get_ip_routes()
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_ip_routes_request_error(self, client):
        """Test IP routes retrieval with request error."""
        with patch.object(client, '_make_request', side_effect=Exception("Request failed")):
            with pytest.raises(Exception, match="Request failed"):
                await client.get_ip_routes()
    
    @pytest.mark.asyncio
    async def test_get_ip_pools_success(self, client, sample_ip_pools):
        """Test IP pools retrieval."""
        with patch.object(client, '_make_request', return_value=sample_ip_pools):
            result = await client.get_ip_pools()
            assert result == sample_ip_pools
    
    @pytest.mark.asyncio
    async def test_get_ip_pools_dict_response(self, client, sample_ip_pools):
        """Test IP pools retrieval with dict response containing 'ret' key."""
        with patch.object(client, '_make_request', return_value={"ret": sample_ip_pools}):
            result = await client.get_ip_pools()
            assert result == sample_ip_pools
    
    @pytest.mark.asyncio
    async def test_get_ip_pools_unexpected_response(self, client):
        """Test IP pools retrieval with unexpected response type."""
        with patch.object(client, '_make_request', return_value="unexpected"):
            result = await client.get_ip_pools()
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_ip_pools_request_error(self, client):
        """Test IP pools retrieval with request error."""
        with patch.object(client, '_make_request', side_effect=Exception("Request failed")):
            with pytest.raises(Exception, match="Request failed"):
                await client.get_ip_pools()
    
    @pytest.mark.asyncio
    async def test_get_network_summary_success(self, client, sample_ip_addresses, sample_ip_routes, sample_ip_pools):
        """Test network summary retrieval."""
        with patch.object(client, 'get_ip_addresses', return_value=sample_ip_addresses), \
             patch.object(client, 'get_ip_routes', return_value=sample_ip_routes), \
             patch.object(client, 'get_ip_pools', return_value=sample_ip_pools):
            
            result = await client.get_network_summary()
            
            assert result["ip_addresses_count"] == 2
            assert result["ip_routes_count"] == 2
            assert result["ip_pools_count"] == 2
            assert "ether1" in result["interfaces"]
            assert "ether2" in result["interfaces"]
            assert "192.168.1.0" in result["networks"]
            assert "10.0.0.0" in result["networks"]
            assert "10.0.0.1" in result["gateways"]
            assert "0.0.0.0" in result["gateways"]
    
    @pytest.mark.asyncio
    async def test_get_network_summary_with_exceptions(self, client):
        """Test network summary retrieval with some API calls failing."""
        with patch.object(client, 'get_ip_addresses', side_effect=Exception("Addresses failed")), \
             patch.object(client, 'get_ip_routes', return_value=[]), \
             patch.object(client, 'get_ip_pools', return_value=[]):
            
            result = await client.get_network_summary()
            
            assert result["ip_addresses_count"] == 0
            assert result["ip_routes_count"] == 0
            assert result["ip_pools_count"] == 0
            assert result["interfaces"] == []
            assert result["networks"] == []
            assert result["gateways"] == []
    
    @pytest.mark.asyncio
    async def test_get_network_summary_all_exceptions(self, client):
        """Test network summary retrieval with all API calls failing."""
        with patch.object(client, 'get_ip_addresses', side_effect=Exception("Addresses failed")), \
             patch.object(client, 'get_ip_routes', side_effect=Exception("Routes failed")), \
             patch.object(client, 'get_ip_pools', side_effect=Exception("Pools failed")):
            
            result = await client.get_network_summary()
            
            # The current implementation handles exceptions gracefully and returns empty results
            assert result["ip_addresses_count"] == 0
            assert result["ip_routes_count"] == 0
            assert result["ip_pools_count"] == 0
            assert result["interfaces"] == []
            assert result["networks"] == []
            assert result["gateways"] == []
    
    def test_build_ip_addresses_request_body(self, client):
        """Test request body building for IP addresses API calls."""
        options = {
            "interface": "ether1",
            "network": "192.168.1.0",
            "comment": "LAN interface",
            "disabled": False
        }
        request_body = client._build_ip_addresses_request_body(options)
        
        assert request_body["interface"] == "ether1"
        assert request_body["network"] == "192.168.1.0"
        assert request_body["comment"] == "LAN interface"
        assert request_body["disabled"] is False
    
    def test_build_ip_addresses_request_body_partial(self, client):
        """Test request body building for IP addresses with partial options."""
        options = {
            "interface": "ether1"
            # Missing other options
        }
        request_body = client._build_ip_addresses_request_body(options)
        
        assert request_body["interface"] == "ether1"
        assert len(request_body) == 1
    
    def test_build_ip_routes_request_body(self, client):
        """Test request body building for IP routes API calls."""
        options = {
            "dst_address": "0.0.0.0/0",
            "gateway": "10.0.0.1",
            "routing_mark": "main",
            "disabled": False
        }
        request_body = client._build_ip_routes_request_body(options)
        
        assert request_body["dst-address"] == "0.0.0.0/0"
        assert request_body["gateway"] == "10.0.0.1"
        assert request_body["routing-mark"] == "main"
        assert request_body["disabled"] is False
    
    def test_build_ip_routes_request_body_partial(self, client):
        """Test request body building for IP routes with partial options."""
        options = {
            "dst_address": "0.0.0.0/0"
            # Missing other options
        }
        request_body = client._build_ip_routes_request_body(options)
        
        assert request_body["dst-address"] == "0.0.0.0/0"
        assert len(request_body) == 1
    
    def test_build_ip_addresses_request_body_none_values(self, client):
        """Test request body building for IP addresses with None values."""
        options = {
            "interface": "ether1",
            "network": None,
            "comment": None,
            "disabled": None
        }
        request_body = client._build_ip_addresses_request_body(options)
        
        assert request_body["interface"] == "ether1"
        assert "network" not in request_body
        assert "comment" not in request_body
        assert "disabled" not in request_body
    
    def test_build_ip_routes_request_body_none_values(self, client):
        """Test request body building for IP routes with None values."""
        options = {
            "dst_address": "0.0.0.0/0",
            "gateway": None,
            "routing_mark": None,
            "disabled": None
        }
        request_body = client._build_ip_routes_request_body(options)
        
        assert request_body["dst-address"] == "0.0.0.0/0"
        assert "gateway" not in request_body
        assert "routing-mark" not in request_body
        assert "disabled" not in request_body
