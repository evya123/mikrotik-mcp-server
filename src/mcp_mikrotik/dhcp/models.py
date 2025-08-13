"""
MikroTik DHCP Type Definitions

This module contains type definitions specific to DHCP operations.
"""

from typing import TypedDict, Optional, List

class MikroTikDHCPServer(TypedDict, total=False):
    """
    MikroTik DHCP server structure.
    
    Reference: MikroTik RouterOS API documentation for DHCP management
    - /ip/dhcp-server/print endpoint
    """
    name: str  # DHCP server name
    interface: str  # Interface name
    address_pool: str  # Address pool name
    lease_time: str  # Lease time (e.g., "3d")
    disabled: Optional[bool]  # Whether server is disabled
    authoritative: Optional[bool]  # Whether server is authoritative
    comment: Optional[str]  # Server comment

class MikroTikDHCPLease(TypedDict, total=False):
    """
    MikroTik DHCP lease structure.
    
    Reference: MikroTik RouterOS API documentation for DHCP management
    - /ip/dhcp-server/lease/print endpoint
    """
    address: str  # IP address
    mac_address: str  # MAC address
    client_id: Optional[str]  # Client ID
    host_name: Optional[str]  # Host name
    active_address: Optional[str]  # Active address
    active_mac_address: Optional[str]  # Active MAC address
    active_server: Optional[str]  # Active server
    expires_after: Optional[str]  # Expiration time
    comment: Optional[str]  # Lease comment

class GetDHCPServersArgs(TypedDict, total=False):
    """
    Arguments for retrieving DHCP servers from MikroTik API.
    
    Reference: MikroTik RouterOS API documentation for DHCP management
    """
    name: Optional[str]  # Filter by server name
    interface: Optional[str]  # Filter by interface
    address_pool: Optional[str]  # Filter by address pool
    disabled: Optional[bool]  # Filter by disabled status
    comment: Optional[str]  # Filter by comment
