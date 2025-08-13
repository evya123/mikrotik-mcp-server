"""
MikroTik IP Type Definitions

This module contains type definitions for IP-related operations in the MikroTik API.
"""
from typing import TypedDict, Optional, List


class MikroTikIPAddress(TypedDict, total=False):
    """
    MikroTik IP address structure.
    
    Based on MikroTik RouterOS API documentation for /ip/address/print endpoint.
    """
    address: str  # IP address with subnet mask (e.g., "192.168.1.1/24")
    network: str  # Network address
    interface: str  # Interface name
    comment: Optional[str]  # Optional comment
    disabled: Optional[bool]  # Whether the address is disabled


class MikroTikIPRoute(TypedDict, total=False):
    """
    MikroTik IP route structure.
    
    Based on MikroTik RouterOS API documentation for /ip/route/print endpoint.
    """
    dst_address: str  # Destination address
    gateway: str  # Gateway address
    distance: int  # Route distance
    comment: Optional[str]  # Optional comment
    disabled: Optional[bool]  # Whether the route is disabled
    routing_mark: Optional[str]  # Routing mark
    scope: Optional[int]  # Route scope


class MikroTikIPPool(TypedDict, total=False):
    """
    MikroTik IP pool structure.
    
    Based on MikroTik RouterOS API documentation for /ip/pool/print endpoint.
    """
    name: str  # Pool name
    ranges: str  # IP address ranges (e.g., "192.168.1.10-192.168.1.100")
    comment: Optional[str]  # Optional comment
    disabled: Optional[bool]  # Whether the pool is disabled


class GetIPAddressesArgs(TypedDict, total=False):
    """
    Arguments for retrieving IP addresses from MikroTik API.
    """
    interface: Optional[str]  # Filter by interface name
    network: Optional[str]  # Filter by network address
    comment: Optional[str]  # Filter by comment
    disabled: Optional[bool]  # Filter by disabled status


class GetIPRoutesArgs(TypedDict, total=False):
    """
    Arguments for retrieving IP routes from MikroTik API.
    """
    dst_address: Optional[str]  # Filter by destination address
    gateway: Optional[str]  # Filter by gateway address
    routing_mark: Optional[str]  # Filter by routing mark
    disabled: Optional[bool]  # Filter by disabled status
