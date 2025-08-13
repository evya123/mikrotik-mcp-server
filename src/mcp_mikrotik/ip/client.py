"""
MikroTik IP Client

This module provides a specialized client for IP management operations.
It handles all IP-related API calls with proper error handling and validation.
"""
from typing import Dict, List, Optional, Any
import requests
import asyncio

from ..base import MikroTikBaseClient
from .models import (
    MikroTikIPAddress,
    MikroTikIPRoute,
    MikroTikIPPool,
    GetIPAddressesArgs,
    GetIPRoutesArgs
)


class MikroTikIPClient(MikroTikBaseClient):
    """
    Specialized client for MikroTik IP management operations.
    
    This client provides methods for managing IP addresses, routes, and pools
    on MikroTik RouterOS devices.
    """
    
    async def get_ip_addresses(self, options: Optional[GetIPAddressesArgs] = None) -> List[MikroTikIPAddress]:
        """
        Get IP addresses configured on the device.
        
        Args:
            options: Optional filtering options
            
        Returns:
            List of IP address configurations
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        try:
            request_body = self._build_ip_addresses_request_body(options or {})
            response = self._make_request('POST', '/ip/address/print', request_body)
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response type: {type(response).__name__}")
                return []
                
        except (requests.RequestException, ValueError, TypeError) as e:
            self._log_error(f"Error fetching IP addresses: {str(e)}")
            raise
    
    async def get_ip_routes(self, options: Optional[GetIPRoutesArgs] = None) -> List[MikroTikIPRoute]:
        """
        Get IP routes configured on the device.
        
        Args:
            options: Optional filtering options
            
        Returns:
            List of IP route configurations
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        try:
            request_body = self._build_ip_routes_request_body(options or {})
            response = self._make_request('POST', '/ip/route/print', request_body)
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response type: {type(response).__name__}")
                return []
                
        except (requests.RequestException, ValueError, TypeError) as e:
            self._log_error(f"Error fetching IP routes: {str(e)}")
            raise
    
    async def get_ip_pools(self) -> List[MikroTikIPPool]:
        """
        Get IP pools configured on the device.
        
        Returns:
            List of IP pool configurations
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        try:
            response = self._make_request('POST', '/ip/pool/print', {})
            
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'ret' in response:
                return response['ret']
            else:
                self._log_warning(f"Unexpected response type: {type(response).__name__}")
                return []
                
        except (requests.RequestException, ValueError, TypeError) as e:
            self._log_error(f"Error fetching IP pools: {str(e)}")
            raise
    
    async def get_network_summary(self) -> Dict[str, Any]:
        """
        Get a summary of network configuration including IP addresses, routes, and pools.
        
        Returns:
            Dictionary containing network configuration summary
            
        Raises:
            requests.ConnectionError: If there's a connection error
            requests.Timeout: If the request times out
            requests.HTTPError: If the API returns an HTTP error status
            requests.RequestException: For other request-related errors
            ValueError: For invalid response data
            TypeError: If the response is not in the expected format
        """
        try:
            # Get all network configuration in parallel
            addresses, routes, pools = await asyncio.gather(
                self.get_ip_addresses(),
                self.get_ip_routes(),
                self.get_ip_pools(),
                return_exceptions=True
            )
            
            # Handle any exceptions that occurred
            if isinstance(addresses, Exception):
                self._log_error(f"Error fetching addresses: {addresses}")
                addresses = []
            if isinstance(routes, Exception):
                self._log_error(f"Error fetching routes: {routes}")
                routes = []
            if isinstance(pools, Exception):
                self._log_error(f"Error fetching pools: {pools}")
                pools = []
            
            return {
                "ip_addresses_count": len(addresses),
                "ip_routes_count": len(routes),
                "ip_pools_count": len(pools),
                "interfaces": list(set(addr.get('interface', '') for addr in addresses if addr.get('interface'))),
                "networks": list(set(addr.get('network', '') for addr in addresses if addr.get('network'))),
                "gateways": list(set(route.get('gateway', '') for route in routes if route.get('gateway')))
            }
            
        except Exception as e:
            self._log_error(f"Error generating network summary: {str(e)}")
            return {"error": str(e)}
    
    def _build_ip_addresses_request_body(self, options: GetIPAddressesArgs) -> Dict[str, Any]:
        """Build the request body for IP addresses API calls."""
        request_body = {}
        
        # Map options to request body with proper API parameter names
        if options.get('interface'):
            request_body['interface'] = options['interface']
        if options.get('network'):
            request_body['network'] = options['network']
        if options.get('comment'):
            request_body['comment'] = options['comment']
        if options.get('disabled') is not None:
            request_body['disabled'] = options['disabled']
        
        return request_body
    
    def _build_ip_routes_request_body(self, options: GetIPRoutesArgs) -> Dict[str, Any]:
        """Build the request body for IP routes API calls."""
        request_body = {}
        
        # Map options to request body with proper API parameter names
        if options.get('dst_address'):
            request_body['dst-address'] = options['dst_address']
        if options.get('gateway'):
            request_body['gateway'] = options['gateway']
        if options.get('routing_mark'):
            request_body['routing-mark'] = options['routing_mark']
        if options.get('disabled') is not None:
            request_body['disabled'] = options['disabled']
        
        return request_body
