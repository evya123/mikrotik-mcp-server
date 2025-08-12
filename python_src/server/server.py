"""
MikroTik MCP Server

This module provides a Model Context Protocol server for MikroTik RouterOS
using the official MCP Python SDK.
"""
import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dotenv import load_dotenv

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Use absolute imports
from python_src.client.mikrotik import MikroTikClient
from python_src.types.models import MikroTikConfig, is_valid_get_logs_args

# Load environment variables from .env file (non-fatal; actual config is read at runtime)
load_dotenv()

def load_mikrotik_config() -> MikroTikConfig:
    """
    Load MikroTik configuration from environment variables.
    
    Returns:
        MikroTikConfig: Configuration dictionary
        
    Raises:
        ValueError: If required configuration is missing
    """
    config = {
        "host": os.environ.get("MIKROTIK_HOST", "192.168.88.1"),
        "username": os.environ.get("MIKROTIK_USERNAME", "admin"),
        "password": os.environ.get("MIKROTIK_PASSWORD", ""),
        "port": int(os.environ.get("MIKROTIK_PORT")) if os.environ.get("MIKROTIK_PORT") else None,
        "useSSL": os.environ.get("MIKROTIK_USE_SSL", "false").lower() == "true",
    }
    
    return config

# Create the MCP server instance with proper metadata
server = Server("mikrotik-routeros-server")


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    """
    Manage server startup and shutdown lifecycle.
    
    This function initializes the MikroTik client on startup and ensures
    proper cleanup on shutdown.
    
    Args:
        server: The MCP server instance
        
    Yields:
        Dict containing initialized resources (MikroTik client)
    """
    # Initialize MikroTik client on startup (lazily, tolerant of missing env)
    mikrotik_client: Optional[MikroTikClient] = None
    config = load_mikrotik_config()
    if config.get("password"):
        try:
            mikrotik_client = MikroTikClient(config)
            if os.environ.get("MIKROTIK_SKIP_CONNECT_TEST", "0") != "1":
                is_connected = await mikrotik_client.test_connection()
                if not is_connected:
                    print(
                        "Warning: Could not establish connection to MikroTik device",
                        file=sys.stderr,
                    )
        except Exception as e:
            print(f"Warning: MikroTik client initialization failed: {e}", file=sys.stderr)
            mikrotik_client = None
    
    try:
        yield {"mikrotik_client": mikrotik_client}
    finally:
        # Clean up on shutdown
        # Note: MikroTik client doesn't require explicit cleanup
        pass


# Note: Lifespan is handled in the run() function


# MCP Resources
@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    List available MCP resources.
    
    Returns:
        List of available resources with their metadata
    """
    return [
        types.Resource(
            uri="mikrotik://logs/recent",
            name="recent_logs",
            title="Recent System Logs",
            description="Get recent MikroTik system logs with basic information",
            mimeType="application/json"
        ),
        types.Resource(
            uri="mikrotik://logs/debug",
            name="debug_logs", 
            title="Debug Logs",
            description="Get MikroTik debug logs for troubleshooting and development",
            mimeType="application/json"
        ),
        types.Resource(
            uri="mikrotik://logs/error",
            name="error_logs",
            title="Error Logs", 
            description="Get MikroTik error logs for system monitoring and alerting",
            mimeType="application/json"
        ),
        types.Resource(
            uri="mikrotik://logs/warning",
            name="warning_logs",
            title="Warning Logs",
            description="Get MikroTik warning logs for proactive system monitoring",
            mimeType="application/json"
        ),
        types.Resource(
            uri="mikrotik://logs/info",
            name="info_logs",
            title="Info Logs",
            description="Get MikroTik informational logs for general system status",
            mimeType="application/json"
        ),
        types.Resource(
            uri="mikrotik://logs/detailed",
            name="detailed_logs",
            title="Detailed Logs",
            description="Get detailed MikroTik logs with extra information and metadata",
            mimeType="application/json"
        ),
        types.Resource(
            uri="mikrotik://system/info",
            name="system_info",
            title="System Information",
            description="Get current system information and resource usage from MikroTik device",
            mimeType="application/json"
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> tuple[bytes, str]:
    """
    Read a resource by URI.
    
    Args:
        uri: The resource URI to read
        
    Returns:
        Tuple of (content_bytes, mime_type)
        
    Raises:
        ValueError: If the resource URI is unknown or an error occurs
    """
    ctx = server.request_context
    mikrotik_client = ctx.lifespan_context["mikrotik_client"]
    
    if not mikrotik_client:
        raise ValueError("MikroTik client not available - check configuration")
    
    try:
        if uri == "mikrotik://logs/recent":
            logs = await mikrotik_client.get_logs({"brief": True})
            return json.dumps(logs, indent=2).encode('utf-8'), "application/json"
        
        elif uri == "mikrotik://logs/debug":
            logs = await mikrotik_client.get_debug_logs()
            return json.dumps(logs, indent=2).encode('utf-8'), "application/json"
        
        elif uri == "mikrotik://logs/error":
            logs = await mikrotik_client.get_error_logs()
            return json.dumps(logs, indent=2).encode('utf-8'), "application/json"
        
        elif uri == "mikrotik://logs/warning":
            logs = await mikrotik_client.get_warning_logs()
            return json.dumps(logs, indent=2).encode('utf-8'), "application/json"
        
        elif uri == "mikrotik://logs/info":
            logs = await mikrotik_client.get_info_logs()
            return json.dumps(logs, indent=2).encode('utf-8'), "application/json"
        
        elif uri == "mikrotik://logs/detailed":
            logs = await mikrotik_client.get_logs_with_extra_info({"brief": True})
            return json.dumps(logs, indent=2).encode('utf-8'), "application/json"
        
        elif uri == "mikrotik://system/info":
            system_info = await mikrotik_client.get_system_info()
            return json.dumps(system_info, indent=2).encode('utf-8'), "application/json"
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    except Exception as e:
        error_msg = f"Error reading resource {uri}: {str(e)}"
        raise ValueError(error_msg)


# MCP Tools
@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available MCP tools.
    
    Returns:
        List of available tools with their schemas
    """
    return [
        types.Tool(
            name="get_logs",
            title="Get System Logs",
            description="Retrieve MikroTik system logs with optional filtering and formatting options",
            inputSchema={
                "type": "object",
                "properties": {
                    "append": {"type": "boolean", "description": "Append to existing log output"},
                    "brief": {"type": "boolean", "description": "Return brief log information"},
                    "countOnly": {"type": "boolean", "description": "Return only count of logs"},
                    "detail": {"type": "boolean", "description": "Return detailed log information"},
                    "file": {"type": "string", "description": "Log file to read from"},
                    "follow": {"type": "boolean", "description": "Follow logs in real-time"},
                    "followOnly": {"type": "boolean", "description": "Follow logs only (no initial output)"},
                    "groupBy": {"type": "string", "description": "Group logs by specified field"},
                    "interval": {"type": "integer", "description": "Interval for grouped logs"},
                    "proplist": {"type": "array", "items": {"type": "string"}, "description": "List of properties to return"},
                    "showIds": {"type": "boolean", "description": "Show log entry IDs"},
                    "terse": {"type": "boolean", "description": "Return terse output"},
                    "where": {"type": "string", "description": "Filter condition for logs (e.g., topics~\"system\")"},
                    "withExtraInfo": {"type": "boolean", "description": "Include extra information in log output"},
                    "withoutPaging": {"type": "boolean", "description": "Return all results without paging"}
                }
            }
        ),
        types.Tool(
            name="get_debug_logs",
            title="Get Debug Logs",
            description="Retrieve MikroTik debug logs for troubleshooting and development purposes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_error_logs",
            title="Get Error Logs",
            description="Retrieve MikroTik error logs for system monitoring and alerting",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_warning_logs",
            title="Get Warning Logs",
            description="Retrieve MikroTik warning logs for proactive system monitoring",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_info_logs",
            title="Get Info Logs",
            description="Retrieve MikroTik informational logs for general system status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_logs_from_buffer",
            title="Get Logs from Buffer",
            description="Retrieve logs from a specific memory buffer on the MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "bufferName": {"type": "string", "description": "Name of the buffer to read from"},
                    "append": {"type": "boolean", "description": "Append to existing log output"},
                    "brief": {"type": "boolean", "description": "Return brief log information"},
                    "countOnly": {"type": "boolean", "description": "Return only count of logs"},
                    "detail": {"type": "boolean", "description": "Return detailed log information"},
                    "file": {"type": "string", "description": "Log file to read from"},
                    "follow": {"type": "boolean", "description": "Follow logs in real-time"},
                    "followOnly": {"type": "boolean", "description": "Follow logs only (no initial output)"},
                    "groupBy": {"type": "string", "description": "Group logs by specified field"},
                    "interval": {"type": "integer", "description": "Interval for grouped logs"},
                    "proplist": {"type": "array", "items": {"type": "string"}, "description": "List of properties to return"},
                    "showIds": {"type": "boolean", "description": "Show log entry IDs"},
                    "terse": {"type": "boolean", "description": "Return terse output"},
                    "withExtraInfo": {"type": "boolean", "description": "Include extra information in log output"},
                    "withoutPaging": {"type": "boolean", "description": "Return all results without paging"}
                },
                "required": ["bufferName"]
            }
        ),
        types.Tool(
            name="get_logs_with_extra_info",
            title="Get Logs with Extra Info",
            description="Retrieve MikroTik logs with additional metadata and context information",
            inputSchema={
                "type": "object",
                "properties": {
                    "append": {"type": "boolean", "description": "Append to existing log output"},
                    "brief": {"type": "boolean", "description": "Return brief log information"},
                    "countOnly": {"type": "boolean", "description": "Return only count of logs"},
                    "detail": {"type": "boolean", "description": "Return detailed log information"},
                    "file": {"type": "string", "description": "Log file to read from"},
                    "follow": {"type": "boolean", "description": "Follow logs in real-time"},
                    "followOnly": {"type": "boolean", "description": "Follow logs only (no initial output)"},
                    "groupBy": {"type": "string", "description": "Group logs by specified field"},
                    "interval": {"type": "integer", "description": "Interval for grouped logs"},
                    "proplist": {"type": "array", "items": {"type": "string"}, "description": "List of properties to return"},
                    "showIds": {"type": "boolean", "description": "Show log entry IDs"},
                    "terse": {"type": "boolean", "description": "Return terse output"},
                    "where": {"type": "string", "description": "Filter condition for logs"},
                    "withExtraInfo": {"type": "boolean", "description": "Include extra information in log output"},
                    "withoutPaging": {"type": "boolean", "description": "Return all results without paging"}
                }
            }
        ),
        types.Tool(
            name="test_connection",
            title="Test Connection",
            description="Test the connection to the MikroTik device and verify authentication",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Handle MCP tool calls.
    
    Args:
        name: Name of the tool to call
        arguments: Tool arguments
        
    Returns:
        List of tool results as content objects
        
    Raises:
        ValueError: If the tool name is unknown or an error occurs
    """
    ctx = server.request_context
    mikrotik_client = ctx.lifespan_context["mikrotik_client"]
    
    if not mikrotik_client:
        return [types.TextContent(
            type="text", 
            text="Error: MikroTik client not available. Please check your configuration."
        )]
    
    try:
        if name == "get_logs":
            if not is_valid_get_logs_args(arguments):
                raise ValueError("Invalid arguments for get_logs tool")
            
            logs = await mikrotik_client.get_logs(arguments)
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "get_debug_logs":
            logs = await mikrotik_client.get_debug_logs()
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "get_error_logs":
            logs = await mikrotik_client.get_error_logs()
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "get_warning_logs":
            logs = await mikrotik_client.get_warning_logs()
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "get_info_logs":
            logs = await mikrotik_client.get_info_logs()
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "get_logs_from_buffer":
            buffer_name = arguments.get("bufferName")
            if not buffer_name:
                raise ValueError("bufferName is required")
            
            # Build options dict, excluding bufferName
            options = {k: v for k, v in arguments.items() if k != "bufferName" and v is not None}
            logs = await mikrotik_client.get_logs_from_buffer(buffer_name, options)
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "get_logs_with_extra_info":
            # Build arguments dict
            args = {k: v for k, v in arguments.items() if v is not None}
            logs = await mikrotik_client.get_logs_with_extra_info(args)
            return [types.TextContent(type="text", text=json.dumps(logs, indent=2))]
        
        elif name == "test_connection":
            is_connected = await mikrotik_client.test_connection()
            if is_connected:
                return [types.TextContent(type="text", text="✅ Connection to MikroTik device successful")]
            else:
                return [types.TextContent(type="text", text="❌ Connection to MikroTik device failed")]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        error_msg = f"Error calling tool {name}: {str(e)}"
        return [types.TextContent(type="text", text=f"❌ {error_msg}")]


# MCP Prompts
@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """
    List available MCP prompts.
    
    Returns:
        List of available prompts with their arguments
    """
    return [
        types.Prompt(
            name="analyze_logs",
            title="Analyze Logs",
            description="Generate a comprehensive prompt for analyzing MikroTik logs with specific criteria",
            arguments=[
                types.PromptArgument(
                    name="log_type",
                    description="Type of logs to analyze (recent, debug, error, warning, info)",
                    required=False
                ),
                types.PromptArgument(
                    name="filter_criteria",
                    description="Optional filter criteria for the logs",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="system_health_check",
            title="System Health Check",
            description="Generate a comprehensive prompt for checking MikroTik system health and performance",
            arguments=[]
        ),
        types.Prompt(
            name="troubleshooting_guide",
            title="Troubleshooting Guide",
            description="Generate a detailed troubleshooting prompt for specific MikroTik issues",
            arguments=[
                types.PromptArgument(
                    name="issue_description",
                    description="Description of the issue to troubleshoot",
                    required=True
                )
            ]
        ),
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
    """
    Get a prompt by name.
    
    Args:
        name: Name of the prompt to retrieve
        arguments: Optional arguments for the prompt
        
    Returns:
        GetPromptResult containing the prompt content
        
    Raises:
        ValueError: If the prompt name is unknown
    """
    if arguments is None:
        arguments = {}
    
    if name == "analyze_logs":
        log_type = arguments.get("log_type", "recent")
        filter_criteria = arguments.get("filter_criteria", "")
        
        base_prompt = f"Please analyze the MikroTik {log_type} logs"
        if filter_criteria:
            base_prompt += f" with the following criteria: {filter_criteria}"
        
        base_prompt += ". Look for any patterns, anomalies, or issues that might need attention. Provide a summary of your findings and any recommendations for system maintenance or troubleshooting."
        
        return types.GetPromptResult(
            description=f"Analyze {log_type} logs",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=base_prompt),
                ),
            ],
        )
    
    elif name == "system_health_check":
        prompt_text = """Please perform a comprehensive health check of the MikroTik RouterOS system. 
        
Analyze the system information, recent logs, and any error or warning messages to assess the overall health and performance of the device. 

Look for:
- System resource usage and performance
- Any recurring errors or warnings
- Network connectivity issues
- Security-related events
- Hardware or software problems

Provide a detailed health assessment with recommendations for any issues found."""
        
        return types.GetPromptResult(
            description="System health check",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                ),
            ],
        )
    
    elif name == "troubleshooting_guide":
        issue_description = arguments.get("issue_description", "")
        
        prompt_text = f"""Based on the following issue description, please provide a comprehensive troubleshooting guide for the MikroTik RouterOS device:

Issue: {issue_description}

Please provide:
1. A step-by-step troubleshooting procedure
2. Relevant log entries to check
3. Common causes and solutions
4. When to escalate or contact support
5. Preventive measures to avoid similar issues

Use the available tools and resources to gather relevant information and provide specific, actionable guidance."""
        
        return types.GetPromptResult(
            description="Troubleshooting guide",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                ),
            ],
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def run() -> None:
    """
    Run the MCP server with stdio transport.
    
    This function sets up the stdio transport and runs the server
    with proper initialization options and capabilities.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        async with server_lifespan(server):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mikrotik-routeros-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={
                            "logging": {
                                "level": "info",
                                "format": "json"
                            }
                        },
                    ),
                ),
            )


def main() -> None:
    """
    Main entry point for the MCP server.
    
    This function initializes the server and runs it with the stdio transport.
    """
    print("MikroTik MCP server starting...", file=sys.stderr)
    
    # Run the MCP server
    asyncio.run(run())


if __name__ == "__main__":
    main()
