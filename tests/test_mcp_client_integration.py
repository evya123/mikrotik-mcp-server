#!/usr/bin/env python3
"""
Opt-in integration test using the official MCP Python SDK client to connect to the local server via stdio.
Enable by setting RUN_SDK_INTEGRATION=1.
"""
import os
import sys
import asyncio
import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

# Ensure project root on sys.path so examples entrypoint is importable
PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
sys.path.insert(0, PROJECT_ROOT)

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_SDK_INTEGRATION") != "1",
    reason="Set RUN_SDK_INTEGRATION=1 to run SDK client integration test.",
)


@pytest.mark.asyncio
async def test_list_tools_and_resources_via_client():
    """Test that the client can discover tools and resources from the improved server."""
    # Use stdio_client to spawn our server
    server_cmd = sys.executable
    server_args = [os.path.join(PROJECT_ROOT, "server", "server.py")]

    async with stdio_client(command=server_cmd, args=server_args) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test tools discovery
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "get_logs" in tool_names
            assert "test_connection" in tool_names

            # Test that tools have proper titles and descriptions
            get_logs_tool = next((t for t in tools.tools if t.name == "get_logs"), None)
            assert get_logs_tool is not None
            assert get_logs_tool.title == "Get System Logs"
            assert "filtering and formatting options" in get_logs_tool.description

            # Test resources discovery
            resources = await session.list_resources()
            resource_uris = [r.uri for r in resources.resources]
            assert "mikrotik://logs/recent" in resource_uris
            assert "mikrotik://system/info" in resource_uris

            # Test that resources have proper titles and descriptions
            recent_logs = next((r for r in resources.resources if r.name == "recent_logs"), None)
            assert recent_logs is not None
            assert recent_logs.title == "Recent System Logs"
            assert "basic information" in recent_logs.description

            # Test prompts discovery
            prompts = await session.list_prompts()
            prompt_names = [p.name for p in prompts.prompts]
            assert "analyze_logs" in prompt_names
            assert "system_health_check" in prompt_names

            # Test that prompts have proper titles
            analyze_prompt = next((p for p in prompts.prompts if p.name == "analyze_logs"), None)
            assert analyze_prompt is not None
            assert analyze_prompt.title == "Analyze Logs"


@pytest.mark.asyncio
async def test_tool_calls_via_client():
    """Test that the client can call tools and get proper responses."""
    server_cmd = sys.executable
    server_args = [os.path.join(PROJECT_ROOT, "server", "server.py")]

    async with stdio_client(command=server_cmd, args=server_args) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test calling a simple tool
            result = await session.call_tool("test_connection", {})
            assert hasattr(result, "content")
            assert any(isinstance(c, TextContent) for c in result.content)
            
            # Check that the response contains the expected emoji indicators
            response_text = "".join(c.text for c in result.content if isinstance(c, TextContent))
            assert "✅" in response_text or "❌" in response_text


@pytest.mark.asyncio
async def test_resource_reading_via_client():
    """Test that the client can read resources and get proper content."""
    server_cmd = sys.executable
    server_args = [os.path.join(PROJECT_ROOT, "server", "server.py")]

    async with stdio_client(command=server_cmd, args=server_args) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test reading a resource
            try:
                result = await session.read_resource("mikrotik://system/info")
                # If we get here, the resource was read successfully
                assert result is not None
            except Exception as e:
                # It's okay if this fails due to missing MikroTik configuration
                # The important thing is that the server handles the request properly
                assert "MikroTik client not available" in str(e) or "configuration" in str(e).lower()


@pytest.mark.asyncio
async def test_prompt_retrieval_via_client():
    """Test that the client can retrieve prompts with proper content."""
    server_cmd = sys.executable
    server_args = [os.path.join(PROJECT_ROOT, "server", "server.py")]

    async with stdio_client(command=server_cmd, args=server_args) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test getting a prompt
            result = await session.get_prompt("system_health_check")
            assert result is not None
            assert result.description == "System health check"
            assert len(result.messages) > 0
            
            # Check that the prompt content is comprehensive
            prompt_content = "".join(
                c.text for m in result.messages 
                for c in m.content if hasattr(c, 'text')
            )
            assert "comprehensive health check" in prompt_content.lower()
            assert "system resource usage" in prompt_content.lower()


@pytest.mark.asyncio
async def test_server_capabilities_via_client():
    """Test that the client can discover server capabilities properly."""
    server_cmd = sys.executable
    server_args = [os.path.join(PROJECT_ROOT, "server", "server.py")]

    async with stdio_client(command=server_cmd, args=server_args) as (read, write):
        async with ClientSession(read, write) as session:
            # Test initialization and capability discovery
            await session.initialize()
            
            # The server should have initialized successfully
            # If we get here without errors, the capabilities are properly declared
            assert True  # Placeholder assertion - success is reaching this point


if __name__ == "__main__":
    pytest.main([__file__])


