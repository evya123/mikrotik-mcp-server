"""
MikroTik Base Type Definitions

This module contains base type definitions used across all MikroTik API modules.
"""
from typing import TypedDict, Optional


class MikroTikConfig(TypedDict, total=False):
    """
    Configuration for MikroTik API connection.
    
    All fields except host, username, and password are optional.
    """
    host: str  # MikroTik device IP address or hostname
    username: str  # Username for authentication
    password: str  # Password for authentication
    port: Optional[int]  # Port number (defaults to 80 for HTTP, 443 for HTTPS)
    useSSL: Optional[bool]  # Whether to use HTTPS (defaults to False)
