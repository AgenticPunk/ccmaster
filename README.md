# CCMaster - Claude Code Session Manager

CCMaster is an intelligent session management tool for Claude Code. It automatically launches new Terminal windows, monitors Claude's working status in real-time, and provides automatic continuation in watch mode, making long conversations more seamless and efficient.

## ✨ Key Features

- 🚀 **One-Command Launch**: Automatically opens Terminal and starts Claude Code sessions
- 📊 **Real-time Status Monitoring**: Displays Claude's working status (Idle/Processing/Working)
- 🔧 **Tool Activity Tracking**: Shows which tools Claude is currently using
- 👁️ **Watch Mode**: Automatically sends "continue" when Claude becomes idle
- 🎯 **Per-Session Hooks**: Each session has isolated hook configurations for better control
- 📝 **Session History**: View all prompts and detailed logs for any session
- 🎨 **Beautiful Output**: Color-coded status indicators for easy reading
- ⌨️ **Interactive Controls**: Press [w] to toggle watch mode during any session
- 🔢 **Turn Limiting**: Set maximum auto-continue turns with --maxturn
- 🤝 **Multi-Agent Support**: Manage multiple Claude sessions simultaneously with --instances
- 🔗 **MCP Integration**: Automatic Model Context Protocol support for inter-session communication

## 🛠 Installation

### Prerequisites

- macOS (uses AppleScript for Terminal automation)
- Python 3.6+
- Claude Code CLI installed and configured

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/ccmaster.git
cd ccmaster

# Run setup script
./setup.sh

# Or with sudo if needed
sudo ./setup.sh
```

## 📖 Usage

### Basic Commands

```bash
# Start a new Claude session in current directory
ccmaster

# Start a new session in specific directory
ccmaster start -d /path/to/project

# Start in watch mode (auto-continue) in current directory
ccmaster watch

# Start in watch mode with specific directory
ccmaster watch -d /path/to/project

# Start in watch mode with maximum 100 auto-continues
ccmaster watch --maxturn 100

# Start 2 Claude sessions in watch mode (multi-agent)
ccmaster watch --instances 2

# Start 3 Claude sessions with max 50 auto-continues each
ccmaster watch --instances 3 --maxturn 50

# List all sessions
ccmaster list

# View session logs
ccmaster logs 20240124_143022

# View user prompts for a session
ccmaster prompts 20240124_143022

# Check MCP server status
ccmaster mcp status

# Remove CCMaster from project .mcp.json
ccmaster mcp remove
```

### Interactive Controls

During a session, you can use keyboard shortcuts:
- **[w]** - Toggle watch mode on/off
  - When max turns is reached, pressing [w] resets the counter and immediately continues

### Watch Mode Features

Watch mode automatically sends "continue" when Claude becomes idle after completing a response:

```bash
# Basic watch mode - unlimited auto-continues
ccmaster watch

# Limited watch mode - stops after 50 turns
ccmaster watch --maxturn 50
```

When the turn limit is reached:
- Watch mode automatically turns off
- Press [w] to reset the counter and resume auto-continuing
- If Claude is idle, it will immediately send a continue command

### Multi-Agent Mode

When running with `--instances`, CCMaster provides a unified view of all sessions:

```bash
# Launch 3 Claude sessions
ccmaster watch --instances 3
```

Output example:
```
🚀 Starting 3 Claude sessions in /Users/yourname/project
👁️  Watch mode: ON - Will auto-continue after idle

[1] 📍 Session ID: 20240124_143022
[2] 📍 Session ID: 20240124_143023
[3] 📍 Session ID: 20240124_143024

[1][14:30:22] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 2)
[2][14:30:23] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 3)
[3][14:30:24] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 4)

🎯 All sessions launched. Monitoring...
Press [q] to quit, [w] to toggle watch mode for all sessions

[1][14:30:25] ● Processing
[2][14:30:25] ● Idle
[3][14:30:25] ● Processing
[1][14:30:26] ▶ User: "Create API endpoints"
[3][14:30:26] ▶ User: "Write tests"
[2][14:30:27] ▶ Auto-continue (1/∞)
[1][14:30:28] ● Working
[1][14:30:28] → Using Write
```

### Example Output

```
🚀 Starting Claude session in /Users/yourname/project
📍 Session ID: 20240124_143022
👁️  Watch mode: ON - Will auto-continue after idle (max 10 turns)

[14:30:22] ● Processing
[14:30:23] ▶ User: "Create a Python web server"
[14:30:24] ● Working
[14:30:24] → Using Write
[14:30:25] → Using Edit
[14:30:28] ● Idle
[14:30:29] ▶ Auto-continue (1/10)
[14:30:30] ● Processing
...
[14:35:45] 🛑 Max auto-continue turns (10) reached - Watch mode disabled
[14:35:45] 💡 Press [w] to re-enable and continue
```

## 🏗 Architecture

CCMaster uses a hooks-based architecture to monitor Claude Code:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CCMaster  │────▶│ Claude Code  │────▶│    Hooks    │
│   Monitor   │     │   Session    │     │  (Per-Session)│
└─────────────┘     └──────────────┘     └─────────────┘
       ▲                                          │
       │                                          │
       └──────────────────────────────────────────┘
                    Status Updates
```

### Multi-Agent Architecture

With `--instances`, CCMaster can manage multiple Claude sessions:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CCMaster  │────▶│ Claude Code 1│────▶│   Hooks 1   │
│   Monitor   │     └──────────────┘     └─────────────┘
│             │     ┌──────────────┐     ┌─────────────┐
│             │────▶│ Claude Code 2│────▶│   Hooks 2   │
│             │     └──────────────┘     └─────────────┘
│             │     ┌──────────────┐     ┌─────────────┐
│             │────▶│ Claude Code N│────▶│   Hooks N   │
└─────────────┘     └──────────────┘     └─────────────┘
```

Each session:
- Has its own Terminal window/tab
- Maintains independent status tracking
- Has isolated hook configurations
- Can be auto-continued individually

### Key Components

1. **Session Manager** (`ccmaster/bin/ccmaster`)
   - Main orchestrator with simplified, reliable design
   - Simple Terminal launching via AppleScript
   - Robust process monitoring using basic process detection
   - Intelligent auto-continue with fallback methods

2. **Hook System** (`ccmaster/hooks/`)
   - `pre_tool_use.py` - Tracks tool usage
   - `user_prompt_submit.py` - Captures user prompts
   - `stop_hook.py` - Detects when Claude finishes responding
   - Each session gets its own isolated hook configuration

3. **Monitoring System**
   - Session-specific process tracking with PID detection
   - Terminal window monitoring - detects when window is closed
   - Tracks Terminal window and tab for accurate auto-continue
   - Tolerant session monitoring (5 failures before declaring ended)
   - Real-time status files in `~/.ccmaster/status/`
   - Session logs in `~/.ccmaster/logs/`
   - User prompts in separate log files

4. **Auto-Continue System**
   - Direct Terminal tab detection for Claude processes
   - Multi-tier fallback (find Claude tab → frontmost Terminal)
   - Clear success/failure feedback
   - No dependency on window focus or precise timing

## 🔧 Configuration

Configuration file location: `~/.ccmaster/config.json`

```json
{
  "claude_code_command": "claude",
  "monitor_interval": 0.5,
  "mcp": {
    "enabled": true,
    "host": "localhost",
    "port_range": [8080, 8090]
  }
}
```

Note: CCMaster automatically adds the `--dangerously-skip-permissions` flag to all Claude commands to skip permission prompts.

Note: CCMaster always uses the current working directory by default when starting a session.

## 🔗 MCP Integration

CCMaster includes automatic Model Context Protocol (MCP) support, enabling intelligent inter-session communication:

### Automatic Setup
When you run `ccmaster watch`, it automatically:
1. Finds an available port (8080-8090) and starts MCP server
2. Creates `.mcp.json` in your project directory with the correct port
3. Claude Code detects it and enables MCP tools

### Available MCP Tools
In Claude Code, you can use these tools:
- `/mcp__ccmaster__list_sessions` - List all active sessions
- `/mcp__ccmaster__send_message_to_session` - Send messages between sessions
- `/mcp__ccmaster__create_session` - Create new sessions programmatically
- `/mcp__ccmaster__kill_session` - Terminate sessions
- `/mcp__ccmaster__spawn_temp_session` - Run temporary sessions
- `/mcp__ccmaster__coordinate_sessions` - Coordinate multi-agent tasks
- `/mcp__ccmaster__get_session_logs` - Access session logs
- `/mcp__ccmaster__get_session_status` - Check session status

### Example Usage
```bash
# In Claude Code, after running ccmaster watch:
/mcp__ccmaster__list_sessions

# Send a message to another session
/mcp__ccmaster__send_message_to_session session_id="20250119_123456" message="Please implement the user API"

# Coordinate multiple sessions
/mcp__ccmaster__coordinate_sessions task_description="Build full-stack app" session_assignments='{"frontend_session": "Build React UI", "backend_session": "Create API endpoints"}'
```

For detailed MCP documentation, see [MCP_SESSION_INTEGRATION.md](MCP_SESSION_INTEGRATION.md)

## 📁 File Structure

```
~/.ccmaster/
├── config.json          # Global configuration
├── sessions.json        # Session metadata
├── status/              # Real-time status files
│   └── SESSION_ID.json
└── logs/                # Session logs
    ├── SESSION_ID.log
    └── SESSION_ID_prompts.log
```

## 🐛 Troubleshooting

### "Found invalid settings files" warning in Claude
This can happen if the settings.json format is incorrect. CCMaster now uses the correct hooks format.
- Run `rm ~/.claude/settings.json` to clear invalid settings
- CCMaster will create proper settings when starting a new session

### Session ends immediately
This is now much more reliable with the simplified approach:
- CCMaster waits 3 seconds for Claude to start
- Requires 5 consecutive failures (10 seconds) before declaring session ended
- Uses simple process detection instead of complex PID tracking

### Auto-continue not working
- Ensure you're in watch mode (green "Watch mode: ON" message)
- Check that Claude has completed its response (shows "Idle" status)
- CCMaster will show clear error messages if auto-continue fails
- If the primary method fails, it will try sending to the frontmost Terminal

### Can't toggle watch mode
- Make sure the ccmaster window has focus
- The [w] key only works in the ccmaster monitoring window
- Watch mode toggle works independently of Terminal focus

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.