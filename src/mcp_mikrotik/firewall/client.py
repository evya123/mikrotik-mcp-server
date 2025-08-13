"""
MikroTik Firewall Client

This module provides a specialized client for MikroTik firewall management.
"""

from typing import Dict, List, Optional, Any
from ..base import MikroTikBaseClient
from .models import MikroTikFirewallRule, GetFirewallRulesArgs

class MikroTikFirewallClient(MikroTikBaseClient):
    """
    Specialized client for MikroTik firewall management.
    
    Reference: MikroTik RouterOS API documentation for firewall management
    """
    
    async def get_firewall_rules(self, options: Optional[GetFirewallRulesArgs] = None) -> List[MikroTikFirewallRule]:
        """
        Get firewall filter rules configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/firewall/filter/print
        - Support filtering and property selection
        
        Args:
            options: Optional filtering options
            
        Returns:
            List of firewall filter rules
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            request_body = self._build_firewall_rules_request_body(options or {})
            response = self._make_request('POST', '/ip/firewall/filter/print', request_body)
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching firewall rules: {str(e)}")
            raise
    
    async def get_nat_rules(self) -> List[MikroTikFirewallRule]:
        """
        Get NAT rules configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/firewall/nat/print
        
        Returns:
            List of NAT rules
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/ip/firewall/nat/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching NAT rules: {str(e)}")
            raise
    
    async def get_mangle_rules(self) -> List[MikroTikFirewallRule]:
        """
        Get mangle rules configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/firewall/mangle/print
        
        Returns:
            List of mangle rules
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/ip/firewall/mangle/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching mangle rules: {str(e)}")
            raise
    
    async def get_address_lists(self) -> List[Dict[str, Any]]:
        """
        Get address lists configured on the device.
        
        Reference: MikroTik RouterOS API documentation
        - Endpoint: /ip/firewall/address-list/print
        
        Returns:
            List of address lists
            
        Raises:
            requests.RequestException: For connection or API errors
            ValueError: For invalid response data
        """
        try:
            response = self._make_request('POST', '/ip/firewall/address-list/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response format: {type(response)}")
                return []
                
        except Exception as e:
            self._log_error(f"Error fetching address lists: {str(e)}")
            raise
    
    def _build_firewall_rules_request_body(self, options: GetFirewallRulesArgs) -> Dict[str, Any]:
        """
        Build the request body for firewall rules API calls.
        
        Args:
            options: Firewall rules filtering options
            
        Returns:
            Request body dictionary
        """
        request_body = {}
        
        # Map options to request body with proper API parameter names
        option_mappings = {
            'chain': 'chain',
            'action': 'action',
            'src_address': 'src-address',
            'dst_address': 'dst-address',
            'protocol': 'protocol',
            'disabled': 'disabled',
            'comment': 'comment'
        }
        
        for option_key, api_key in option_mappings.items():
            if options.get(option_key) is not None:
                request_body[api_key] = options[option_key]
        
        return request_body
