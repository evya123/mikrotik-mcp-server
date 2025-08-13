"""
MikroTik Main Client

This module provides the main client that combines all specialized MikroTik clients.
It provides a unified interface for all MikroTik API operations.
"""

from .base import MikroTikBaseClient
from .logs import MikroTikLogsClient
from .system import MikroTikSystemClient
from .ip import MikroTikIPClient
from .interface import MikroTikInterfaceClient
from .firewall import MikroTikFirewallClient
from .wireless import MikroTikWirelessClient
from .routing import MikroTikRoutingClient
from .dhcp import MikroTikDHCPClient


class MikroTikClient(MikroTikBaseClient):
    """
    Main MikroTik client that combines all specialized clients.
    
    This client provides access to all MikroTik API functionality through
    specialized sub-clients for different API domains.
    """
    
    def __init__(self, config):
        """Initialize the main client and all specialized clients."""
        super().__init__(config)
        
        # Initialize specialized clients
        self.logs = MikroTikLogsClient(config)
        self.system = MikroTikSystemClient(config)
        self.ip = MikroTikIPClient(config)
        self.interface = MikroTikInterfaceClient(config)
        self.firewall = MikroTikFirewallClient(config)
        self.wireless = MikroTikWirelessClient(config)
        self.routing = MikroTikRoutingClient(config)
        self.dhcp = MikroTikDHCPClient(config)
    
    # Delegate methods to specialized clients for backward compatibility
    
    async def get_logs(self, options=None, max_logs=1000):
        """Get system logs with optional filtering."""
        return await self.logs.get_logs(options, max_logs)
    
    async def get_debug_logs(self, options=None, max_logs=1000):
        """Get debug logs."""
        return await self.logs.get_debug_logs(options, max_logs)
    
    async def get_error_logs(self, options=None, max_logs=1000):
        """Get error logs."""
        return await self.logs.get_error_logs(options, max_logs)
    
    async def get_warning_logs(self, options=None, max_logs=1000):
        """Get warning logs."""
        return await self.logs.get_warning_logs(options, max_logs)
    
    async def get_info_logs(self, options=None, max_logs=1000):
        """Get info logs."""
        return await self.logs.get_info_logs(options, max_logs)
    
    async def get_logs_from_buffer(self, buffer_name, options=None, max_logs=1000):
        """Get logs from a specific buffer."""
        return await self.logs.get_logs_from_buffer(buffer_name, options, max_logs)
    
    async def get_logs_with_extra_info(self, options=None, max_logs=1000):
        """Get logs with extra info."""
        return await self.logs.get_logs_with_extra_info(options, max_logs)
    
    async def find_logs(self, where, options=None):
        """Find logs using client-side filtering."""
        return await self.logs.find_logs(where, options)
    
    async def get_logs_by_condition(self, condition, options=None, max_logs=1000):
        """Get logs filtered by a specific condition."""
        return await self.logs.get_logs_by_condition(condition, options, max_logs)
    
    async def get_system_info(self):
        """Get system information."""
        return await self.system.get_system_info()
    
    async def get_system_resources(self):
        """Get detailed system resource information."""
        return await self.system.get_system_resources()
    
    async def get_system_health(self):
        """Get system health information including resource usage."""
        return await self.system.get_system_health()
    
    async def get_ip_addresses(self, options=None):
        """Get IP addresses configured on the device."""
        return await self.ip.get_ip_addresses(options)
    
    async def get_ip_routes(self, options=None):
        """Get IP routes configured on the device."""
        return await self.ip.get_ip_routes(options)
    
    async def get_ip_pools(self):
        """Get IP pools configured on the device."""
        return await self.ip.get_ip_pools()
    
    async def get_network_summary(self):
        """Get a summary of network configuration."""
        return await self.ip.get_network_summary()
