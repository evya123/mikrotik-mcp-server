"""
Test the improved MCP server features and error handling.
"""
import pytest
import sys
import os
import json
from unittest.mock import Mock, AsyncMock, patch

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from python_src.server.server import (
    server, 
    handle_call_tool, 
    handle_read_resource,
    server_lifespan
)


@pytest.mark.asyncio
async def test_improved_tool_descriptions():
    """Test that tools have improved, more descriptive descriptions."""
    from python_src.server.server import handle_list_tools
    tools = await handle_list_tools()
    
    # Check that descriptions are more informative
    get_logs_tool = next((t for t in tools if t.name == "get_logs"), None)
    assert get_logs_tool is not None
    assert "filtering and formatting options" in get_logs_tool.description
    
    test_connection_tool = next((t for t in tools if t.name == "test_connection"), None)
    assert test_connection_tool is not None
    assert "verify authentication" in test_connection_tool.description


@pytest.mark.asyncio
async def test_improved_resource_descriptions():
    """Test that resources have improved, more descriptive descriptions."""
    from python_src.server.server import handle_list_resources
    resources = await handle_list_resources()
    
    # Check that descriptions are more informative
    recent_logs = next((r for r in resources if r.name == "recent_logs"), None)
    assert recent_logs is not None
    assert "basic information" in recent_logs.description
    
    system_info = next((r for r in resources if r.name == "system_info"), None)
    assert system_info is not None
    assert "resource usage" in system_info.description


@pytest.mark.asyncio
async def test_prompt_metadata_improvements():
    """Test that prompts have improved metadata and descriptions."""
    from python_src.server.server import handle_list_prompts
    prompts = await handle_list_prompts()
    
    # Check that prompts have titles
    analyze_logs = next((p for p in prompts if p.name == "analyze_logs"), None)
    assert analyze_logs is not None
    assert analyze_logs.title == "Analyze Logs"
    assert "comprehensive" in analyze_logs.description
    
    system_health = next((p for p in prompts if p.name == "system_health_check"), None)
    assert system_health is not None
    assert system_health.title == "System Health Check"
    assert "performance" in system_health.description


@pytest.mark.asyncio
async def test_server_capabilities():
    """Test that the server declares proper capabilities."""
    from mcp.server.lowlevel import NotificationOptions
    
    capabilities = server.get_capabilities(
        notification_options=NotificationOptions(),
        experimental_capabilities={}
    )
    
    # Check that basic capabilities are present
    assert hasattr(capabilities, 'tools')
    assert hasattr(capabilities, 'resources')
    assert hasattr(capabilities, 'prompts')
    
    # Check that tools capability has proper feature flags
    if hasattr(capabilities.tools, 'listChanged'):
        assert capabilities.tools.listChanged is not None
    
    # Check that resources capability has proper feature flags
    if hasattr(capabilities.resources, 'subscribeListChanged'):
        assert capabilities.resources.subscribeListChanged is not None


@pytest.mark.asyncio
async def test_lifespan_context_management():
    """Test that the server lifespan properly manages context."""
    # Test lifespan context creation
    async with server_lifespan(server) as context:
        assert "mikrotik_client" in context
        # Client might be None if no config, which is expected behavior


@pytest.mark.asyncio
async def test_tool_schema_validation():
    """Test that tool schemas are properly structured and validated."""
    from python_src.server.server import handle_list_tools
    tools = await handle_list_tools()
    
    for tool in tools:
        schema = tool.inputSchema
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Check that all properties have descriptions
        for prop_name, prop_def in schema["properties"].items():
            assert "description" in prop_def, f"Property {prop_name} missing description"
            assert "type" in prop_def, f"Property {prop_name} missing type"


@pytest.mark.asyncio
async def test_resource_uri_consistency():
    """Test that resource URIs follow consistent patterns."""
    from python_src.server.server import handle_list_resources
    resources = await handle_list_resources()
    
    for resource in resources:
        # All URIs should start with mikrotik://
        uri_str = str(resource.uri)
        assert uri_str.startswith("mikrotik://"), f"Invalid URI format: {uri_str}"
        
        # URIs should have proper structure
        parts = uri_str.replace("mikrotik://", "").split("/")
        assert len(parts) >= 2, f"URI should have at least category and type: {uri_str}"
        
        # Check that category is valid
        valid_categories = ["logs", "system"]
        assert parts[0] in valid_categories, f"Invalid category in URI: {uri_str}"


@pytest.mark.asyncio
async def test_tool_schemas():
    """Test that tools have proper JSON schemas."""
    from python_src.server.server import handle_list_tools
    tools = await handle_list_tools()
    
    # Test get_logs tool has comprehensive schema
    get_logs_tool = next((t for t in tools if t.name == "get_logs"), None)
    assert get_logs_tool is not None, "get_logs tool not found"
    
    schema = get_logs_tool.inputSchema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "where" in schema["properties"]
    assert "brief" in schema["properties"]
    assert "countOnly" in schema["properties"]
    
    # Test get_logs_from_buffer has required field
    buffer_tool = next((t for t in tools if t.name == "get_logs_from_buffer"), None)
    assert buffer_tool is not None, "get_logs_from_buffer tool not found"
    
    buffer_schema = buffer_tool.inputSchema
    assert "required" in buffer_schema
    assert "bufferName" in buffer_schema["required"]


@pytest.mark.asyncio
async def test_resource_metadata():
    """Test that resources have consistent and useful metadata."""
    from python_src.server.server import handle_list_resources
    resources = await handle_list_resources()
    
    # Test that all resources have consistent naming patterns
    for resource in resources:
        # Names should be snake_case
        assert "_" in resource.name or resource.name.islower(), f"Resource {resource.uri} has invalid name format"
        
        # Titles should be Title Case
        assert resource.title[0].isupper(), f"Resource {resource.uri} title should start with capital"
        
        # Descriptions should be informative
        assert len(resource.description) > 20, f"Resource {resource.uri} description too short"


if __name__ == "__main__":
    pytest.main([__file__])
