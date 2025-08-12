"""
MikroTik API Type Definitions

This module contains type definitions for the MikroTik API client and MCP server.
"""
from typing import Dict, List, Optional, TypedDict, Any, Union, TypeVar, Generic


class MikroTikConfig(TypedDict, total=False):
    """Configuration for MikroTik API connection."""
    host: str
    username: str
    password: str
    port: Optional[int]
    useSSL: Optional[bool]


class MikroTikLogEntry(TypedDict, total=False):
    """MikroTik log entry structure."""
    time: str
    topics: str
    message: str
    level: Optional[str]
    extra_info: Optional[str]  # Changed from "extra-info" to "extra_info" for Python compatibility
    buffer: Optional[str]


class MikroTikLogResponse(TypedDict):
    """MikroTik log response structure."""
    ret: List[MikroTikLogEntry]


T = TypeVar('T')

class MikroTikAPIResponse(TypedDict, Generic[T]):
    """Generic MikroTik API response structure."""
    ret: List[T]


class GetLogsArgs(TypedDict, total=False):
    """Arguments for retrieving logs from MikroTik API."""
    # Core parameters from MikroTik docs
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
    where: Optional[str]
    withExtraInfo: Optional[bool]
    withoutPaging: Optional[bool]


class GetLogsByConditionArgs(TypedDict, total=False):
    """Arguments for retrieving logs by condition from MikroTik API."""
    condition: str
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
    if 'append' in args and not isinstance(args['append'], bool):
        return False
    if 'brief' in args and not isinstance(args['brief'], bool):
        return False
    if 'countOnly' in args and not isinstance(args['countOnly'], bool):
        return False
    if 'detail' in args and not isinstance(args['detail'], bool):
        return False
    if 'file' in args and not isinstance(args['file'], str):
        return False
    if 'follow' in args and not isinstance(args['follow'], bool):
        return False
    if 'followOnly' in args and not isinstance(args['followOnly'], bool):
        return False
    if 'groupBy' in args and not isinstance(args['groupBy'], str):
        return False
    if 'interval' in args and not isinstance(args['interval'], (int, float)):
        return False
    if 'proplist' in args and not isinstance(args['proplist'], list):
        return False
    if 'showIds' in args and not isinstance(args['showIds'], bool):
        return False
    if 'terse' in args and not isinstance(args['terse'], bool):
        return False
    if 'where' in args and not isinstance(args['where'], str):
        return False
    if 'withExtraInfo' in args and not isinstance(args['withExtraInfo'], bool):
        return False
    if 'withoutPaging' in args and not isinstance(args['withoutPaging'], bool):
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
    if 'append' in args and not isinstance(args['append'], bool):
        return False
    if 'brief' in args and not isinstance(args['brief'], bool):
        return False
    if 'countOnly' in args and not isinstance(args['countOnly'], bool):
        return False
    if 'detail' in args and not isinstance(args['detail'], bool):
        return False
    if 'file' in args and not isinstance(args['file'], str):
        return False
    if 'follow' in args and not isinstance(args['follow'], bool):
        return False
    if 'followOnly' in args and not isinstance(args['followOnly'], bool):
        return False
    if 'groupBy' in args and not isinstance(args['groupBy'], str):
        return False
    if 'interval' in args and not isinstance(args['interval'], (int, float)):
        return False
    if 'proplist' in args and not isinstance(args['proplist'], list):
        return False
    if 'showIds' in args and not isinstance(args['showIds'], bool):
        return False
    if 'terse' in args and not isinstance(args['terse'], bool):
        return False
    if 'withExtraInfo' in args and not isinstance(args['withExtraInfo'], bool):
        return False
    if 'withoutPaging' in args and not isinstance(args['withoutPaging'], bool):
        return False
        
    return True
