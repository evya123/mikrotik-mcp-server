"""
Tests for MikroTik Logs Client

This module tests the logs client functionality including log retrieval,
filtering, and specialized log type methods.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.mcp_mikrotik.logs.client import MikroTikLogsClient
from src.mcp_mikrotik.logs.models import GetLogsArgs


class TestMikroTikLogsClient:
    """Test cases for MikroTikLogsClient."""
    
    @pytest.fixture
    def client(self):
        """Create a logs client instance for testing."""
        config = {
            "host": "192.168.1.1",
            "username": "admin",
            "password": "test_password",
            "port": 443,
            "useSSL": True
        }
        return MikroTikLogsClient(config)
    
    @pytest.fixture
    def sample_logs(self):
        """Sample log entries for testing."""
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
    
    @pytest.mark.asyncio
    async def test_get_logs_basic(self, client, sample_logs):
        """Test basic log retrieval without options."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_logs()
            assert result == sample_logs
    
    @pytest.mark.asyncio
    async def test_get_logs_with_count_only(self, client):
        """Test log retrieval with countOnly option."""
        with patch.object(client, '_make_request', return_value="150"):
            result = await client.get_logs({"countOnly": True})
            assert result == 150
    
    @pytest.mark.asyncio
    async def test_get_logs_with_filtering(self, client, sample_logs):
        """Test log retrieval with client-side filtering."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_logs({"where": 'topics~"system"'})
            # Should return logs with "system" in topics
            assert len(result) == 2
            assert all("system" in log["topics"] for log in result)
    
    @pytest.mark.asyncio
    async def test_get_logs_with_max_logs_limit(self, client, sample_logs):
        """Test log retrieval with max_logs limit."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_logs(max_logs=2)
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_debug_logs(self, client, sample_logs):
        """Test debug logs retrieval."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_debug_logs()
            # Should return only logs with "debug" in topics
            # Since our sample doesn't have debug logs, this should return empty
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_error_logs(self, client, sample_logs):
        """Test error logs retrieval."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_error_logs()
            # Should return only logs with "error" in topics
            # Since our sample doesn't have error logs, this should return empty
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_warning_logs(self, client, sample_logs):
        """Test warning logs retrieval."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_warning_logs()
            # Should return only logs with "warning" in topics
            # Should return 1 log with warning in topics
            assert len(result) == 1
            assert "warning" in result[0]["topics"]
    
    @pytest.mark.asyncio
    async def test_get_info_logs(self, client, sample_logs):
        """Test info logs retrieval."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_info_logs()
            # Should return only logs with "info" in topics
            # Should return 2 logs with info in topics
            assert len(result) == 2
            assert all("info" in log["topics"] for log in result)
    
    @pytest.mark.asyncio
    async def test_get_logs_from_buffer(self, client, sample_logs):
        """Test logs retrieval from specific buffer."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_logs_from_buffer("main")
            # Should call get_logs with buffer filter
            assert result == sample_logs
    
    @pytest.mark.asyncio
    async def test_get_logs_with_extra_info(self, client, sample_logs):
        """Test logs retrieval with extra info."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.get_logs_with_extra_info()
            # Should call get_logs with withExtraInfo option
            assert result == sample_logs
    
    @pytest.mark.asyncio
    async def test_find_logs(self, client, sample_logs):
        """Test find_logs method."""
        with patch.object(client, '_make_request', return_value=sample_logs):
            result = await client.find_logs('topics~"system"')
            # Should return only logs with "system" in topics
            # Should return 2 logs with system in topics
            assert len(result) == 2
            assert all("system" in log["topics"] for log in result)
    
    def test_build_logs_request_body(self, client):
        """Test request body building for logs API calls."""
        options = {
            "brief": True,
            "countOnly": False,
            "where": 'topics~"system"'
        }
        request_body = client._build_logs_request_body(options)
        
        assert request_body["brief"] is True
        assert request_body["count-only"] is False
        # where parameter should not be in request body (handled client-side)
        assert "where" not in request_body
    
    def test_handle_count_only_response_string(self, client):
        """Test handling of count-only response as string."""
        result = client._handle_count_only_response("150")
        assert result == 150
    
    def test_handle_count_only_response_integer(self, client):
        """Test handling of count-only response as integer."""
        result = client._handle_count_only_response(150)
        assert result == 150
    
    def test_handle_count_only_response_invalid(self, client):
        """Test handling of invalid count-only response."""
        result = client._handle_count_only_response("invalid")
        assert result == 0
    
    def test_extract_log_entries_list(self, client, sample_logs):
        """Test extraction of log entries from list response."""
        result = client._extract_log_entries(sample_logs)
        assert result == sample_logs
    
    def test_extract_log_entries_dict_with_ret(self, client, sample_logs):
        """Test extraction of log entries from dict with 'ret' key."""
        response = {"ret": sample_logs}
        result = client._extract_log_entries(response)
        assert result == sample_logs
    
    def test_extract_log_entries_dict_without_ret(self, client):
        """Test extraction of log entries from dict without 'ret' key."""
        response = {"other": "data"}
        result = client._extract_log_entries(response)
        assert result == []
    
    def test_extract_log_entries_unexpected_type(self, client):
        """Test extraction of log entries from unexpected response type."""
        response = "unexpected"
        result = client._extract_log_entries(response)
        assert result == []
    
    def test_filter_logs_no_filter(self, client, sample_logs):
        """Test log filtering with no filter condition."""
        result = client._filter_logs(sample_logs, "")
        assert result == sample_logs
    
    def test_filter_logs_topics_contains(self, client, sample_logs):
        """Test log filtering with topics contains condition."""
        result = client._filter_logs(sample_logs, 'topics~"system"')
        assert len(result) == 2
        assert all("system" in log["topics"] for log in result)
    
    def test_filter_logs_message_contains(self, client, sample_logs):
        """Test log filtering with message contains condition."""
        result = client._filter_logs(sample_logs, 'message~"DHCP"')
        assert len(result) == 1
        assert "DHCP" in result[0]["message"]
    
    def test_filter_logs_multiple_conditions_and(self, client, sample_logs):
        """Test log filtering with multiple AND conditions."""
        result = client._filter_logs(sample_logs, 'topics~"system" and message~"started"')
        assert len(result) == 1
        assert "system" in result[0]["topics"]
        assert "started" in result[0]["message"]
    
    def test_filter_logs_multiple_conditions_or(self, client, sample_logs):
        """Test log filtering with multiple OR conditions."""
        result = client._filter_logs(sample_logs, 'topics~"system" or topics~"dhcp"')
        assert len(result) == 3  # All logs should match
    
    def test_filter_logs_case_insensitive(self, client, sample_logs):
        """Test log filtering with case-insensitive condition."""
        result = client._filter_logs(sample_logs, 'topics~i"SYSTEM"')
        assert len(result) == 2
        assert all("system" in log["topics"].lower() for log in result)
    
    def test_filter_logs_equality_operator(self, client, sample_logs):
        """Test log filtering with equality operator."""
        result = client._filter_logs(sample_logs, 'topics="system,info"')
        assert len(result) == 1
        assert result[0]["topics"] == "system,info"
    
    def test_filter_logs_invalid_syntax(self, client, sample_logs):
        """Test log filtering with invalid syntax (should return all logs)."""
        result = client._filter_logs(sample_logs, 'invalid~syntax')
        assert result == sample_logs
    
    def test_check_condition_topics_contains(self, client):
        """Test condition checking for topics contains."""
        log = {"topics": "system,info", "message": "test"}
        result = client._check_condition(log, 'topics~"system"')
        assert result is True
    
    def test_check_condition_message_contains(self, client):
        """Test condition checking for message contains."""
        log = {"topics": "system,info", "message": "test message"}
        result = client._check_condition(log, 'message~"test"')
        assert result is True
    
    def test_check_condition_topics_equals(self, client):
        """Test condition checking for topics equality."""
        log = {"topics": "system,info", "message": "test"}
        result = client._check_condition(log, 'topics="system,info"')
        assert result is True
    
    def test_check_condition_message_equals(self, client):
        """Test condition checking for message equality."""
        log = {"topics": "system,info", "message": "test message"}
        result = client._check_condition(log, 'message="test message"')
        assert result is True
    
    def test_check_condition_case_insensitive(self, client):
        """Test condition checking for case-insensitive contains."""
        log = {"topics": "SYSTEM,INFO", "message": "TEST"}
        result = client._check_condition(log, 'topics~i"system"')
        assert result is True
    
    def test_check_condition_or_operator(self, client):
        """Test condition checking with OR operator."""
        log = {"topics": "system,info", "message": "test"}
        # OR conditions are now handled at the _filter_logs level, not in _check_condition
        # This should return False since the condition contains "or" which is not a valid single condition
        result = client._check_condition(log, 'topics~"dhcp" or topics~"system"')
        assert result is False
    
    def test_check_condition_unknown_condition(self, client):
        """Test condition checking with unknown condition (should return True)."""
        log = {"topics": "system,info", "message": "test"}
        result = client._check_condition(log, 'unknown~"value"')
        assert result is True
    
    def test_check_condition_missing_field(self, client):
        """Test condition checking with missing field."""
        log = {"message": "test"}  # Missing topics field
        result = client._check_condition(log, 'topics~"system"')
        assert result is False
