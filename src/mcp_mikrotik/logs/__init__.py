"""
MikroTik Logs Module

This module provides specialized client functionality for MikroTik log management.
"""

from .client import MikroTikLogsClient
from .models import (
    MikroTikLogEntry,
    GetLogsArgs,
    GetLogsByConditionArgs,
    is_valid_get_logs_args,
    is_valid_get_logs_by_condition_args
)

__all__ = [
    "MikroTikLogsClient",
    "MikroTikLogEntry",
    "GetLogsArgs",
    "GetLogsByConditionArgs",
    "is_valid_get_logs_args",
    "is_valid_get_logs_by_condition_args"
]
