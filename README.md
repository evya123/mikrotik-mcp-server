# MikroTik MCP Server

A comprehensive Model Context Protocol (MCP) server implementation for MikroTik RouterOS devices, providing programmatic access to device management, monitoring, and configuration through a well-organized, production-ready Python codebase.

## Features

### 🔍 **Log Management**
- **Comprehensive Log Retrieval**: Access system logs with advanced filtering and formatting options
- **Client-Side Filtering**: Robust filtering capabilities for topics, messages, and log levels
- **Specialized Log Types**: Dedicated methods for debug, error, warning, and info logs
- **Buffer Support**: Access logs from separate memory logging buffers
- **Extra Information**: Retrieve logs with additional metadata and context

### 🖥️ **System Management**
- **Resource Monitoring**: Real-time system resource usage and performance metrics
- **Health Assessment**: Comprehensive system health evaluation with status indicators
- **Performance Metrics**: CPU load, memory usage, disk space, and uptime monitoring
- **Proactive Alerts**: Warning and critical status detection for resource thresholds

### 🌐 **IP & Network Management**
- **IP Address Management**: View and filter IP address configurations across interfaces
- **Routing Table**: Access and analyze IP routing configurations and gateway settings
- **IP Pools**: Manage DHCP address pools and allocation ranges
- **Network Summary**: Comprehensive overview of network topology and configuration

### 🔌 **Interface Management**
- **Interface Discovery**: Retrieve all configured interfaces with detailed properties
- **Interface Types**: Support for Ethernet, wireless, bridge, and other interface types
- **Status Monitoring**: Real-time interface status, MTU, MAC addresses, and operational state
- **Filtering Options**: Advanced filtering by name, type, status, and comments

### 🛡️ **Firewall Management**
- **Rule Management**: Comprehensive firewall rule retrieval and filtering
- **NAT Configuration**: Network Address Translation rule management
- **Mangle Rules**: Packet modification and QoS rule handling
- **Address Lists**: IP address list management for security policies

### 🌐 **DHCP Management**
- **Server Configuration**: DHCP server setup and configuration management
- **Lease Management**: Active DHCP lease monitoring and tracking
- **Network Configuration**: DHCP network and subnet management
- **Client Management**: DHCP client configuration and status

### 🛠️ **MCP Integration**
- **Resource Discovery**: Rich metadata for all available resources and tools
- **Tool Integration**: Comprehensive tool schemas with parameter validation
- **Prompt System**: Intelligent prompts for common tasks and troubleshooting
- **Error Handling**: Robust error handling with detailed error messages

## Architecture

The project follows a modular, domain-driven architecture:

```
src/mcp_mikrotik/
├── __init__.py          # Main package exports
├── base.py              # Base client with common functionality
├── models.py            # Shared type definitions
├── client.py            # Main client combining all specialized clients
├── logs/                # Log management module
│   ├── __init__.py
│   ├── models.py        # Log-specific type definitions
│   └── client.py        # Specialized logs client
├── system/              # System management module
│   ├── __init__.py
│   ├── models.py        # System-specific type definitions
│   └── client.py        # Specialized system client
├── ip/                  # IP and network management module
│   ├── __init__.py
│   ├── models.py        # IP-specific type definitions
│   └── client.py        # Specialized IP client
├── interface/           # Interface management module
│   ├── __init__.py
│   ├── models.py        # Interface-specific type definitions
│   └── client.py        # Specialized interface client
├── firewall/            # Firewall management module
│   ├── __init__.py
│   ├── models.py        # Firewall-specific type definitions
│   └── client.py        # Specialized firewall client
└── dhcp/                # DHCP management module
    ├── __init__.py
    ├── models.py        # DHCP-specific type definitions
    └── client.py        # Specialized DHCP client
```

## Installation

### Prerequisites
- Python 3.11 or higher
- Access to a MikroTik RouterOS device
- Network connectivity to the device

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mikrotik-mcp
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp config/example.env .env
   # Edit .env with your MikroTik device details
   ```

## Configuration

Create a `.env` file with your MikroTik device configuration:

```env
# MikroTik device connection settings
MIKROTIK_HOST=192.168.88.1
MIKROTIK_USERNAME=admin
MIKROTIK_PASSWORD=your_password_here
MIKROTIK_PORT=443
MIKROTIK_USE_SSL=true

# Optional: Debug mode
DEBUG=true

# Optional: Log level
LOG_LEVEL=INFO
```

## Usage

### Basic Usage

```python
from src.mcp_mikrotik import MikroTikClient

# Initialize client
config = {
    "host": "192.168.88.1",
    "username": "admin",
    "password": "your_password",
    "useSSL": True
}

client = MikroTikClient(config)

# Test connection
is_connected = await client.test_connection()
print(f"Connected: {is_connected}")

# Get system information
system_info = await client.get_system_info()
print(f"System uptime: {system_info.get('uptime')}")

# Get recent logs
logs = await client.get_logs({"brief": True, "max_logs": 10})
for log in logs:
    print(f"{log['time']}: {log['message']}")
```

### Log Management

```python
# Get specific log types
debug_logs = await client.get_debug_logs()
error_logs = await client.get_error_logs()
warning_logs = await client.get_warning_logs()

# Filter logs by condition
system_logs = await client.find_logs('topics~"system"')
dhcp_logs = await client.find_logs('topics~"dhcp" and message~"assigned"')

# Get logs with extra information
detailed_logs = await client.get_logs_with_extra_info({"brief": False})
```

### System Monitoring

```python
# Get comprehensive system health
health = await client.get_system_health()
print(f"System status: {health['status']}")
print(f"Memory usage: {health['memory_usage_percent']}%")
print(f"Disk usage: {health['disk_usage_percent']}%")

# Get detailed resource information
resources = await client.get_system_resources()
for resource in resources:
    print(f"CPU: {resource['cpu_count']} cores, {resource['cpu_frequency']} MHz")
```

### Network Management

```python
# Get IP addresses
addresses = await client.get_ip_addresses()
for addr in addresses:
    print(f"{addr['address']} on {addr['interface']}")

# Get routing table
routes = await client.get_ip_routes()
for route in routes:
    print(f"{route['dst_address']} -> {route['gateway']}")

# Get network summary
summary = await client.get_network_summary()
print(f"Total IP addresses: {summary['ip_addresses_count']}")
print(f"Total routes: {summary['ip_routes_count']}")
```

### Interface Management

```python
# Get all interfaces
interfaces = await client.get_interfaces()
for interface in interfaces:
    print(f"{interface['name']}: {interface['type']} - {interface['status']}")

# Get specific interface types
ethernet_interfaces = await client.get_ethernet_interfaces()
wireless_interfaces = await client.get_wireless_interfaces()
bridge_interfaces = await client.get_bridge_interfaces()

# Filter interfaces by properties
lan_interfaces = await client.get_interfaces({
    "type": "ether",
    "running": True,
    "comment": "LAN"
})
```

### Firewall Management

```python
# Get firewall rules
firewall_rules = await client.get_firewall_rules()
for rule in firewall_rules:
    print(f"{rule['chain']}: {rule['action']} {rule['src_address']} -> {rule['dst_address']}")

# Get NAT rules
nat_rules = await client.get_nat_rules()
for rule in nat_rules:
    print(f"NAT: {rule['chain']} {rule['action']}")

# Get address lists
address_lists = await client.get_address_lists()
for addr_list in address_lists:
    print(f"List: {addr_list['name']} - {addr_list['address']}")
```

### DHCP Management

```python
# Get DHCP servers
dhcp_servers = await client.get_dhcp_servers()
for server in dhcp_servers:
    print(f"DHCP Server: {server['name']} on {server['interface']}")

# Get active leases
dhcp_leases = await client.get_dhcp_leases()
for lease in dhcp_leases:
    print(f"Lease: {lease['address']} -> {lease['mac_address']}")

# Get DHCP networks
dhcp_networks = await client.get_dhcp_networks()
for network in dhcp_networks:
    print(f"Network: {network['name']} - {network['address']}")
```

## MCP Server

### Running the Server

```bash
# Run the MCP server
python -m server.server

# Or use the installed script
mikrotik-mcp
```

### Available Resources

The MCP server provides the following resources:

- `mikrotik://logs/recent` - Recent system logs
- `mikrotik://logs/debug` - Debug logs
- `mikrotik://logs/error` - Error logs
- `mikrotik://logs/warning` - Warning logs
- `mikrotik://logs/info` - Info logs
- `mikrotik://logs/detailed` - Detailed logs with extra info
- `mikrotik://system/info` - System information
- `mikrotik://system/health` - System health metrics
- `mikrotik://ip/addresses` - IP address configurations
- `mikrotik://ip/routes` - IP routing table
- `mikrotik://ip/pools` - IP address pools
- `mikrotik://ip/network_summary` - Network configuration summary
- `mikrotik://interface/all` - All interface configurations
- `mikrotik://interface/ethernet` - Ethernet interface configurations
- `mikrotik://interface/wireless` - Wireless interface configurations
- `mikrotik://interface/bridge` - Bridge interface configurations
- `mikrotik://firewall/rules` - Firewall rule configurations
- `mikrotik://firewall/nat` - NAT rule configurations
- `mikrotik://firewall/address-lists` - Firewall address lists
- `mikrotik://dhcp/servers` - DHCP server configurations
- `mikrotik://dhcp/leases` - Active DHCP leases
- `mikrotik://dhcp/networks` - DHCP network configurations

### Available Tools

- `get_logs` - Retrieve system logs with filtering
- `get_debug_logs` - Get debug logs
- `get_error_logs` - Get error logs
- `get_warning_logs` - Get warning logs
- `get_info_logs` - Get info logs
- `get_logs_from_buffer` - Get logs from specific buffer
- `get_logs_with_extra_info` - Get logs with extra metadata
- `get_system_info` - Get system information
- `get_system_health` - Get system health metrics
- `get_ip_addresses` - Get IP address configurations
- `get_ip_routes` - Get IP routing table
- `get_ip_pools` - Get IP address pools
- `get_network_summary` - Get network configuration summary
- `get_interfaces` - Get all interface configurations
- `get_ethernet_interfaces` - Get Ethernet interface configurations
- `get_wireless_interfaces` - Get wireless interface configurations
- `get_bridge_interfaces` - Get bridge interface configurations
- `get_firewall_rules` - Get firewall rule configurations
- `get_nat_rules` - Get NAT rule configurations
- `get_mangle_rules` - Get mangle rule configurations
- `get_address_lists` - Get firewall address lists
- `get_dhcp_servers` - Get DHCP server configurations
- `get_dhcp_leases` - Get active DHCP leases
- `get_dhcp_networks` - Get DHCP network configurations
- `get_dhcp_clients` - Get DHCP client configurations
- `test_connection` - Test device connectivity

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_logs_client.py
pytest tests/test_system_client.py
pytest tests/test_ip_client.py

# Run with coverage
pytest --cov=src/mcp_mikrotik --cov-report=html
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Project Structure

```
mikrotik-mcp/
├── src/mcp_mikrotik/           # Main package source
│   ├── __init__.py             # Package exports
│   ├── base.py                 # Base client functionality
│   ├── models.py               # Shared type definitions
│   ├── client.py               # Main client interface
│   ├── logs/                   # Log management module
│   ├── system/                 # System management module
│   └── ip/                     # IP management module
├── server/                     # MCP server implementation
├── tests/                      # Comprehensive test suite
├── config/                     # Configuration examples
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## API Reference

### MikroTikClient

The main client class that provides access to all functionality:

```python
class MikroTikClient:
    def __init__(self, config: MikroTikConfig)
    
    # Log management
    async def get_logs(options: Optional[GetLogsArgs] = None, max_logs: int = 1000)
    async def get_debug_logs(options: Optional[Dict[str, Any]] = None, max_logs: int = 1000)
    async def get_error_logs(options: Optional[Dict[str, Any]] = None, max_logs: int = 1000)
    async def get_warning_logs(options: Optional[Dict[str, Any]] = None, max_logs: int = 1000)
    async def get_info_logs(options: Optional[Dict[str, Any]] = None, max_logs: int = 1000)
    async def get_logs_from_buffer(buffer_name: str, options: Optional[Dict[str, Any]] = None, max_logs: int = 1000)
    async def get_logs_with_extra_info(options: Optional[Dict[str, Any]] = None, max_logs: int = 1000)
    async def find_logs(where: str, options: Optional[Dict[str, Any]] = None)
    
    # System management
    async def get_system_info()
    async def get_system_resources()
    async def get_system_health()
    
    # IP management
    async def get_ip_addresses(options: Optional[GetIPAddressesArgs] = None)
    async def get_ip_routes(options: Optional[GetIPRoutesArgs] = None)
    async def get_ip_pools()
    async def get_network_summary()
    
    # Interface management
    async def get_interfaces(options: Optional[GetInterfacesArgs] = None)
    async def get_ethernet_interfaces()
    async def get_wireless_interfaces()
    async def get_bridge_interfaces()
    
    # Firewall management
    async def get_firewall_rules(options: Optional[GetFirewallRulesArgs] = None)
    async def get_nat_rules()
    async def get_mangle_rules()
    async def get_address_lists()
    
    # DHCP management
    async def get_dhcp_servers(options: Optional[GetDHCPServersArgs] = None)
    async def get_dhcp_leases()
    async def get_dhcp_networks()
    async def get_dhcp_clients()
    
    # Connection testing
    async def test_connection()
```

### Specialized Clients

Access specialized functionality through dedicated clients:

```python
# Log management
logs_client = client.logs
system_client = client.system
ip_client = client.ip
interface_client = client.interface
firewall_client = client.firewall
dhcp_client = client.dhcp

# Use specialized methods
debug_logs = await logs_client.get_debug_logs()
system_health = await system_client.get_system_health()
network_summary = await ip_client.get_network_summary()
ethernet_interfaces = await interface_client.get_ethernet_interfaces()
firewall_rules = await firewall_client.get_firewall_rules()
dhcp_leases = await dhcp_client.get_dhcp_leases()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples

## Roadmap

- [x] Interface management module
- [x] Firewall configuration module
- [x] DHCP server management
- [ ] Wireless management module
- [ ] VPN configuration
- [ ] User management
- [ ] Backup and restore functionality
- [ ] Real-time monitoring and alerts
- [ ] Configuration templates
- [ ] Bulk operations support