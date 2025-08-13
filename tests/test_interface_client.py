"""
Tests for MikroTik Interface Client

This module contains tests for the MikroTik interface management functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock
from src.mcp_mikrotik.interface.client import MikroTikInterfaceClient
from src.mcp_mikrotik.interface.models import MikroTikInterface, GetInterfacesArgs


@pytest.fixture
def interface_client():
    """Create a MikroTik interface client for testing."""
    config = {
        "host": "192.168.88.1",
        "username": "admin",
        "password": "password",
        "port": 443,
        "useSSL": True
    }
    return MikroTikInterfaceClient(config)


@pytest.fixture
def sample_interfaces():
    """Sample interface data for testing."""
    return [
        {
            "name": "ether1",
            "type": "ether",
            "mtu": 1500,
            "mac_address": "00:0C:29:XX:XX:XX",
            "disabled": False,
            "running": True,
            "comment": "WAN Interface"
        },
        {
            "name": "ether2",
            "type": "ether",
            "mtu": 1500,
            "mac_address": "00:0C:29:XX:XX:XX",
            "disabled": False,
            "running": True,
            "comment": "LAN Interface"
        }
    ]


class TestMikroTikInterfaceClient:
    """Test cases for MikroTik interface client."""
    
    @pytest.mark.asyncio
    async def test_get_interfaces_success(self, interface_client, sample_interfaces):
        """Test successful interface retrieval."""
        with patch.object(interface_client, '_make_request', return_value=sample_interfaces):
            result = await interface_client.get_interfaces()
            
            assert result == sample_interfaces
            assert len(result) == 2
            assert result[0]["name"] == "ether1"
            assert result[1]["name"] == "ether2"
    
    @pytest.mark.asyncio
    async def test_get_interfaces_with_options(self, interface_client, sample_interfaces):
        """Test interface retrieval with filtering options."""
        options = GetInterfacesArgs(name="ether1", disabled=False)
        
        with patch.object(interface_client, '_make_request', return_value=sample_interfaces):
            with patch.object(interface_client, '_build_interfaces_request_body') as mock_builder:
                mock_builder.return_value = {"name": "ether1"}
                result = await interface_client.get_interfaces(options)
                
                assert result == sample_interfaces
                # Verify options were passed to request builder
                mock_builder.assert_called_once_with(options)
    
    @pytest.mark.asyncio
    async def test_get_interfaces_dict_response(self, interface_client, sample_interfaces):
        """Test handling of dict response with 'ret' key."""
        response = {"ret": sample_interfaces}
        
        with patch.object(interface_client, '_make_request', return_value=response):
            result = await interface_client.get_interfaces()
            
            assert result == sample_interfaces
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_interfaces_unexpected_response(self, interface_client):
        """Test handling of unexpected response format."""
        response = "unexpected"
        
        with patch.object(interface_client, '_make_request', return_value=response):
            with patch.object(interface_client, '_log_warning') as mock_warning:
                result = await interface_client.get_interfaces()
                
                assert result == []
                mock_warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_interfaces_request_error(self, interface_client):
        """Test handling of request errors."""
        with patch.object(interface_client, '_make_request', side_effect=Exception("Connection error")):
            with patch.object(interface_client, '_log_error') as mock_error:
                with pytest.raises(Exception):
                    await interface_client.get_interfaces()
                
                mock_error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_ethernet_interfaces_success(self, interface_client, sample_interfaces):
        """Test successful Ethernet interface retrieval."""
        with patch.object(interface_client, '_make_request', return_value=sample_interfaces):
            result = await interface_client.get_ethernet_interfaces()
            
            assert result == sample_interfaces
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_wireless_interfaces_success(self, interface_client, sample_interfaces):
        """Test successful wireless interface retrieval."""
        with patch.object(interface_client, '_make_request', return_value=sample_interfaces):
            result = await interface_client.get_wireless_interfaces()
            
            assert result == sample_interfaces
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_bridge_interfaces_success(self, interface_client, sample_interfaces):
        """Test successful bridge interface retrieval."""
        with patch.object(interface_client, '_make_request', return_value=sample_interfaces):
            result = await interface_client.get_bridge_interfaces()
            
            assert result == sample_interfaces
            assert len(result) == 2
    
    def test_build_interfaces_request_body(self, interface_client):
        """Test building request body for interface API calls."""
        options = GetInterfacesArgs(
            name="ether1",
            type="ether",
            disabled=False,
            running=True,
            comment="Test Interface"
        )
        
        result = interface_client._build_interfaces_request_body(options)
        
        expected = {
            "name": "ether1",
            "type": "ether",
            "disabled": False,
            "running": True,
            "comment": "Test Interface"
        }
        
        assert result == expected
    
    def test_build_interfaces_request_body_partial(self, interface_client):
        """Test building request body with partial options."""
        options = GetInterfacesArgs(name="ether1")
        
        result = interface_client._build_interfaces_request_body(options)
        
        expected = {"name": "ether1"}
        assert result == expected
    
    def test_build_interfaces_request_body_none_values(self, interface_client):
        """Test building request body with None values."""
        options = GetInterfacesArgs(
            name="ether1",
            type=None,
            disabled=None
        )
        
        result = interface_client._build_interfaces_request_body(options)
        
        expected = {"name": "ether1"}
        assert result == expected
    
    def test_build_interfaces_request_body_empty(self, interface_client):
        """Test building request body with empty options."""
        options = GetInterfacesArgs()
        
        result = interface_client._build_interfaces_request_body(options)
        
        assert result == {}
