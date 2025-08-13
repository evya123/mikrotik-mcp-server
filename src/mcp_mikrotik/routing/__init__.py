"""
MikroTik Routing Module

This module provides specialized client functionality for MikroTik routing management.
"""

# TODO: Implement routing management functionality
# Reference: MikroTik RouterOS API documentation for routing management
# - /routing/ospf/print - OSPF routing configuration
# - /routing/bgp/print - BGP routing configuration
# - /routing/rip/print - RIP routing configuration
# - /routing/table/print - Routing tables
# - Route redistribution and policy routing

from .client import MikroTikRoutingClient

__all__ = [
    "MikroTikRoutingClient"
]
