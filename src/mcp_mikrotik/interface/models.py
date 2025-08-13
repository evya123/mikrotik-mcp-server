"""
MikroTik Interface Type Definitions

This module contains type definitions specific to interface operations.
"""

from typing import TypedDict, Optional, List

class MikroTikInterface(TypedDict, total=False):
    """
    MikroTik interface structure.
    
    Reference: MikroTik RouterOS API documentation for interface management
    - /interface/print endpoint
    """
    name: str  # Interface name
    type: str  # Interface type (ethernet, wireless, bridge, etc.)
    mtu: Optional[int]  # Maximum Transmission Unit
    mac_address: Optional[str]  # MAC address
    disabled: Optional[bool]  # Whether interface is disabled
    running: Optional[bool]  # Whether interface is running
    comment: Optional[str]  # Interface comment
    default_name: Optional[str]  # Default interface name
    speed: Optional[str]  # Interface speed
    duplex: Optional[str]  # Interface duplex mode
    auto_negotiation: Optional[bool]  # Auto-negotiation status

class GetInterfacesArgs(TypedDict, total=False):
    """
    Arguments for retrieving interfaces from MikroTik API.
    
    Reference: MikroTik RouterOS API documentation for interface management
    """
    name: Optional[str]  # Filter by interface name
    type: Optional[str]  # Filter by interface type
    disabled: Optional[bool]  # Filter by disabled status
    running: Optional[bool]  # Filter by running status
    comment: Optional[str]  # Filter by comment
