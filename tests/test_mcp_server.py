"""
Test the MikroTik MCP Server implementation.
"""
import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from server.server import server


def test_server_initialization():
    """Test that the MCP server is properly initialized."""
    assert server is not None
    assert server.name == "mikrotik-routeros-server"


@pytest.mark.asyncio
async def test_server_has_resources():
    """Test that the server has the expected resources with proper metadata."""
    # Get the server's resources using the handler
    from server.server import handle_list_resources
    resources = await handle_list_resources()
    
    expected_resources = [
        "mikrotik://logs/recent",
        "mikrotik://logs/debug", 
        "mikrotik://logs/error",
        "mikrotik://logs/warning",
        "mikrotik://logs/info",
        "mikrotik://logs/detailed",
        "mikrotik://system/info"
    ]
    
    # Extract URIs from resources
    actual_uris = [str(resource.uri) for resource in resources]
    
    for expected_uri in expected_resources:
        assert expected_uri in actual_uris, f"Missing resource: {expected_uri}"
    
    # Test that resources have proper titles and descriptions
    for resource in resources:
        assert resource.title is not None, f"Resource {resource.uri} missing title"
        assert resource.description is not None, f"Resource {resource.uri} missing description"
        assert resource.name is not None, f"Resource {resource.uri} missing name"
        assert resource.mimeType == "application/json", f"Resource {resource.uri} has wrong mime type"


@pytest.mark.asyncio
async def test_server_has_tools():
    """Test that the server has the expected tools with proper metadata."""
    # Get the server's tools using the handler
    from server.server import handle_list_tools
    tools = await handle_list_tools()
    
    expected_tools = [
        "get_logs",
        "get_debug_logs",
        "get_error_logs", 
        "get_warning_logs",
        "get_info_logs",
        "get_logs_from_buffer",
        "get_logs_with_extra_info",
        "test_connection"
    ]
    
    # Extract tool names from the response
    actual_tool_names = [tool.name for tool in tools]
    
    for expected_tool in expected_tools:
        assert expected_tool in actual_tool_names, f"Missing tool: {expected_tool}"
    
    # Test that tools have proper titles and descriptions
    for tool in tools:
        assert tool.title is not None, f"Tool {tool.name} missing title"
        assert tool.description is not None, f"Tool {tool.name} missing description"
        assert tool.inputSchema is not None, f"Tool {tool.name} missing input schema"


@pytest.mark.asyncio
async def test_server_has_prompts():
    """Test that the server has the expected prompts with proper metadata."""
    # Get the server's prompts using the handler
    from server.server import handle_list_prompts
    prompts = await handle_list_prompts()
    
    expected_prompts = [
        "analyze_logs",
        "system_health_check",
        "troubleshooting_guide"
    ]
    
    # Extract prompt names from the response
    actual_prompt_names = [prompt.name for prompt in prompts]
    
    for expected_prompt in expected_prompts:
        assert expected_prompt in actual_prompt_names, f"Missing prompt: {expected_prompt}"
    
    # Test that prompts have proper titles and descriptions
    for prompt in prompts:
        assert prompt.title is not None, f"Prompt {prompt.name} missing title"
        assert prompt.description is not None, f"Prompt {prompt.name} missing description"


@pytest.mark.asyncio
async def test_tool_schemas():
    """Test that tools have proper JSON schemas."""
    from server.server import handle_list_tools
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
    from server.server import handle_list_resources
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
