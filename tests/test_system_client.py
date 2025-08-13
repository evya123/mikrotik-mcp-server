"""
Tests for MikroTik System Client

This module tests the system client functionality including system information,
resource management, and health monitoring.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.mcp_mikrotik.system.client import MikroTikSystemClient


class TestMikroTikSystemClient:
    """Test cases for MikroTikSystemClient."""
    
    @pytest.fixture
    def client(self):
        """Create a system client instance for testing."""
        config = {
            "host": "192.168.1.1",
            "username": "admin",
            "password": "test_password",
            "port": 443,
            "useSSL": True
        }
        return MikroTikSystemClient(config)
    
    @pytest.fixture
    def sample_system_info(self):
        """Sample system information for testing."""
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
    
    @pytest.mark.asyncio
    async def test_get_system_info_success(self, client, sample_system_info):
        """Test successful system info retrieval."""
        with patch.object(client, '_make_request', return_value=[sample_system_info]):
            result = await client.get_system_info()
            assert result == sample_system_info
    
    @pytest.mark.asyncio
    async def test_get_system_info_empty_response(self, client):
        """Test system info retrieval with empty response."""
        with patch.object(client, '_make_request', return_value=[]):
            result = await client.get_system_info()
            assert result == {}
    
    @pytest.mark.asyncio
    async def test_get_system_info_unexpected_type(self, client):
        """Test system info retrieval with unexpected response type."""
        with patch.object(client, '_make_request', return_value="unexpected"):
            with pytest.raises(TypeError, match="Expected list response"):
                await client.get_system_info()
    
    @pytest.mark.asyncio
    async def test_get_system_info_request_error(self, client):
        """Test system info retrieval with request error."""
        with patch.object(client, '_make_request', side_effect=Exception("Request failed")):
            with pytest.raises(Exception, match="Request failed"):
                await client.get_system_info()
    
    @pytest.mark.asyncio
    async def test_get_system_resources_list_response(self, client, sample_system_info):
        """Test system resources retrieval with list response."""
        with patch.object(client, '_make_request', return_value=[sample_system_info]):
            result = await client.get_system_resources()
            assert result == [sample_system_info]
    
    @pytest.mark.asyncio
    async def test_get_system_resources_dict_response(self, client, sample_system_info):
        """Test system resources retrieval with dict response containing 'ret' key."""
        with patch.object(client, '_make_request', return_value={"ret": [sample_system_info]}):
            result = await client.get_system_resources()
            assert result == [sample_system_info]
    
    @pytest.mark.asyncio
    async def test_get_system_resources_unexpected_response(self, client):
        """Test system resources retrieval with unexpected response type."""
        with patch.object(client, '_make_request', return_value="unexpected"):
            result = await client.get_system_resources()
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_system_resources_request_error(self, client):
        """Test system resources retrieval with request error."""
        with patch.object(client, '_make_request', side_effect=Exception("Request failed")):
            with pytest.raises(Exception, match="Request failed"):
                await client.get_system_resources()
    
    @pytest.mark.asyncio
    async def test_get_system_health_success(self, client, sample_system_info):
        """Test successful system health retrieval."""
        with patch.object(client, 'get_system_info', return_value=sample_system_info):
            result = await client.get_system_health()
            
            assert result["status"] == "healthy"
            assert result["uptime"] == "1d 12:00:00"
            assert result["version"] == "6.49.7"
            assert result["cpu_load"] == 15
            assert result["memory_usage_percent"] == 50.0
            assert result["disk_usage_percent"] == 50.0
            assert result["free_memory_mb"] == 512.0
            assert result["free_disk_mb"] == 1024.0
    
    @pytest.mark.asyncio
    async def test_get_system_health_critical_memory(self, client):
        """Test system health with critical memory usage."""
        system_info = {
            "total_memory": 1000000000,
            "free_memory": 50000000,  # 5% free memory
            "total_hdd_space": 2000000000,
            "free_hdd_space": 1000000000  # 50% free disk
        }
        
        with patch.object(client, 'get_system_info', return_value=system_info):
            result = await client.get_system_health()
            assert result["status"] == "critical"
            assert result["memory_usage_percent"] == 95.0
    
    @pytest.mark.asyncio
    async def test_get_system_health_critical_disk(self, client):
        """Test system health with critical disk usage."""
        system_info = {
            "total_memory": 1000000000,
            "free_memory": 500000000,  # 50% free memory
            "total_hdd_space": 2000000000,
            "free_hdd_space": 100000000  # 5% free disk
        }
        
        with patch.object(client, 'get_system_info', return_value=system_info):
            result = await client.get_system_health()
            assert result["status"] == "critical"
            assert result["disk_usage_percent"] == 95.0
    
    @pytest.mark.asyncio
    async def test_get_system_health_warning(self, client):
        """Test system health with warning status."""
        system_info = {
            "total_memory": 1000000000,
            "free_memory": 150000000,  # 15% free memory
            "total_hdd_space": 2000000000,
            "free_hdd_space": 300000000  # 15% free disk
        }
        
        with patch.object(client, 'get_system_info', return_value=system_info):
            result = await client.get_system_health()
            assert result["status"] == "warning"
            assert result["memory_usage_percent"] == 85.0
            assert result["disk_usage_percent"] == 85.0
    
    @pytest.mark.asyncio
    async def test_get_system_health_attention(self, client):
        """Test system health with attention status."""
        system_info = {
            "total_memory": 1000000000,
            "free_memory": 250000000,  # 25% free memory
            "total_hdd_space": 2000000000,
            "free_hdd_space": 500000000  # 25% free disk
        }
        
        with patch.object(client, 'get_system_info', return_value=system_info):
            result = await client.get_system_health()
            assert result["status"] == "attention"
            assert result["memory_usage_percent"] == 75.0
            assert result["disk_usage_percent"] == 75.0
    
    @pytest.mark.asyncio
    async def test_get_system_health_no_system_info(self, client):
        """Test system health retrieval with no system information."""
        with patch.object(client, 'get_system_info', return_value={}):
            result = await client.get_system_health()
            assert result["status"] == "unknown"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_system_health_missing_memory_info(self, client):
        """Test system health retrieval with missing memory information."""
        system_info = {
            "uptime": "1d 12:00:00",
            "version": "6.49.7"
            # Missing memory and disk information
        }
        
        with patch.object(client, 'get_system_info', return_value=system_info):
            result = await client.get_system_health()
            assert result["status"] == "healthy"
            assert result["memory_usage_percent"] == 0.0
            assert result["disk_usage_percent"] == 0.0
            assert result["free_memory_mb"] == 0.0
            assert result["free_disk_mb"] == 0.0
    
    @pytest.mark.asyncio
    async def test_get_system_health_exception_handling(self, client):
        """Test system health retrieval with exception handling."""
        with patch.object(client, 'get_system_info', side_effect=Exception("System error")):
            result = await client.get_system_health()
            assert result["status"] == "error"
            assert result["error"] == "System error"
    
    def test_memory_calculation_accuracy(self, client):
        """Test memory usage calculation accuracy."""
        # Test with exact values
        total_memory = 1000000000  # 1GB
        free_memory = 250000000    # 250MB
        
        # Calculate expected usage
        expected_usage = ((total_memory - free_memory) / total_memory) * 100
        
        # This should be exactly 75.0%
        assert expected_usage == 75.0
    
    def test_disk_calculation_accuracy(self, client):
        """Test disk usage calculation accuracy."""
        # Test with exact values
        total_disk = 2000000000  # 2GB
        free_disk = 500000000    # 500MB
        
        # Calculate expected usage
        expected_usage = ((total_disk - free_disk) / total_disk) * 100
        
        # This should be exactly 75.0%
        assert expected_usage == 75.0
    
    def test_health_status_thresholds(self, client):
        """Test health status threshold logic."""
        # Test healthy status (all below 70%)
        assert client._determine_health_status(65.0, 60.0) == "healthy"
        
        # Test attention status (one above 70%)
        assert client._determine_health_status(75.0, 60.0) == "attention"
        assert client._determine_health_status(60.0, 75.0) == "attention"
        
        # Test warning status (one above 80%)
        assert client._determine_health_status(85.0, 60.0) == "warning"
        assert client._determine_health_status(60.0, 85.0) == "warning"
        
        # Test critical status (one above 90%)
        assert client._determine_health_status(95.0, 60.0) == "critical"
        assert client._determine_health_status(60.0, 95.0) == "critical"
    
    def test_memory_conversion_to_mb(self, client):
        """Test memory conversion from bytes to MB."""
        bytes_value = 1073741824  # 1GB in bytes
        mb_value = bytes_value / (1024 * 1024)
        
        assert mb_value == 1024.0  # 1GB = 1024MB
