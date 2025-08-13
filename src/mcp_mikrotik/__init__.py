"""
MikroTik MCP Package

This package provides a comprehensive Model Context Protocol (MCP) implementation
for MikroTik RouterOS devices. It includes specialized clients for different API
domains and a unified main client interface.
"""

from .client import MikroTikClient
from .base import MikroTikBaseClient
from .logs import MikroTikLogsClient
from .system import MikroTikSystemClient
from .ip import MikroTikIPClient
from .interface import MikroTikInterfaceClient
from .firewall import MikroTikFirewallClient
from .wireless import MikroTikWirelessClient
from .routing import MikroTikRoutingClient
from .dhcp import MikroTikDHCPClient
from .models import MikroTikConfig

__version__ = "0.2.0"
__all__ = [
    "MikroTikClient",
    "MikroTikBaseClient",
    "MikroTikLogsClient",
    "MikroTikSystemClient",
    "MikroTikIPClient",
    "MikroTikInterfaceClient",
    "MikroTikFirewallClient",
    "MikroTikWirelessClient",
    "MikroTikRoutingClient",
    "MikroTikDHCPClient",
    "MikroTikConfig"
]
