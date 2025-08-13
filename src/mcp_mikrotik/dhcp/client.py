"""
MikroTik DHCP Client

This module provides a specialized client for MikroTik DHCP management.
"""

from typing import Dict, List, Optional, Any
from ..base import MikroTikBaseClient
from .models import MikroTikDHCPServer, MikroTikDHCPLease, GetDHCPServersArgs

class MikroTikDHCPClient(MikroTikBaseClient):
    """
    Specialized client for MikroTik DHCP management.
    
    Reference: MikroTik RouterOS API documentation for DHCP management
    """
    
    async def get_dhcp_servers(self, options: Optional[GetDHCPServersArgs] = None) -> List[MikroTikDHCPServer]:
        """
        Get DHCP servers configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/dhcp-server/print
        - Support filtering and property selection
        
        Args:
            options: Optional filtering options
            
        Returns:
            List of DHCP server configurations
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            request_body = self._build_dhcp_servers_request_body(options or {})
            response = self._make_request('POST', '/ip/dhcp-server/print', request_body)
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching DHCP servers: {str(e)}")
            raise
    
    async def get_dhcp_leases(self) -> List[MikroTikDHCPLease]:
        """
        Get DHCP leases from all servers.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/dhcp-server/lease/print
        
        Returns:
            List of DHCP leases
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/ip/dhcp-server/lease/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching DHCP leases: {str(e)}")
            raise
    
    async def get_dhcp_networks(self) -> List[Dict[str, Any]]:
        """
        Get DHCP networks configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/dhcp-server/network/print
        
        Returns:
            List of DHCP networks
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/ip/dhcp-server/network/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching DHCP networks: {str(e)}")
            raise
    
    async def get_dhcp_clients(self) -> List[Dict[str, Any]]:
        """
        Get DHCP clients configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/dhcp-client/print
        
        Returns:
            List of DHCP clients
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/ip/dhcp-client/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching DHCP clients: {str(e)}")
            raise
    
    def _build_dhcp_servers_request_body(self, options: GetDHCPServersArgs) -> Dict[str, Any]:
        """
        Build the request body for DHCP servers API calls.
        
        Args:
            options: DHCP servers filtering options
            
        Returns:
            Request body dictionary
        """
        request_body = {}
        
        # Map options to request body with proper API parameter names
        option_mappings = {
            'name': 'name',
            'interface': 'interface',
            'address_pool': 'address-pool',
            'disabled': 'disabled',
            'comment': 'comment'
        }
        
        for option_key, api_key in option_mappings.items():
            if options.get(option_key) is not None:
                request_body[api_key] = options[option_key]
        
        return request_body
