"""
MikroTik Interface Client

This module provides a specialized client for MikroTik interface management.
"""

from typing import Dict, List, Optional, Any
from ..base import MikroTikBaseClient
from .models import MikroTikInterface, GetInterfacesArgs

class MikroTikInterfaceClient(MikroTikBaseClient):
    """
    Specialized client for MikroTik interface management.
    
    Reference: MikroTik RouterOS API documentation for interface management
    """
    
    async def get_interfaces(self, options: Optional[GetInterfacesArgs] = None) -> List[MikroTikInterface]:
        """
        Get all interfaces configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /interface/print
        - Support filtering and property selection
        
        Args:
            options: Optional filtering options
            
        Returns:
            List of interface configurations
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            request_body = self._build_interfaces_request_body(options or {})
            response = self._make_request('POST', '/interface/print', request_body)
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching interfaces: {str(e)}")
            raise
    
    async def get_ethernet_interfaces(self) -> List[MikroTikInterface]:
        """
        Get Ethernet interfaces configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /interface/ethernet/print
        
        Returns:
            List of Ethernet interface configurations
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/interface/ethernet/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching Ethernet interfaces: {str(e)}")
            raise
    
    async def get_wireless_interfaces(self) -> List[MikroTikInterface]:
        """
        Get wireless interfaces configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /interface/wireless/print
        
        Returns:
            List of wireless interface configurations
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/interface/wireless/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching wireless interfaces: {str(e)}")
            raise
    
    async def get_bridge_interfaces(self) -> List[MikroTikInterface]:
        """
        Get bridge interfaces configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /interface/bridge/print
        
        Returns:
            List of bridge interface configurations
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/interface/bridge/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching bridge interfaces: {str(e)}")
            raise
    
    def _build_interfaces_request_body(self, options: GetInterfacesArgs) -> Dict[str, Any]:
        """
        Build the request body for interface API calls.
        
        Args:
            options: Interface filtering options
            
        Returns:
            Request body dictionary
        """
        request_body = {}
        
        # Map options to request body with proper API parameter names
        option_mappings = {
            'name': 'name',
            'type': 'type',
            'disabled': 'disabled',
            'running': 'running',
            'comment': 'comment'
        }
        
        for option_key, api_key in option_mappings.items():
            if options.get(option_key) is not None:
                request_body[api_key] = options[option_key]
        
        return request_body
