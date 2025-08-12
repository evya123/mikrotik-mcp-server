"""
MikroTik API Client

This module provides a client for interacting with the MikroTik RouterOS REST API.

This client provides methods for retrieving logs and system information from a MikroTik device.
It implements client-side filtering for logs, as the RouterOS REST API's 'where' parameter
for /log/print doesn't work as expected.

Supported filter syntax:
- Contains (~): field~"value" - Checks if field contains value
- Equals (=): field="value" - Checks if field equals value exactly
- Case-insensitive contains (~i): field~i"value" - Case-insensitive contains
- Multiple conditions with AND: condition1 and condition2
- Multiple conditions with OR: condition1 or condition2

Currently supported fields:
- topics: Filter by log topics (e.g., topics~"system")
- message: Filter by log message content (e.g., message~"login")

Examples:
- topics~"system" - Logs with "system" in topics
- message~"error" - Logs with "error" in message
- topics~"dhcp" and message~"assigned" - DHCP logs about address assignment
- topics~"system" or topics~"dhcp" - Logs with either "system" or "dhcp" in topics
"""
import re
import json
import requests
from typing import Dict, List, Optional, Any, Union, cast
from requests.auth import HTTPBasicAuth

# Use absolute imports
from python_src.types.models import (
    MikroTikConfig, 
    MikroTikLogEntry, 
    MikroTikAPIResponse,
    GetLogsArgs
)


class MikroTikClient:
    """Client for interacting with the MikroTik RouterOS REST API."""
    
    def __init__(self, config: MikroTikConfig):
        """
        Initialize the MikroTik API client.
        
        Args:
            config: Configuration for the MikroTik API connection
        """
        self.config = config
        protocol = "https" if config.get("useSSL", False) else "http"
        port = config.get("port") or (443 if config.get("useSSL", False) else 80)
        
        self.base_url = f"{protocol}://{config['host']}:{port}/rest"
        self.auth = HTTPBasicAuth(config['username'], config['password'])
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            "Content-Type": "application/json",
        })
        self.session.timeout = 30  # 30 seconds timeout
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a request to the MikroTik API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For unsupported HTTP methods or invalid response data
            json.JSONDecodeError: If the response cannot be parsed as JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        print(f"[MikroTik] Request: {method} {endpoint}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            print(f"[MikroTik] Response: {response.status_code} {response.reason}")
            
            try:
                return response.json()
            except ValueError as e:
                # Handle empty or invalid JSON response
                if response.content:
                    print(f"[MikroTik] Invalid JSON response: {response.content[:100]}...")
                else:
                    print("[MikroTik] Empty response received")
                raise ValueError(f"Failed to parse API response as JSON: {str(e)}")
                
        except requests.ConnectionError as e:
            print(f"[MikroTik] Connection error: {str(e)}")
            raise
        except requests.Timeout as e:
            print(f"[MikroTik] Request timeout: {str(e)}")
            raise
        except requests.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else 'unknown'
            print(f"[MikroTik] HTTP error {status_code}: {str(e)}")
            
            # Try to extract more detailed error information from the response
            error_detail = ""
            try:
                if hasattr(e, 'response') and e.response and e.response.content:
                    error_content = e.response.content.decode('utf-8', errors='replace')
                    error_detail = f" - Details: {error_content[:200]}"
            except Exception:
                pass
                
            raise requests.HTTPError(f"API request failed with status {status_code}{error_detail}", response=e.response if hasattr(e, 'response') else None)
        except requests.RequestException as e:
            print(f"[MikroTik] Request error: {str(e)}")
            raise
    
    def _filter_logs(self, logs: List[MikroTikLogEntry], where: str) -> List[MikroTikLogEntry]:
        """
        Client-side filtering implementation for log entries.
        
        The MikroTik RouterOS REST API's 'where' parameter for /log/print doesn't work as expected,
        so we implement filtering on the client side. This method parses the filter condition and
        applies it to each log entry.
        
        Supported filter syntax:
        - Simple equality: field="value"
        - Contains: field~"value"
        - Multiple conditions with AND: condition1 and condition2
        
        Currently supported fields:
        - topics: Filter by log topics (e.g., topics~"system")
        - message: Filter by log message content (e.g., message~"login")
        
        Examples:
        - topics~"system"
        - message~"error"
        - topics~"dhcp" and message~"assigned"
        
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
            # Split the condition by 'and' to support multiple conditions
            conditions = where.split(' and ')
            
            filtered_logs = []
            for log in logs:
                # A log entry must match all conditions to be included
                if all(self._check_condition(log, condition) for condition in conditions):
                    filtered_logs.append(log)
            
            return filtered_logs
        except Exception as e:
            print(f"[MikroTik] Filter parsing error: {str(e)}")
            print(f"[MikroTik] Invalid filter syntax: '{where}'. Returning all logs.")
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
        if 'topics~' in condition and not 'topics~i' in condition:
            match = re.search(r'topics~"([^"]+)"', condition)
            if match and match.group(1):
                value = match.group(1)
                topics = log.get('topics', '')
                if not topics:
                    return False
                return value in topics
        
        # Contains operator for message field
        elif 'message~' in condition and not 'message~i' in condition:
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
        
        # Handle complex conditions with OR operator
        elif ' or ' in condition:
            or_conditions = condition.split(' or ')
            return any(self._check_condition(log, or_cond) for or_cond in or_conditions)
        
        # Unknown condition - log a warning and pass through
        print(f"[MikroTik] Warning: Unsupported filter condition: '{condition}'")
        return True
    
    async def get_logs(self, options: Optional[GetLogsArgs] = None, max_logs: int = 1000) -> Union[List[MikroTikLogEntry], int]:
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
        
        # Limit the number of logs if max_logs is specified
        # Note: This is not a standard RouterOS API parameter but helps with performance
        if max_logs is not None and not options.get('countOnly'):
            # Use the limit parameter if available in the future
            # For now, we'll handle limiting on the client side
            pass
        
        # Note: 'where' parameter is ignored by REST API, so we'll do client-side filtering
        try:
            response = self._make_request('POST', '/log/print', request_body)
            
            # Handle countOnly response (returns a string with the count)
            if options.get('countOnly'):
                if isinstance(response, str):
                    try:
                        return int(response)
                    except ValueError:
                        print(f"[MikroTik] Warning: Count-only response is not a valid number: {response}")
                        return 0
                elif isinstance(response, int):
                    return response
                else:
                    print(f"[MikroTik] Warning: Unexpected count-only response type: {type(response).__name__}")
                    return 0
            
            # Handle different response types for log entries
            if isinstance(response, list):
                logs = response
            elif isinstance(response, dict):
                # Some API endpoints return a dict with a 'ret' property
                if 'ret' in response:
                    logs = response['ret']
                else:
                    logs = []
                    print(f"[MikroTik] Note: Received dict response: {response}")
            else:
                print(f"[MikroTik] Warning: Unexpected response type: {type(response).__name__}")
                logs = []
            
            # Limit the number of logs if max_logs is specified
            if max_logs is not None and len(logs) > max_logs:
                print(f"[MikroTik] Warning: Limiting logs to {max_logs} entries (retrieved {len(logs)})")
                logs = logs[:max_logs]
            
            # Apply client-side filtering if where parameter is provided
            where = options.get('where')
            if where:
                logs = self._filter_logs(logs, where)
            
            return logs
        except (requests.RequestException, ValueError, TypeError) as e:
            print(f"[MikroTik] Error retrieving logs: {str(e)}")
            raise
    
    async def get_logs_by_condition(self, condition: str, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
        """
        Get logs filtered by a specific condition.
        
        This is a convenience method that calls get_logs with a where parameter.
        
        Args:
            condition: Filter condition (e.g., 'topics~"system"', 'message~"login"')
            options: Additional options for the API call
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of filtered log entries
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            'where': condition,
            **options
        }, max_logs=max_logs)
    
    async def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            System information
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        try:
            response = self._make_request('POST', '/system/resource/print', {})
            
            # The RouterOS API returns an array directly, not wrapped in a 'ret' property
            if isinstance(response, list) and len(response) > 0:
                return response[0]
            elif isinstance(response, list) and len(response) == 0:
                print("[MikroTik] Warning: Empty system info response")
                return {}
            elif not isinstance(response, list):
                raise TypeError(f"Expected list response, got {type(response).__name__}")
            return {}
        except (requests.RequestException, ValueError, TypeError) as e:
            print(f"[MikroTik] Error fetching system info: {str(e)}")
            raise
    
    async def get_debug_logs(self, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
        """
        Get debug logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of debug log entries
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"debug"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_error_logs(self, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
        """
        Get error logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of error log entries
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"error"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_warning_logs(self, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
        """
        Get warning logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of warning log entries
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"warning"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_info_logs(self, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
        """
        Get info logs using /log/print with where filter.
        
        Args:
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of info log entries
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            **options,
            'where': 'topics~"info"',
            'brief': True
        }, max_logs=max_logs)
    
    async def get_logs_from_buffer(self, buffer_name: str, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
        """
        Get logs from a specific buffer (for separate memory logging buffers).
        
        Args:
            buffer_name: Name of the buffer
            options: Additional options
            max_logs: Maximum number of logs to retrieve (default: 1000)
            
        Returns:
            List of log entries from the specified buffer
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            'where': f'buffer={buffer_name}',
            **options,
        }, max_logs=max_logs)
    
    async def get_logs_with_extra_info(self, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000) -> List[MikroTikLogEntry]:
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
            
        Raises:
            Same exceptions as get_logs
        """
        if options is None:
            options = {}
        
        return await self.get_logs({
            'withExtraInfo': True,
            **options,
        }, max_logs=max_logs)
    
    async def find_logs(self, where: str, options: Optional[Dict[str, Any]] = None) -> List[MikroTikLogEntry]:
        """
        Find logs using client-side filtering (previously used /log/find endpoint).
        
        This method now uses /log/print with client-side filtering instead of /log/find,
        as testing has shown that /log/find doesn't filter logs as expected.
        
        Args:
            where: Filter condition
            options: Additional options
            
        Returns:
            List of matching log entries
            
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
        
        # Use /log/print with client-side filtering
        return await self.get_logs({
            **options,
            'where': where
        })
    
    async def test_connection(self) -> bool:
        """
        Test connection to the MikroTik device.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            await self.get_system_info()
            return True
        except Exception as e:
            print(f"[MikroTik] Connection test failed: {str(e)}")
            return False
