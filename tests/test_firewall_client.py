"""
Tests for MikroTik Firewall Client

This module contains tests for the MikroTik firewall management functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock
from src.mcp_mikrotik.firewall.client import MikroTikFirewallClient
from src.mcp_mikrotik.firewall.models import MikroTikFirewallRule, GetFirewallRulesArgs


@pytest.fixture
def firewall_client():
    """Create a MikroTik firewall client for testing."""
    config = {
        "host": "192.168.88.1",
        "username": "admin",
        "password": "password",
        "port": 443,
        "useSSL": True
    }
    return MikroTikFirewallClient(config)


@pytest.fixture
def sample_firewall_rules():
    """Sample firewall rules data for testing."""
    return [
        {
            "chain": "input",
            "action": "accept",
            "src_address": "192.168.88.0/24",
            "dst_address": "",
            "protocol": "tcp",
            "src_port": "",
            "dst_port": "22",
            "comment": "SSH Access",
            "disabled": False,
            "log": True,
            "log_prefix": "SSH"
        },
        {
            "chain": "forward",
            "action": "accept",
            "src_address": "192.168.88.0/24",
            "dst_address": "0.0.0.0/0",
            "protocol": "tcp",
            "src_port": "",
            "dst_port": "80",
            "comment": "HTTP Access",
            "disabled": False,
            "log": False,
            "log_prefix": ""
        }
    ]


class TestMikroTikFirewallClient:
    """Test cases for MikroTik firewall client."""
    
    @pytest.mark.asyncio
    async def test_get_firewall_rules_success(self, firewall_client, sample_firewall_rules):
        """Test successful firewall rules retrieval."""
        with patch.object(firewall_client, '_make_request', return_value=sample_firewall_rules):
            result = await firewall_client.get_firewall_rules()
            
            assert result == sample_firewall_rules
            assert len(result) == 2
            assert result[0]["chain"] == "input"
            assert result[1]["chain"] == "forward"
    
    @pytest.mark.asyncio
    async def test_get_firewall_rules_with_options(self, firewall_client, sample_firewall_rules):
        """Test firewall rules retrieval with filtering options."""
        options = GetFirewallRulesArgs(chain="input", action="accept")
        
        with patch.object(firewall_client, '_make_request', return_value=sample_firewall_rules):
            with patch.object(firewall_client, '_build_firewall_rules_request_body') as mock_builder:
                mock_builder.return_value = {"chain": "input"}
                result = await firewall_client.get_firewall_rules(options)
                
                assert result == sample_firewall_rules
                # Verify options were passed to request builder
                mock_builder.assert_called_once_with(options)
    
    @pytest.mark.asyncio
    async def test_get_firewall_rules_dict_response(self, firewall_client, sample_firewall_rules):
        """Test handling of dict response with 'ret' key."""
        response = {"ret": sample_firewall_rules}
        
        with patch.object(firewall_client, '_make_request', return_value=response):
            result = await firewall_client.get_firewall_rules()
            
            assert result == sample_firewall_rules
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_firewall_rules_unexpected_response(self, firewall_client):
        """Test handling of unexpected response format."""
        response = "unexpected"
        
        with patch.object(firewall_client, '_make_request', return_value=response):
            with patch.object(firewall_client, '_log_warning') as mock_warning:
                result = await firewall_client.get_firewall_rules()
                
                assert result == []
                mock_warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_firewall_rules_request_error(self, firewall_client):
        """Test handling of request errors."""
        with patch.object(firewall_client, '_make_request', side_effect=Exception("Connection error")):
            with patch.object(firewall_client, '_log_error') as mock_error:
                with pytest.raises(Exception):
                    await firewall_client.get_firewall_rules()
                
                mock_error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_nat_rules_success(self, firewall_client, sample_firewall_rules):
        """Test successful NAT rules retrieval."""
        with patch.object(firewall_client, '_make_request', return_value=sample_firewall_rules):
            result = await firewall_client.get_nat_rules()
            
            assert result == sample_firewall_rules
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_mangle_rules_success(self, firewall_client, sample_firewall_rules):
        """Test successful mangle rules retrieval."""
        with patch.object(firewall_client, '_make_request', return_value=sample_firewall_rules):
            result = await firewall_client.get_mangle_rules()
            
            assert result == sample_firewall_rules
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_address_lists_success(self, firewall_client):
        """Test successful address lists retrieval."""
        sample_address_lists = [
            {"name": "trusted", "address": "192.168.88.0/24", "comment": "Trusted Network"},
            {"name": "blocked", "address": "10.0.0.0/8", "comment": "Blocked Network"}
        ]
        
        with patch.object(firewall_client, '_make_request', return_value=sample_address_lists):
            result = await firewall_client.get_address_lists()
            
            assert result == sample_address_lists
            assert len(result) == 2
    
    def test_build_firewall_rules_request_body(self, firewall_client):
        """Test building request body for firewall rules API calls."""
        options = GetFirewallRulesArgs(
            chain="input",
            action="accept",
            src_address="192.168.88.0/24",
            protocol="tcp",
            disabled=False,
            comment="Test Rule"
        )
        
        result = firewall_client._build_firewall_rules_request_body(options)
        
        expected = {
            "chain": "input",
            "action": "accept",
            "src-address": "192.168.88.0/24",
            "protocol": "tcp",
            "disabled": False,
            "comment": "Test Rule"
        }
        
        assert result == expected
    
    def test_build_firewall_rules_request_body_partial(self, firewall_client):
        """Test building request body with partial options."""
        options = GetFirewallRulesArgs(chain="input")
        
        result = firewall_client._build_firewall_rules_request_body(options)
        
        expected = {"chain": "input"}
        assert result == expected
    
    def test_build_firewall_rules_request_body_none_values(self, firewall_client):
        """Test building request body with None values."""
        options = GetFirewallRulesArgs(
            chain="input",
            action=None,
            src_address=None
        )
        
        result = firewall_client._build_firewall_rules_request_body(options)
        
        expected = {"chain": "input"}
        assert result == expected
    
    def test_build_firewall_rules_request_body_empty(self, firewall_client):
        """Test building request body with empty options."""
        options = GetFirewallRulesArgs()
        
        result = firewall_client._build_firewall_rules_request_body(options)
        
        assert result == {}
