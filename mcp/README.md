# CCMaster MCP Implementation

**Version:** 1.0.0  
**Date:** January 19, 2025

## Overview

The CCMaster MCP (Model Context Protocol) implementation enables intelligent inter-session communication between Claude Code sessions. This allows multiple Claude agents to coordinate tasks, share information, and collaborate on complex projects.

## Key Features

### 🔄 Inter-Session Communication
- **Asynchronous Messaging**: Sessions can send messages to each other without blocking
- **Intelligent Prompting**: Instead of just "continue", sessions can send specific prompts and tasks
- **Cross-Session Coordination**: Coordinate multiple agents working on different parts of a project

### 🤖 Multi-Agent Orchestration
- **Session Management**: Create, kill, and monitor multiple Claude Code sessions
- **Task Distribution**: Assign different tasks to different sessions
- **Temporary Sessions**: Spawn sessions for specific tasks and automatically clean up

### 📊 Real-Time Monitoring
- **Session Status**: Get real-time status of all sessions
- **Log Streaming**: Access logs from any session
- **System Metrics**: Monitor CCMaster system performance

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Claude Code Sessions                             │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│ │   Session A     │  │   Session B     │  │   Session C     │             │
│ │   Frontend      │  │   Backend       │  │   Testing       │             │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│          │                    │                    │                       │
│          └────────────────────┼────────────────────┘                       │
│                               │                                             │
│                    ┌─────────────────┐                                     │
│                    │  MCP Client     │                                     │
│                    │ (claude_client) │                                     │
│                    └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                               │
                               │ JSON-RPC 2.0 over HTTP
                               │
┌─────────────────────────────────────────────────────────────────────────────┐
│                               CCMaster                                      │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│ │   MCP Server    │  │   Session       │  │   Multi-Agent   │             │
│ │   (HTTP:8080)   │  │   Manager       │  │   Coordinator   │             │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│          │                    │                    │                       │
│          └────────────────────┼────────────────────┘                       │
│                               │                                             │
│                    ┌─────────────────┐                                     │
│                    │  Claude Code    │                                     │
│                    │  Sessions       │                                     │
│                    └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### 1. Install Dependencies

```bash
# Python 3.7+ required
pip install requests
```

### 2. Configure CCMaster

Edit `~/.ccmaster/config.json`:

```json
{
  "claude_code_command": "claude",
  "monitor_interval": 0.5,
  "mcp": {
    "enabled": true,
    "host": "localhost",
    "port": 8080
  }
}
```

### 3. Start CCMaster with MCP

```bash
# Start CCMaster in watch mode (MCP server starts automatically)
ccmaster watch

# You should see:
# ⟐ Starting Claude session in /current/directory
# ⟐ MCP server started on localhost:8080
# ◆ Session ID: 20250119_123456_12345
# ⊙ Watch mode: ON - Will auto-continue after idle
```

## Usage Examples

### Basic Inter-Session Communication

#### From Claude Code Session:
```bash
# In any Claude Code session, you can now interact with other sessions
python /path/to/ccmaster/mcp/claude_client.py list-sessions
```

#### Example Response:
```json
{
  "sessions": [
    {
      "session_id": "20250119_123456_12345",
      "working_dir": "/Users/user/project",
      "status": "active",
      "is_active": true,
      "created_at": "2025-01-19T12:34:56"
    },
    {
      "session_id": "20250119_123500_67890",
      "working_dir": "/Users/user/project/backend",
      "status": "active",
      "is_active": true,
      "created_at": "2025-01-19T12:35:00"
    }
  ]
}
```

### Send Messages Between Sessions

```bash
# Send a message from Session A to Session B
python claude_client.py send-message "20250119_123500_67890" "Please implement the user authentication API endpoints"

# Send a message and wait for response
python claude_client.py send-message "20250119_123456_12345" "What's the status of the frontend components?" --wait
```

### Create New Sessions for Specific Tasks

```bash
# Create a new session for testing
python claude_client.py create-session "/Users/user/project/tests" --max-turns 5

# Spawn a temporary session to run a specific command
python claude_client.py spawn-temp "npm test" --working-dir "/Users/user/project" --timeout 120
```

### Coordinate Multiple Sessions

```bash
# Coordinate sessions for a complex task
python claude_client.py coordinate "Implement user management system" '{
  "20250119_123456_12345": "Create frontend user interface and forms",
  "20250119_123500_67890": "Implement backend API endpoints and database models",
  "20250119_123510_11111": "Write comprehensive tests for user management"
}'
```

## MCP Tools Reference

### Session Management Tools

#### `list_sessions`
Lists all Claude Code sessions.

**Parameters:**
- `include_ended` (boolean): Include ended sessions in the list

**Returns:**
- `sessions`: Array of session objects
- `total_count`: Total number of sessions
- `active_count`: Number of active sessions

#### `get_session_status`
Gets detailed status of a specific session.

**Parameters:**
- `session_id` (string): Session ID to check

**Returns:**
- Session status object with current state, working directory, creation time, etc.

#### `send_message_to_session`
Sends a message/prompt to a specific session.

**Parameters:**
- `session_id` (string): Target session ID
- `message` (string): Message to send
- `wait_for_response` (boolean): Wait for session to respond

**Returns:**
- Success status, timestamp, and optional response status

#### `create_session`
Creates a new Claude Code session.

**Parameters:**
- `working_dir` (string): Working directory for the session
- `watch_mode` (boolean): Enable watch mode for auto-continuation
- `max_turns` (integer): Maximum auto-continue turns

**Returns:**
- Session ID, working directory, and configuration

#### `kill_session`
Terminates a specific session.

**Parameters:**
- `session_id` (string): Session ID to kill

**Returns:**
- Success status and confirmation message

#### `spawn_temp_session`
Spawns a temporary session, runs a command, and cleans up.

**Parameters:**
- `command` (string): Command to execute
- `working_dir` (string): Working directory
- `timeout` (integer): Timeout in seconds

**Returns:**
- Execution results, logs, and cleanup status

#### `coordinate_sessions`
Coordinates multiple sessions for a complex task.

**Parameters:**
- `task_description` (string): Description of the overall task
- `session_assignments` (object): Session ID to subtask mapping

**Returns:**
- Coordination status and results for each session

#### `get_session_logs`
Gets logs from a specific session.

**Parameters:**
- `session_id` (string): Session ID
- `lines` (integer): Number of recent lines to retrieve

**Returns:**
- Log lines and metadata

### MCP Resources

#### `ccmaster://sessions`
Real-time data about all sessions.

**Content:** JSON with session information, status, and metadata

#### `ccmaster://status`
CCMaster system status and metrics.

**Content:** JSON with system metrics, uptime, and server information

## Use Cases

### 1. Full-Stack Development

```bash
# Session A: Frontend development
python claude_client.py create-session "/project/frontend"
python claude_client.py send-message "SESSION_A" "Create the user login component"

# Session B: Backend development
python claude_client.py create-session "/project/backend"
python claude_client.py send-message "SESSION_B" "Implement authentication API"

# Session C: Testing
python claude_client.py create-session "/project/tests"
python claude_client.py send-message "SESSION_C" "Write integration tests for user auth"
```

### 2. Code Review and Collaboration

```bash
# Session A implements a feature
python claude_client.py send-message "SESSION_A" "Implement the payment processing module"

# Session B reviews the implementation
python claude_client.py send-message "SESSION_B" "Review the payment processing code and suggest improvements"

# Session C handles documentation
python claude_client.py send-message "SESSION_C" "Document the payment processing API"
```

### 3. Multi-Language Projects

```bash
# Session A: Python backend
python claude_client.py create-session "/project/python-api"

# Session B: JavaScript frontend
python claude_client.py create-session "/project/js-frontend"

# Session C: Go microservice
python claude_client.py create-session "/project/go-service"

# Coordinate all sessions
python claude_client.py coordinate "Build microservices architecture" '{
  "SESSION_A": "Create Python API with FastAPI",
  "SESSION_B": "Build React frontend with TypeScript",
  "SESSION_C": "Implement Go microservice for data processing"
}'
```

### 4. Testing and Quality Assurance

```bash
# Run tests across different sessions
python claude_client.py spawn-temp "npm test" --working-dir "/project/frontend"
python claude_client.py spawn-temp "pytest" --working-dir "/project/backend"
python claude_client.py spawn-temp "go test ./..." --working-dir "/project/go-service"

# Get test results
python claude_client.py logs "TEMP_SESSION_1" --lines 50
```

## Advanced Configuration

### Environment Variables

```bash
# Set default MCP server location
export CCMASTER_MCP_HOST=localhost
export CCMASTER_MCP_PORT=8080

# Enable debug logging
export CCMASTER_DEBUG=true
```

### Custom Client Configuration

```python
from mcp.client import CCMasterMCPClient

# Create client with custom configuration
client = CCMasterMCPClient('localhost', 8080)
client.connect()

# Custom tool call
result = client.call_tool('custom_tool', {'param': 'value'})
```

## Troubleshooting

### Common Issues

#### 1. MCP Server Not Starting
```bash
# Check if port is available
netstat -an | grep 8080

# Check CCMaster logs
ccmaster logs SESSION_ID
```

#### 2. Connection Refused
```bash
# Verify CCMaster is running
ps aux | grep ccmaster

# Check MCP server status
curl http://localhost:8080/
```

#### 3. Permission Errors
```bash
# Make sure claude_client.py is executable
chmod +x /path/to/ccmaster/mcp/claude_client.py

# Check file permissions
ls -la /path/to/ccmaster/mcp/
```

### Debug Mode

```bash
# Enable debug logging
export CCMASTER_DEBUG=true
ccmaster watch

# Or modify config.json
{
  "mcp": {
    "enabled": true,
    "host": "localhost",
    "port": 8080,
    "debug": true
  }
}
```

## Security Considerations

### Network Security
- MCP server runs on localhost by default
- Use firewall rules to restrict access
- Consider HTTPS for production deployments

### Authentication
- Current implementation uses localhost-only access
- For production, implement authentication tokens
- Use environment variables for sensitive configuration

### Data Protection
- Session logs may contain sensitive information
- Implement log rotation and cleanup
- Use secure file permissions for configuration files

## Performance Optimization

### Server Tuning
```json
{
  "mcp": {
    "enabled": true,
    "host": "localhost",
    "port": 8080,
    "max_connections": 10,
    "timeout": 30,
    "keepalive": true
  }
}
```

### Client Optimization
```python
# Reuse client connections
client = CCMasterMCPClient('localhost', 8080)
client.connect()

# Batch operations
results = []
for session_id in session_ids:
    result = client.get_session_status(session_id)
    results.append(result)

client.disconnect()
```

## Future Enhancements

### Planned Features
- [ ] WebSocket support for real-time updates
- [ ] Authentication and authorization
- [ ] Session persistence and recovery
- [ ] Advanced coordination strategies
- [ ] Integration with external MCP servers
- [ ] Web-based dashboard for session management

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Project Issues](https://github.com/username/ccmaster/issues)
- Documentation: [CCMaster Docs](https://docs.ccmaster.io)
- Community: [Discord Server](https://discord.gg/ccmaster)