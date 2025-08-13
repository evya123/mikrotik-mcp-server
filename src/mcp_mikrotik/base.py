"""
MikroTik Base Client

This module provides the base client class that all specialized MikroTik clients inherit from.
It handles common functionality like authentication, HTTP requests, and logging.
"""
import json
from typing import Dict, List, Optional, Any, Union
import requests
from requests.auth import HTTPBasicAuth

from .models import MikroTikConfig


class MikroTikBaseClient:
    """
    Base client for interacting with the MikroTik RouterOS REST API.
    
    This class provides common functionality that all specialized clients inherit from,
    including authentication, HTTP request handling, and logging.
    """
    
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
        
        self._log_info(f"Request: {method} {endpoint}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            self._log_info(f"Response: {response.status_code} {response.reason}")
            
            try:
                return response.json()
            except ValueError as e:
                # Handle empty or invalid JSON response
                if response.content:
                    self._log_warning(f"Invalid JSON response: {response.content[:100]}...")
                else:
                    self._log_info("Empty response received")
                raise ValueError(f"Failed to parse API response as JSON: {str(e)}")
                
        except requests.ConnectionError as e:
            self._log_error(f"Connection error: {str(e)}")
            raise
        except requests.Timeout as e:
            self._log_error(f"Request timeout: {str(e)}")
            raise
        except requests.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else 'unknown'
            self._log_error(f"HTTP error {status_code}: {str(e)}")
            
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
            self._log_error(f"Request error: {str(e)}")
            raise
    
    def _log_info(self, message: str) -> None:
        """Log an informational message."""
        print(f"[MikroTik] {message}")
    
    def _log_warning(self, message: str) -> None:
        """Log a warning message."""
        print(f"[MikroTik] Warning: {message}")
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        print(f"[MikroTik] Error: {message}")
    
    def _log_note(self, message: str) -> None:
        """Log a note message."""
        print(f"[MikroTik] Note: {message}")
    
    async def test_connection(self) -> bool:
        """
        Test connection to the MikroTik device.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Use a simple endpoint to test connectivity
            self._make_request('POST', '/system/resource/print', {})
            return True
        except Exception as e:
            self._log_error(f"Connection test failed: {str(e)}")
            return False
