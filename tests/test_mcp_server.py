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


# Enhanced tests from improvements
@pytest.mark.asyncio
async def test_improved_tool_descriptions():
    """Test that tools have improved, more descriptive descriptions."""
    from server.server import handle_list_tools
    tools = await handle_list_tools()
    
    get_logs_tool = next((t for t in tools if t.name == "get_logs"), None)
    assert get_logs_tool is not None
    assert "filtering and formatting options" in get_logs_tool.description
    
    test_connection_tool = next((t for t in tools if t.name == "test_connection"), None)
    assert test_connection_tool is not None
    assert "verify authentication" in test_connection_tool.description


@pytest.mark.asyncio
async def test_improved_resource_descriptions():
    """Test that resources have improved, more descriptive descriptions."""
    from server.server import handle_list_resources
    resources = await handle_list_resources()
    
    recent_logs = next((r for r in resources if r.name == "recent_logs"), None)
    assert recent_logs is not None
    assert "basic information" in recent_logs.description
    
    system_info = next((r for r in resources if r.name == "system_info"), None)
    assert system_info is not None
    assert "resource usage" in system_info.description


@pytest.mark.asyncio
async def test_prompt_metadata_improvements():
    """Test that prompts have improved metadata and descriptions."""
    from server.server import handle_list_prompts
    prompts = await handle_list_prompts()
    
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
    from server.server import server_lifespan
    
    # Test lifespan context creation
    async with server_lifespan(server) as context:
        assert "mikrotik_client" in context
        # Client might be None if no config, which is expected behavior


@pytest.mark.asyncio
async def test_tool_schema_validation():
    """Test that tool schemas are properly structured and validated."""
    from server.server import handle_list_tools
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
    from server.server import handle_list_resources
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


# Additional coverage tests
@pytest.mark.asyncio
async def test_server_configuration_validation():
    """Test that server configuration is properly validated."""
    # Test server name format
    assert server.name == "mikrotik-routeros-server"
    assert len(server.name) > 0
    assert "mikrotik" in server.name.lower()
    
    # Test server has required attributes
    assert hasattr(server, 'name')
    assert hasattr(server, 'get_capabilities')


@pytest.mark.asyncio
async def test_mcp_primitive_counts():
    """Test that the server exposes the expected number of MCP primitives."""
    from server.server import handle_list_tools, handle_list_resources, handle_list_prompts
    
    tools = await handle_list_tools()
    resources = await handle_list_resources()
    prompts = await handle_list_prompts()
    
    # Verify we have the expected number of primitives
    assert len(tools) >= 8, f"Expected at least 8 tools, got {len(tools)}"
    assert len(resources) >= 7, f"Expected at least 7 resources, got {len(resources)}"
    assert len(prompts) >= 3, f"Expected at least 3 prompts, got {len(prompts)}"


@pytest.mark.asyncio
async def test_error_response_format():
    """Test that error responses follow proper MCP format."""
    from server.server import handle_call_tool
    
    # Test with invalid tool name
    result = await handle_call_tool("nonexistent_tool", {})
    
    # Should return list of content items
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Should contain text content
    assert any(hasattr(content, 'text') for content in result)
    
    # Check error message content
    error_text = "".join(
        content.text for content in result 
        if hasattr(content, 'text')
    )
    assert len(error_text) > 0, "Error response should contain text"


if __name__ == "__main__":
    pytest.main([__file__])
