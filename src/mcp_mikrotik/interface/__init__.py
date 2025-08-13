"""
MikroTik Interface Module

This module provides specialized client functionality for MikroTik interface management.
"""

# TODO: Implement interface management functionality
# Reference: MikroTik RouterOS API documentation for interface management
# - /interface/print - List all interfaces
# - /interface/ethernet/print - List Ethernet interfaces
# - /interface/wireless/print - List wireless interfaces
# - /interface/bridge/print - List bridge interfaces
# - Interface statistics and monitoring

from .client import MikroTikInterfaceClient

__all__ = [
    "MikroTikInterfaceClient"
]
