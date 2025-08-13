"""
MikroTik DHCP Module

This module provides specialized client functionality for MikroTik DHCP management.
"""

# TODO: Implement DHCP management functionality
# Reference: MikroTik RouterOS API documentation for DHCP management
# - /ip/dhcp-server/print - List DHCP servers
# - /ip/dhcp-server/lease/print - List DHCP leases
# - /ip/dhcp-server/network/print - List DHCP networks
# - /ip/dhcp-client/print - List DHCP clients

from .client import MikroTikDHCPClient

__all__ = [
    "MikroTikDHCPClient"
]
