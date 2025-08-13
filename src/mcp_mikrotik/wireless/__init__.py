"""
MikroTik Wireless Module

This module provides specialized client functionality for MikroTik wireless management.
"""

# TODO: Implement wireless management functionality
# Reference: MikroTik RouterOS API documentation for wireless management
# - /interface/wireless/print - List wireless interfaces
# - /interface/wireless/registration-table/print - List connected wireless clients
# - /interface/wireless/sniffer/print - Wireless sniffer configuration
# - Wireless security and authentication settings

from .client import MikroTikWirelessClient

__all__ = [
    "MikroTikWirelessClient"
]
