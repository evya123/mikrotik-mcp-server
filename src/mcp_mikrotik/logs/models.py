"""
MikroTik Logs Type Definitions

This module contains type definitions for log-related operations in the MikroTik API.
"""
from typing import Dict, List, Optional, TypedDict, Any, Union


class MikroTikLogEntry(TypedDict, total=False):
    """
    MikroTik log entry structure.
    
    Based on MikroTik RouterOS API documentation for /log/print endpoint.
    """
    time: str  # Timestamp of the log entry
    topics: str  # Log topics/categories
    message: str  # Log message content
    level: Optional[str]  # Log level (info, warning, error, etc.)
    extra_info: Optional[str]  # Additional information (if available)
    buffer: Optional[str]  # Buffer name for separate memory logging buffers


class GetLogsArgs(TypedDict, total=False):
    """
    Arguments for retrieving logs from MikroTik API.
    
    All parameters are optional and correspond to MikroTik RouterOS API parameters.
    """
    append: Optional[bool]  # Append to existing log output
    brief: Optional[bool]  # Return brief log information
    countOnly: Optional[bool]  # Return only count of logs
    detail: Optional[bool]  # Return detailed log information
    file: Optional[str]  # Log file to read from
    follow: Optional[bool]  # Follow logs in real-time
    followOnly: Optional[bool]  # Follow logs only (no initial output)
    groupBy: Optional[str]  # Group logs by specified field
    interval: Optional[int]  # Interval for grouped logs
    proplist: Optional[List[str]]  # List of properties to return
    showIds: Optional[bool]  # Show log entry IDs
    terse: Optional[bool]  # Return terse output
    where: Optional[str]  # Filter condition for logs
    withExtraInfo: Optional[bool]  # Include extra information in log output
    withoutPaging: Optional[bool]  # Return all results without paging


class GetLogsByConditionArgs(TypedDict, total=False):
    """
    Arguments for retrieving logs by condition from MikroTik API.
    
    Extends GetLogsArgs with a required condition field.
    """
    condition: str  # Filter condition (e.g., 'topics~"system"')
    append: Optional[bool]
    brief: Optional[bool]
    countOnly: Optional[bool]
    detail: Optional[bool]
    file: Optional[str]
    follow: Optional[bool]
    followOnly: Optional[bool]
    groupBy: Optional[str]
    interval: Optional[int]
    proplist: Optional[List[str]]
    showIds: Optional[bool]
    terse: Optional[bool]
    withExtraInfo: Optional[bool]
    withoutPaging: Optional[bool]


def is_valid_get_logs_args(args: Any) -> bool:
    """
    Validate that the provided arguments match the GetLogsArgs structure.
    
    Args:
        args: The arguments to validate
        
    Returns:
        bool: True if arguments are valid, False otherwise
    """
    if not isinstance(args, dict):
        return False
        
    # Check each field for correct type
    type_checks = {
        'append': bool,
        'brief': bool,
        'countOnly': bool,
        'detail': bool,
        'file': str,
        'follow': bool,
        'followOnly': bool,
        'groupBy': str,
        'interval': (int, float),
        'proplist': list,
        'showIds': bool,
        'terse': bool,
        'where': str,
        'withExtraInfo': bool,
        'withoutPaging': bool
    }
    
    for field, expected_type in type_checks.items():
        if field in args and not isinstance(args[field], expected_type):
            return False
            
    return True


def is_valid_get_logs_by_condition_args(args: Any) -> bool:
    """
    Validate that the provided arguments match the GetLogsByConditionArgs structure.
    
    Args:
        args: The arguments to validate
        
    Returns:
        bool: True if arguments are valid, False otherwise
    """
    if not isinstance(args, dict) or 'condition' not in args:
        return False
        
    if not isinstance(args['condition'], str):
        return False
        
    # Check each field for correct type
    type_checks = {
        'append': bool,
        'brief': bool,
        'countOnly': bool,
        'detail': bool,
        'file': str,
        'follow': bool,
        'followOnly': bool,
        'groupBy': str,
        'interval': (int, float),
        'proplist': list,
        'showIds': bool,
        'terse': bool,
        'withExtraInfo': bool,
        'withoutPaging': bool
    }
    
    for field, expected_type in type_checks.items():
        if field in args and not isinstance(args[field], expected_type):
            return False
            
    return True
