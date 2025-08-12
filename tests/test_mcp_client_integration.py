#!/usr/bin/env python3
"""
MCP Protocol Compliance Tests

These tests verify that the server properly implements the MCP protocol
without requiring actual server process spawning.
"""
import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock, patch

# Ensure project root on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
sys.path.insert(0, PROJECT_ROOT)

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_SDK_INTEGRATION") != "1",
    reason="Set RUN_SDK_INTEGRATION=1 to run MCP protocol compliance tests.",
)


@pytest.mark.asyncio
async def test_mcp_protocol_compliance():
    """Test that the server properly implements MCP protocol requirements."""
    from server.server import server
    from mcp.server.lowlevel import NotificationOptions
    
    # Test server initialization
    assert server is not None
    assert server.name == "mikrotik-routeros-server"
    
    # Test capability declaration
    capabilities = server.get_capabilities(
        notification_options=NotificationOptions(),
        experimental_capabilities={}
    )
    
    # Verify required capabilities are present
    assert hasattr(capabilities, 'tools')
    assert hasattr(capabilities, 'resources')
    assert hasattr(capabilities, 'prompts')
    
    # Verify tools capability structure
    assert capabilities.tools is not None
    assert hasattr(capabilities.tools, 'listChanged')
    
    # Verify resources capability structure
    assert capabilities.resources is not None
    assert hasattr(capabilities.resources, 'subscribeListChanged')
    
    # Verify prompts capability structure
    assert capabilities.prompts is not None


@pytest.mark.asyncio
async def test_mcp_primitive_discovery():
    """Test that the server properly exposes MCP primitives (tools, resources, prompts)."""
    from server.server import (
        handle_list_tools, 
        handle_list_resources, 
        handle_list_prompts
    )
    
    # Test tools discovery
    tools = await handle_list_tools()
    assert len(tools) > 0, "Server should expose at least one tool"
    
    # Verify tool structure
    for tool in tools:
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'title')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'inputSchema')
        assert tool.name is not None
        assert tool.title is not None
        assert tool.description is not None
        assert tool.inputSchema is not None
    
    # Test resources discovery
    resources = await handle_list_resources()
    assert len(resources) > 0, "Server should expose at least one resource"
    
    # Verify resource structure
    for resource in resources:
        assert hasattr(resource, 'uri')
        assert hasattr(resource, 'name')
        assert hasattr(resource, 'title')
        assert hasattr(resource, 'description')
        assert hasattr(resource, 'mimeType')
        assert resource.uri is not None
        assert resource.name is not None
        assert resource.title is not None
        assert resource.description is not None
        assert resource.mimeType is not None
    
    # Test prompts discovery
    prompts = await handle_list_prompts()
    assert len(prompts) > 0, "Server should expose at least one prompt"
    
    # Verify prompt structure
    for prompt in prompts:
        assert hasattr(prompt, 'name')
        assert hasattr(prompt, 'title')
        assert hasattr(prompt, 'description')
        assert hasattr(prompt, 'messages')
        assert prompt.name is not None
        assert prompt.title is not None
        assert prompt.description is not None
        assert prompt.messages is not None


@pytest.mark.asyncio
async def test_mcp_schema_validation():
    """Test that MCP primitives have valid schemas and metadata."""
    from server.server import handle_list_tools
    
    tools = await handle_list_tools()
    
    for tool in tools:
        schema = tool.inputSchema
        
        # Verify schema structure
        assert schema["type"] == "object", f"Tool {tool.name} schema must be object type"
        assert "properties" in schema, f"Tool {tool.name} schema must have properties"
        
        # Verify all properties have required fields
        for prop_name, prop_def in schema["properties"].items():
            assert "type" in prop_def, f"Property {prop_name} in {tool.name} missing type"
            assert "description" in prop_def, f"Property {prop_name} in {tool.name} missing description"
            
            # Verify type is valid
            valid_types = ["string", "boolean", "number", "integer", "array", "object"]
            assert prop_def["type"] in valid_types, f"Property {prop_name} in {tool.name} has invalid type: {prop_def['type']}"


@pytest.mark.asyncio
async def test_mcp_error_handling():
    """Test that the server handles errors gracefully according to MCP protocol."""
    from server.server import handle_call_tool
    
    # Test tool call with invalid tool name
    with patch('server.server.mikrotik_client', None):
        result = await handle_call_tool("invalid_tool", {})
        
        # Should return error content
        assert len(result) > 0
        assert any(hasattr(content, 'text') for content in result)
        
        # Check for error message
        error_text = "".join(
            content.text for content in result 
            if hasattr(content, 'text')
        )
        assert "not available" in error_text.lower() or "error" in error_text.lower()


if __name__ == "__main__":
    pytest.main([__file__])


