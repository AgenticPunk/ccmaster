# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running CCMaster
```bash
# Install/setup
./setup.sh

# Basic usage
ccmaster                          # Start new session in current directory
ccmaster watch                    # Start with auto-continue enabled
ccmaster watch --instances 3      # Start multiple Claude sessions
ccmaster watch --maxturn 50       # Limit auto-continues

# Session management
ccmaster list                     # List all sessions
ccmaster logs SESSION_ID          # View session logs
ccmaster prompts SESSION_ID       # View user prompts

# MCP management
ccmaster mcp status               # Check MCP server status
ccmaster mcp remove               # Remove from project .mcp.json
```

### Testing
```bash
# Run MCP tests (no test framework, run directly)
python mcp/test_mcp.py
python mcp/simple_test.py
```

### Development Notes
- No linting/formatting tools configured - maintain consistent Python style
- No package management - dependencies checked in setup.sh
- Python 3.6+ required, macOS-only (uses AppleScript)
- Check for `requests` module availability for MCP features

## Architecture

CCMaster is a session management tool for Claude Code with these key components:

### Core Structure
```
ccmaster/
├── bin/ccmaster         # Main entry point - session orchestrator
└── hooks/               # Per-session Claude Code hooks
    ├── hook_utils.py    # Shared utilities for all hooks
    ├── pre_tool_use.*   # Track tool usage
    ├── user_prompt_submit.*  # Capture user prompts
    └── stop_hook.*      # Detect when Claude finishes

mcp/
├── server.py           # MCP server with session management tools
├── tools.py            # Session management tool implementations
├── protocol.py         # MCP protocol definitions
└── client.py           # MCP client implementation
```

### Key Design Principles

1. **Minimal Dependencies**: No external package management, simple installation via symlinks
2. **Per-Session Isolation**: Each Claude session gets its own hook configuration in `~/.claude/SESSION_ID/`
3. **Real-time Monitoring**: Status updates via filesystem in `~/.ccmaster/status/SESSION_ID.json`
4. **Multi-Agent Support**: Can manage multiple Claude sessions with unified monitoring
5. **Dynamic Session Creation**: Claude can create new sessions via MCP tools

### Session Lifecycle

1. **Launch**: AppleScript creates new Terminal window/tab
2. **Hook Setup**: Isolated hooks directory created for session
3. **Monitoring**: Process detection and Terminal window tracking
4. **Auto-Continue**: Direct Terminal tab targeting with fallbacks
5. **MCP Integration**: Automatic server start and project configuration

### Important Implementation Details

- **Process Detection**: Uses `ps -eo pid,ppid,args` parsing instead of complex PID tracking
- **Terminal Integration**: AppleScript for window/tab creation and command injection
- **Session Tolerance**: Requires 5 consecutive failures before declaring session ended
- **Port Allocation**: MCP server uses dynamic port range (8080-8090) to avoid conflicts
- **Hook Communication**: JSON files in `~/.ccmaster/status/` for real-time updates
- **Session Prefixes**: Original sessions use [1], [2], MCP-created use [MCP-1], [MCP-2]

### Working with MCP

When modifying MCP functionality:
1. Server creates `.mcp.json` in project directory automatically
2. Dynamic port allocation prevents conflicts
3. All sessions (original + MCP-created) tracked uniformly
4. CLI stays alive until all sessions end
5. Proper cleanup on termination (Ctrl+C)

### Session Status Format

Status files in `~/.ccmaster/status/SESSION_ID.json`:
```json
{
  "status": "idle|processing|working",
  "pid": 12345,
  "current_tool": "Write|Edit|etc",
  "last_update": "2024-01-24T14:30:22.123456",
  "user_prompt": "Latest user input"
}
```