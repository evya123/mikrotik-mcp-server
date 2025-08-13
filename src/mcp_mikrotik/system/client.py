"""
MikroTik System Client

This module provides a specialized client for system management operations.
It handles all system-related API calls with proper error handling and validation.
"""
from typing import Dict, List, Optional, Any
import requests

from ..base import MikroTikBaseClient
from .models import MikroTikSystemInfo


class MikroTikSystemClient(MikroTikBaseClient):
    """
    Specialized client for MikroTik system management operations.
    
    This client provides methods for retrieving system information, resources,
    and status from MikroTik RouterOS devices.
    """
    
    async def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            System information dictionary
            
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
                self._log_warning("Empty system info response")
                return {}
            elif not isinstance(response, list):
                raise TypeError(f"Expected list response, got {type(response).__name__}")
            return {}
        except (requests.RequestException, ValueError, TypeError) as e:
            self._log_error(f"Error fetching system info: {str(e)}")
            raise
    
    async def get_system_resources(self) -> List[MikroTikSystemInfo]:
        """
        Get detailed system resource information.
        
        Returns:
            List of system resource information entries
            
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
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response type: {type(response).__name__}")
                return []
        except (requests.RequestException, ValueError, TypeError) as e:
            self._log_error(f"Error fetching system resources: {str(e)}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health information including resource usage.
        
        This method provides a comprehensive view of system health by combining
        resource information with calculated metrics.
        
        Returns:
            Dictionary containing system health metrics
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        try:
            system_info = await self.get_system_info()
            
            if not system_info:
                return {"status": "unknown", "error": "No system information available"}
            
            # Calculate health metrics
            memory_usage = 0
            if system_info.get('total_memory') and system_info.get('free_memory'):
                memory_usage = ((system_info['total_memory'] - system_info['free_memory']) / 
                               system_info['total_memory']) * 100
            
            disk_usage = 0
            if system_info.get('total_hdd_space') and system_info.get('free_hdd_space'):
                disk_usage = ((system_info['total_hdd_space'] - system_info['free_hdd_space']) / 
                             system_info['total_hdd_space']) * 100
            
            # Determine overall health status
            status = "healthy"
            if memory_usage > 90 or disk_usage > 90:
                status = "critical"
            elif memory_usage > 80 or disk_usage > 80:
                status = "warning"
            elif memory_usage > 70 or disk_usage > 70:
                status = "attention"
            
            return {
                "status": self._determine_health_status(memory_usage, disk_usage),
                "uptime": system_info.get('uptime'),
                "version": system_info.get('version'),
                "cpu_load": system_info.get('cpu_load'),
                "memory_usage_percent": round(memory_usage, 2),
                "disk_usage_percent": round(disk_usage, 2),
                "free_memory_mb": round(system_info.get('free_memory', 0) / (1024 * 1024), 2),
                "free_disk_mb": round(system_info.get('free_hdd_space', 0) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self._log_error(f"Error calculating system health: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _determine_health_status(self, memory_usage: float, disk_usage: float) -> str:
        """
        Determine overall health status based on resource usage.
        
        Args:
            memory_usage: Memory usage percentage
            disk_usage: Disk usage percentage
            
        Returns:
            Health status string
        """
        if memory_usage > 90 or disk_usage > 90:
            return "critical"
        elif memory_usage > 80 or disk_usage > 80:
            return "warning"
        elif memory_usage > 70 or disk_usage > 70:
            return "attention"
        else:
            return "healthy"
