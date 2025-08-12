# MikroTik MCP Server

A Model Context Protocol (MCP) server for interacting with MikroTik RouterOS devices. This server provides tools and resources for monitoring logs, system information, and device management through the MCP protocol.

## ✨ Features

- **MCP Resources**: Access to MikroTik system logs, debug logs, error logs, warning logs, info logs, and system information
- **MCP Tools**: Interactive tools for retrieving logs with filtering options, testing connections, and managing device data
- **MCP Prompts**: Pre-built prompt templates for log analysis, system health checks, and troubleshooting
- **Official MCP SDK**: Built using the latest [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk) v1.12.0+
- **Enhanced UX**: Improved metadata, better error handling, and user-friendly feedback
- **Comprehensive Testing**: Full test suite with integration tests and SDK alignment validation

## 🚀 What's New

### MCP SDK Alignment (Latest Update)
- **Enhanced Metadata**: Proper titles, descriptions, and naming conventions following SDK best practices
- **Improved Error Handling**: Graceful client handling with user-friendly error messages and visual feedback
- **Better Schemas**: Comprehensive JSON schemas with examples and validation
- **Enhanced Capabilities**: Logging configuration and future-ready capability declarations
- **Quality Assurance**: Comprehensive testing for all improvements and edge cases

## 📋 Prerequisites

- Python 3.11 or higher
- Access to a MikroTik RouterOS device
- Network connectivity to the device

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mikrotik-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp config/example.env .env
# Edit .env with your MikroTik device details
```

## ⚙️ Configuration

Create a `.env` file with your MikroTik device configuration:

```env
MIKROTIK_HOST=192.168.88.1
MIKROTIK_USERNAME=admin
MIKROTIK_PASSWORD=your_password
MIKROTIK_PORT=443
MIKROTIK_USE_SSL=true
```

## 🎯 Usage

### Running the Server

#### Direct Execution
```bash
python -m python_src.server.server
```

#### Using MCP CLI Tools
```bash
# Test with MCP Inspector
mcp dev python_src/server/server.py

# Install in Claude Desktop
mcp install python_src/server/server.py

# Run directly
mcp run python_src/server/server.py
```

### Available MCP Resources

The server provides the following resources with enhanced metadata:

- `mikrotik://logs/recent` - Recent system logs with basic information
- `mikrotik://logs/debug` - Debug logs for troubleshooting and development
- `mikrotik://logs/error` - Error logs for system monitoring and alerting
- `mikrotik://logs/warning` - Warning logs for proactive system monitoring
- `mikrotik://logs/info` - Info logs for general system status
- `mikrotik://logs/detailed` - Detailed logs with extra information and metadata
- `mikrotik://system/info` - System information and resource usage

### Available MCP Tools

Enhanced tools with comprehensive schemas and descriptions:

- `get_logs` - Retrieve logs with optional filtering and formatting options
- `get_debug_logs` - Get debug logs for troubleshooting and development purposes
- `get_error_logs` - Get error logs for system monitoring and alerting
- `get_warning_logs` - Get warning logs for proactive system monitoring
- `get_info_logs` - Get info logs for general system status
- `get_logs_from_buffer` - Get logs from a specific memory buffer on the device
- `get_logs_with_extra_info` - Get logs with additional metadata and context
- `test_connection` - Test connection and verify authentication

### Available MCP Prompts

Enhanced prompts with comprehensive guidance:

- `analyze_logs` - Generate comprehensive prompts for log analysis with specific criteria
- `system_health_check` - Generate prompts for comprehensive system health assessment
- `troubleshooting_guide` - Generate detailed troubleshooting prompts for specific issues

## 📚 API Examples

### Basic Usage

```python
from python_src.client.mikrotik import MikroTikClient

# Configuration
config = {
    "host": "192.168.88.1",
    "username": "admin",
    "password": "your_password",
    "port": 443,
    "useSSL": True
}

# Create client
client = MikroTikClient(config)

# Test connection
is_connected = await client.test_connection()
if is_connected:
    print("✅ Connection successful!")
    
    # Get system info
    system_info = await client.get_system_info()
    print("System Information:", json.dumps(system_info, indent=2))
    
    # Get recent logs
    logs = await client.get_logs({"brief": True})
    print(f"Recent logs ({len(logs)} entries):")
    for i, log in enumerate(logs):
        print(f"{i + 1}. [{log.get('time', '')}] {log.get('topics', '')}: {log.get('message', '')}")
```

### Log Retrieval Examples

```python
# Get logs with filtering
logs = await client.get_logs({
    "brief": True,
    "where": 'topics~"system" and message~"login"'
})

# Get specific log types
debug_logs = await client.get_debug_logs()
error_logs = await client.get_error_logs()
warning_logs = await client.get_warning_logs()
info_logs = await client.get_info_logs()

# Get logs with extra info
detailed_logs = await client.get_logs_with_extra_info({"brief": True})
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "python3",
      "args": ["/path/to/mikrotik-mcp/python_src/server/server.py"],
      "env": {
        "MIKROTIK_HOST": "192.168.88.1",
        "MIKROTIK_USERNAME": "admin",
        "MIKROTIK_PASSWORD": "your_password",
        "MIKROTIK_PORT": "443",
        "MIKROTIK_USE_SSL": "true"
      }
    }
  }
}
```

## 🧪 Development

### Project Structure

```
mikrotik-mcp/
├── python_src/
│   ├── client/          # MikroTik API client
│   ├── server/          # MCP server implementation
│   └── types/           # Type definitions
├── python_tests/        # Comprehensive test suite
├── config/              # Configuration files
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Running Tests

```bash
# Run all tests
pytest python_tests/

# Run specific test categories
pytest python_tests/test_mcp_server.py          # Core server tests
pytest python_tests/test_mcp_improvements.py    # SDK alignment tests
pytest python_tests/test_mcp_client_integration.py  # Client integration tests

# Run integration tests (requires real MikroTik device)
RUN_INTEGRATION_TESTS=1 pytest python_tests/test_connection.py

# Run SDK client integration tests
RUN_SDK_INTEGRATION=1 pytest python_tests/test_mcp_client_integration.py
```

### Code Quality

The project follows PEP 8 style guidelines and includes comprehensive testing:

```bash
# Code formatting
black python_src/
isort python_src/

# Linting and type checking
flake8 python_src/
mypy python_src/

# Run all quality checks
pytest --cov=python_src --cov-report=html
```

## 🔌 MCP Integration

This server implements the latest Model Context Protocol specification and can be used with:

- **Claude Desktop**: Install using `mcp install`
- **MCP Inspector**: Test using `mcp dev`
- **Custom MCP Clients**: Connect using stdio or HTTP transports

### Transport Support

- **stdio**: Standard input/output for CLI tools
- **Streamable HTTP**: HTTP-based transport for web applications
- **SSE**: Server-Sent Events transport (legacy)

### Enhanced Capabilities

- **Improved Metadata**: Better titles, descriptions, and naming for tools and resources
- **Enhanced Error Handling**: Graceful failures with user-friendly messages
- **Comprehensive Schemas**: Detailed JSON schemas with examples and validation
- **Logging Configuration**: Configurable logging levels and formats
- **Future-Ready**: Extensible capability system for new features

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**: Check network connectivity and device credentials
2. **Authentication Error**: Verify username and password in `.env`
3. **Port Issues**: Ensure the correct port is configured (80 for HTTP, 443 for HTTPS)

### Connection Troubleshooting

**Cannot Connect to MikroTik Device:**
- Ensure your machine can reach the MikroTik device (try pinging it)
- Check if the device is on the same network or if routing is properly configured
- Verify the REST API service is enabled in RouterOS (IP → Services)
- Ensure the port matches what you've configured in `.env`

**Authentication Errors:**
- Double-check username and password in `.env`
- Try logging in with the same credentials via WebFig or WinBox
- Ensure the user has the `api` or `read` permission

**SSL Configuration:**
- If using SSL (`MIKROTIK_USE_SSL=true`), ensure the device has a valid certificate
- If you're using a self-signed certificate, you might need to disable certificate verification

### Enhanced Error Messages

The server now provides clear, actionable error messages:
- ✅ Success indicators for successful operations
- ❌ Error indicators for failed operations
- Detailed error descriptions with troubleshooting suggestions

### Performance Issues

**Slow Response Times:**
- Set a reasonable `max_logs` parameter (default is 1000)
- Use more specific filters to reduce the number of logs retrieved
- Use the `proplist` parameter to retrieve only the fields you need

**Memory Usage:**
- Use the `max_logs` parameter to limit the number of logs retrieved
- Process logs in batches if you need to retrieve a large number
- Use more specific filters to reduce the number of logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Testing Requirements

- All new features must include comprehensive tests
- Integration tests should be added for new MCP capabilities
- SDK alignment tests should validate new features follow best practices

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with the latest [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Follows MCP specification standards and best practices
- Designed for MikroTik RouterOS integration
- Enhanced with comprehensive testing and quality assurance