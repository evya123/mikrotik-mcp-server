"""
MikroTik Firewall Type Definitions

This module contains type definitions specific to firewall operations.
"""

from typing import TypedDict, Optional, List

class MikroTikFirewallRule(TypedDict, total=False):
    """
    MikroTik firewall rule structure.
    
    Reference: MikroTik RouterOS API documentation for firewall management
    - /ip/firewall/filter/print endpoint
    """
    chain: str  # Rule chain (input, output, forward, etc.)
    action: str  # Rule action (accept, drop, reject, etc.)
    src_address: Optional[str]  # Source address
    dst_address: Optional[str]  # Destination address
    protocol: Optional[str]  # Protocol (tcp, udp, icmp, etc.)
    src_port: Optional[str]  # Source port
    dst_port: Optional[str]  # Destination port
    comment: Optional[str]  # Rule comment
    disabled: Optional[bool]  # Whether rule is disabled
    log: Optional[bool]  # Whether to log matching packets
    log_prefix: Optional[str]  # Log prefix for matching packets

class GetFirewallRulesArgs(TypedDict, total=False):
    """
    Arguments for retrieving firewall rules from MikroTik API.
    
    Reference: MikroTik RouterOS API documentation for firewall management
    """
    chain: Optional[str]  # Filter by rule chain
    action: Optional[str]  # Filter by rule action
    src_address: Optional[str]  # Filter by source address
    dst_address: Optional[str]  # Filter by destination address
    protocol: Optional[str]  # Filter by protocol
    disabled: Optional[bool]  # Filter by disabled status
    comment: Optional[str]  # Filter by comment
