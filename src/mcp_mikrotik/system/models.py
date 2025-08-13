"""
MikroTik System Type Definitions

This module contains type definitions for system-related operations in the MikroTik API.
"""
from typing import TypedDict, Optional, Any


class MikroTikSystemInfo(TypedDict, total=False):
    """
    MikroTik system information structure.
    
    Based on MikroTik RouterOS API documentation for /system/resource/print endpoint.
    """
    uptime: str  # System uptime
    version: str  # RouterOS version
    board_name: str  # Board name/model
    cpu_count: int  # Number of CPU cores
    cpu_frequency: int  # CPU frequency in MHz
    cpu_load: int  # Current CPU load percentage
    free_hdd_space: int  # Free hard disk space in bytes
    total_hdd_space: int  # Total hard disk space in bytes
    free_memory: int  # Free memory in bytes
    total_memory: int  # Total memory in bytes
    architecture_name: str  # System architecture
    platform: str  # Hardware platform


class MikroTikResourceInfo(TypedDict, total=False):
    """
    MikroTik resource information structure.
    
    Based on MikroTik RouterOS API documentation for /system/resource/print endpoint.
    """
    ret: list[MikroTikSystemInfo]  # List of system info entries
