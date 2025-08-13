"""
MikroTik Logs Client

This module provides a specialized client for log management operations.
It handles all log-related API calls with proper error handling and validation.
"""
import re
import json
from typing import Dict, List, Optional, Any, Union
import requests
from requests.auth import HTTPBasicAuth

from ..base import MikroTikBaseClient
from .models import (
    MikroTikLogEntry,
    GetLogsArgs,
    GetLogsByConditionArgs
)


class MikroTikLogsClient(MikroTikBaseClient):
    """
    Specialized client for MikroTik log management operations.
    
    This client provides methods for retrieving, filtering, and analyzing
    system logs from MikroTik RouterOS devices.
    """
    
    async def get_logs(
        self, 
        options: Optional[GetLogsArgs] = None, 
        max_logs: int = 1000
    ) -> Union[List[MikroTikLogEntry], int]:
        """
        Get system logs with optional filtering.
        
        This method retrieves logs from the MikroTik device and applies client-side filtering
        if a 'where' parameter is provided. The filtering is done on the client side because
        the RouterOS REST API's 'where' parameter for /log/print doesn't work as expected.
        
        Args:
            options: Options for retrieving logs
            max_logs: Maximum number of logs to retrieve (default: 1000)
                      Set to None to retrieve all logs (may impact performance)
            
        Returns:
            List of log entries or log count (if countOnly is True)
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        if options is None:
            options = {}
        
        request_body = self._build_logs_request_body(options)
        
        try:
            response = self._make_request('POST', '/log/print', request_body)
            
            # Handle countOnly response
            if options.get('countOnly'):
                return self._handle_count_only_response(response)
            
            # Process log entries
            logs = self._extract_log_entries(response)
            
            # Apply client-side filtering if where parameter is provided
            where = options.get('where')
            if where:
                logs = self._filter_logs(logs, where)
            
            # Limit the number of logs if max_logs is specified
            if max_logs is not None and len(logs) > max_logs:
                self._log_warning(f"Limiting logs to {max_logs} entries (retrieved {len(logs)})")
                logs = logs[:max_logs]
            
            return logs
            
        except (requests.RequestException, ValueError, TypeError) as e:
            self._log_error(f"Error retrieving logs: {str(e)}")
            raise
    
    async def get_debug_logs(
        self, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get debug logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of debug log entries
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"debug"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_error_logs(
        self, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get error logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of error log entries
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"error"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_warning_logs(
        self, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get warning logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of warning log entries
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"warning"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_info_logs(
        self, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get info logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of info log entries
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"info"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_logs_from_buffer(
        self, 
        buffer_name: str, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get logs from a specific buffer (for separate memory logging buffers).
        
        Args:
            buffer_name: Name of the buffer
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of log entries from the specified buffer
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            'where': f'buffer={buffer_name}',
            **options,
        }, max_logs=max_logs)
    
    async def get_logs_with_extra_info(
        self, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get logs with extra info (includes extra-info field).
        
        Note: The MikroTik RouterOS REST API may not return extra information for all logs,
        or any logs at all, depending on the device configuration. This method sets the
        'withExtraInfo' parameter, but the response may not include extra information.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of log entries with extra info (if available)
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            'withExtraInfo': True,
            **options,
        }, max_logs=max_logs)
    
    async def find_logs(
        self, 
        where: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> List[MikroTikLogEntry]:
        """
        Find logs using client-side filtering.
        
        This method now uses /log/print with client-side filtering instead of /log/find,
        as testing has shown that /log/find doesn't filter logs as expected.
        
        Args:
            where: Filter condition
            options: Additional options
            
        Returns:
            List of matching log entries
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': where
        })
    
    async def get_logs_by_condition(
        self, 
        condition: str, 
        options: Optional[Dict[str, Any]] = None, 
        max_logs: int = 1000
    ) -> List[MikroTikLogEntry]:
        """
        Get logs filtered by a specific condition.
        
        This is a convenience method that calls get_logs with a where parameter.
        
        Args:
            condition: Filter condition (e.g., 'topics~"system"', 'message~"login"')
            options: Additional options for the API call
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of filtered log entries
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            'where': condition,
            **options
        }, max_logs=max_logs)

    def _build_logs_request_body(self, options: GetLogsArgs) -> Dict[str, Any]:
        """Build the request body for log API calls."""
        request_body = {}
        
        # Map options to request body with proper API parameter names
        option_mappings = {
            'append': 'append',
            'brief': 'brief',
            'countOnly': 'count-only',
            'detail': 'detail',
            'file': 'file',
            'follow': 'follow',
            'followOnly': 'follow-only',
            'groupBy': 'group-by',
            'interval': 'interval',
            'proplist': 'proplist',
            'showIds': 'show-ids',
            'terse': 'terse',
            'withExtraInfo': 'with-extra-info',
            'withoutPaging': 'without-paging'
        }
        
        for option_key, api_key in option_mappings.items():
            if options.get(option_key) is not None:
                request_body[api_key] = options[option_key]
        
        return request_body
    
    def _handle_count_only_response(self, response: Any) -> int:
        """Handle count-only response from the API."""
        if isinstance(response, str):
            try:
                return int(response)
            except ValueError:
                self._log_warning(f"Count-only response is not a valid number: {response}")
                return 0
        elif isinstance(response, int):
            return response
        else:
            self._log_warning(f"Unexpected count-only response type: {type(response).__name__}")
            return 0
    
    def _extract_log_entries(self, response: Any) -> List[MikroTikLogEntry]:
        """Extract log entries from the API response."""
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            # Some API endpoints return a dict with a 'ret' property
            if 'ret' in response:
                return response['ret']
            else:
                self._log_note(f"Received dict response: {response}")
                return []
        else:
            self._log_warning(f"Unexpected response type: {type(response).__name__}")
            return []
    
    def _filter_logs(self, logs: List[MikroTikLogEntry], where: str) -> List[MikroTikLogEntry]:
        """
        Client-side filtering implementation for log entries.
        
        The MikroTik RouterOS REST API's 'where' parameter for /log/print doesn't work as expected,
        so we implement filtering on the client side. This method parses the filter condition and
        applies it to each log entry.
        
        Supported filter syntax:
        - Simple equality: field="value"
        - Contains: field~"value"
        - Case-insensitive contains: field~i"value"
        - Multiple conditions with AND: condition1 and condition2
        - Multiple conditions with OR: condition1 or condition2
        
        Currently supported fields:
        - topics: Filter by log topics (e.g., topics~"system")
        - message: Filter by log message content (e.g., message~"login")
        
        Examples:
        - topics~"system"
        - message~"error"
        - topics~"dhcp" and message~"assigned"
        - topics~"system" or topics~"dhcp"
        
        Args:
            logs: List of log entries to filter
            where: Filter condition string
            
        Returns:
            Filtered list of log entries
            
        Note:
            If the filter syntax is invalid or an error occurs during filtering,
            all logs will be returned and an error will be printed.
        """
        if not where:
            return logs
        
        try:
            # Handle OR conditions first, then AND conditions
            if ' or ' in where:
                # Split by OR first, then handle each OR group
                or_groups = where.split(' or ')
                filtered_logs = []
                for log in logs:
                    # A log entry must match at least one OR group
                    if any(self._check_condition(log, or_group.strip()) for or_group in or_groups):
                        filtered_logs.append(log)
                return filtered_logs
            else:
                # Split the condition by 'and' to support multiple AND conditions
                conditions = where.split(' and ')
                
                filtered_logs = []
                for log in logs:
                    # A log entry must match all conditions to be included
                    if all(self._check_condition(log, condition) for condition in conditions):
                        filtered_logs.append(log)
                
                return filtered_logs
        except Exception as e:
            self._log_error(f"Filter parsing error: {str(e)}")
            self._log_error(f"Invalid filter syntax: '{where}'. Returning all logs.")
            return logs  # Return all logs if filter parsing fails
    
    def _check_condition(self, log: MikroTikLogEntry, condition: str) -> bool:
        """
        Check if a log entry matches a specific filter condition.
        
        This method parses a single condition string and checks if the log entry matches it.
        Supports various filter syntaxes:
        - Contains (~): field~"value" - Checks if field contains value
        - Equals (=): field="value" - Checks if field equals value exactly
        - Case-insensitive contains (~i): field~i"value" - Case-insensitive contains
        
        Args:
            log: Log entry to check
            condition: Filter condition
            
        Returns:
            True if the log matches the condition, False otherwise
        """
        # Contains operator for topics field
        if 'topics~' in condition and 'topics~i' not in condition:
            match = re.search(r'topics~"([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1)
                topics = log.get('topics', '')
                if not topics:
                    return False
                return value in topics
        
        # Contains operator for message field
        elif 'message~' in condition and 'message~i' not in condition:
            match = re.search(r'message~"([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1)
                message = log.get('message', '')
                if not message:
                    return False
                return value in message
        
        # Equality operator for topics field
        elif 'topics=' in condition:
            match = re.search(r'topics="([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1)
                topics = log.get('topics', '')
                if not topics:
                    return False
                return value == topics
        
        # Equality operator for message field
        elif 'message=' in condition:
            match = re.search(r'message="([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1)
                message = log.get('message', '')
                if not message:
                    return False
                return value == message
        
        # Case-insensitive contains operator for topics field
        elif 'topics~i' in condition:
            match = re.search(r'topics~i"([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1).lower()
                topics = log.get('topics', '').lower()
                if not topics:
                    return False
                return value in topics
        
        # Case-insensitive contains operator for message field
        elif 'message~i' in condition:
            match = re.search(r'message~i"([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1).lower()
                message = log.get('message', '').lower()
                if not message:
                    return False
                return value in message
        
        # Unknown condition - log a warning and pass through
        self._log_warning(f"Unsupported filter condition: '{condition}'")
        return True
