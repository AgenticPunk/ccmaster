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
- 🌐 **Dynamic Session Creation**: Claude can create new sessions on-demand using MCP tools
- 💬 **Cross-Session Communication**: Send messages and coordinate tasks between sessions
- 🔄 **Unified Session Management**: All sessions (original + MCP-created) tracked with consistent prefixes
- 🛡️ **Session Lifecycle Control**: CLI stays alive until all sessions end, proper cleanup on termination
- 💾 **Session Recovery**: Load and resume previous sessions with full context using `ccmaster load`
- 🗑️ **Session Management**: Delete unwanted sessions through interactive interface
- 🔚 **Auto-Close Sessions**: All Claude sessions automatically close when CCMaster exits
- 🧠 **PM Mode**: Claude analyzes project requirements and creates a truly collaborative team of specialized instances
- 🤝 **Real Team Collaboration**: All team members work in shared workspace, PM coordinates tasks and monitors progress
- 📋 **Dynamic Task Assignment**: PM sends specific tasks to team members based on project needs and progress
- 🔄 **Continuous Team Management**: PM runs indefinitely, coordinating team and responding to new requirements
- 📈 **Adaptive Team Growth**: Add new requirements anytime - PM creates new specialists AND coordinates with existing team

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

# PM Mode - Claude analyzes project and creates specialized instances
ccmaster pm "Create an e-commerce platform with React frontend and Node.js backend"

# PM Mode with options
ccmaster pm "Your project description" --no-watch  # Disable auto-continue
ccmaster pm "Your project description" --pm-template template.md  # Custom template

# List all sessions
ccmaster list

# Load and resume a previous session (interactive)
ccmaster load

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

CCMaster supports three modes of multi-agent creation:
1. **Pre-planned** (`--instances`) - Create a fixed number of identical sessions
2. **Dynamic** (MCP tools) - Claude creates new sessions during runtime
3. **PM Mode** (`pm` command) - Claude analyzes project and creates specialized team

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CCMaster  │────▶│ Claude Code 1│────▶│   Hooks 1   │
│   Monitor   │     └──────────────┘     └─────────────┘
│      +      │     ┌──────────────┐     ┌─────────────┐
│ MCP Server  │────▶│ Claude Code 2│────▶│   Hooks 2   │
│             │     └──────────────┘     └─────────────┘
│             │     ┌──────────────┐     ┌─────────────┐
│             │◀────│MCP-Created N │────▶│   Hooks N   │
└─────────────┘     └──────────────┘     └─────────────┘
       ▲                     │
       │                     │
       └─────────────────────┘
         Inter-Session Communication
```

Each session (original or MCP-created):
- Has its own Terminal window/tab with unique prefix ([1], [MCP-2])
- Maintains independent status tracking and auto-continue
- Has isolated hook configurations for clean monitoring
- Can communicate with other sessions via MCP tools
- Supports dynamic creation during runtime

### Session Recovery & Management

CCMaster provides powerful session recovery features:

```bash
# Launch the interactive session loader
ccmaster load
```

Features:
- **Interactive Selection**: Navigate through sessions with arrow keys
- **Session Details**: View ID, role, status, working directory, and start time
- **Load & Resume**: Press Enter to resume a session with full context
- **Delete Sessions**: Press 'd' to delete unwanted sessions and their logs
- **Context Restoration**: Previous prompts are included when resuming
- **Auto-Close on Exit**: All active Claude sessions close when CCMaster exits

When resuming a session:
1. Working directory is restored
2. Claude starts fresh and waits for your input
3. Full monitoring and watch mode support
4. **PM Sessions**: Automatically resumes all team members together

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

5. **MCP Server & Tools** (`ccmaster/mcp/`)
   - `server.py` - Main MCP server with session management tools
   - `tools.py` - Session management tool implementations
   - Dynamic session creation and coordination capabilities
   - Cross-session communication and monitoring
   - Automatic project configuration and Claude integration

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

## 🔗 MCP Integration & Multi-Agent Coordination

CCMaster provides seamless Model Context Protocol (MCP) integration, enabling powerful multi-agent workflows and inter-session communication:

### Automatic MCP Setup
When you run `ccmaster watch`, CCMaster automatically:
1. **Starts MCP Server**: Finds an available port (8080-8090) and launches the MCP server
2. **Project Configuration**: Creates `.mcp.json` in your project directory with correct server details
3. **Claude Integration**: Claude Code automatically detects and connects to the MCP server
4. **Session Management**: All sessions (original and MCP-created) are tracked and monitored

### Multi-Agent Session Creation
Claude can create new sessions on-demand using MCP tools:

```bash
# Create a new session for a specific task
/mcp__ccmaster__create_session working_dir="/path/to/project" watch_mode=true max_turns=50

# Output shows new session being tracked:
[1][14:30:22] ● Processing  
[MCP-2][14:30:25] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 3)
[MCP-2][14:30:26] ● Idle
```

### Available MCP Tools
CCMaster provides comprehensive session management tools within Claude:

**Session Management:**
- `list_sessions` - List all active and ended sessions with detailed status
- `get_session_status` - Get real-time status of any session
- `create_session` - Create new Claude Code sessions programmatically
- `kill_session` - Terminate specific sessions cleanly

**Inter-Session Communication:**
- `send_message_to_session` - Send prompts/commands between sessions
- `coordinate_sessions` - Orchestrate multiple sessions for complex tasks
- `get_session_logs` - Access session logs and conversation history

**Temporary Tasks:**
- `spawn_temp_session` - Create, execute, and cleanup temporary sessions
- `prompt` - Send messages to the CCMaster console (demo/debugging)

### Advanced Multi-Agent Workflows

**1. PM Mode - True Team Collaboration**
```bash
# Let Claude analyze and create a collaborative team:
ccmaster pm "Build a SaaS application with user management, billing, and analytics"

# PM Claude creates a true team that works together:
# - All team members share the same workspace (directory)
# - PM sends tasks to team members throughout development
# - Team members see each other's files and integrate their work
# - PM monitors progress and coordinates between team members

# Example team collaboration with error handling:
# 1. Frontend Dev creates components/UserProfile.jsx
# 2. Backend Dev sees it and creates matching API endpoints
# 3. PM runs the project: npm start
# 4. Error: "Cannot find module './UserProfile'"
# 5. PM assigns to Frontend: "Fix import error in App.jsx"
# 6. Frontend fixes, PM retests
# 7. Error: "API connection refused on port 3001"
# 8. PM assigns to Backend: "Start API server on port 3001"
# 9. Backend fixes, PM retests until everything works
# 10. PM coordinates deployment with DevOps

# Dynamic team growth - type in PM terminal:
"Add mobile apps for iOS and Android"
# PM creates iOS/Android devs AND coordinates with existing team

"Deploy to production on AWS"
# PM creates Cloud Architect AND coordinates deployment tasks
```

**2. Team Members Communicating Directly**
```bash
# Frontend needs something from Backend:
/mcp__ccmaster__send_message_to_session session_id="backend_dev" message="I need user profile API endpoint"

# Backend notifies completion:
/mcp__ccmaster__notify_completion task_description="User profile API" output_details="GET /api/user/:id returns user data"

# Designer broadcasts update:
/mcp__ccmaster__broadcast_to_team message="New design system ready in /design/tokens.json" sender_role="UI Designer"

# Managing dependencies:
/mcp__ccmaster__wait_for_dependency dependency_session="backend_dev" dependency_description="Authentication middleware"
```

**3. Task Coordination**
```bash
# Assign different parts of a project to different sessions:
/mcp__ccmaster__coordinate_sessions 
  task_description="Build e-commerce platform" 
  session_assignments='{
    "mcp_20250119_143022": "Build React frontend with cart and checkout",
    "mcp_20250119_143025": "Create Node.js API with payment integration", 
    "mcp_20250119_143028": "Set up PostgreSQL database and migrations"
  }'
```

**4. Cross-Session Communication**
```bash
# Send status updates between sessions:
/mcp__ccmaster__send_message_to_session 
  session_id="mcp_20250119_143022" 
  message="API endpoints are ready. Please update frontend to use /api/products and /api/cart"
  wait_for_response=true
```

**5. Session Monitoring & Control**
```bash
# Monitor all sessions:
/mcp__ccmaster__list_sessions include_ended=false

# Check specific session status:
/mcp__ccmaster__get_session_status session_id="mcp_20250119_143022"

# Get recent logs from a session:
/mcp__ccmaster__get_session_logs session_id="mcp_20250119_143022" lines=50
```

### Unified Session Management
CCMaster treats all sessions equally - original and MCP-created sessions have:
- **Auto-Continue Support**: All sessions support watch mode and auto-continuation
- **Session Prefixes**: Clear labeling ([1], [MCP-2], [MCP-3]) for easy identification
- **Terminal Tracking**: Proper window/tab tracking for accurate auto-continue
- **Lifecycle Management**: CLI stays alive until all sessions end
- **Status Monitoring**: Real-time status updates for all sessions

### Example Multi-Agent Output
```
🚀 Starting Claude session in /Users/yourname/project
📍 Session ID: 20250119_143022  
👁️  Watch mode: ON - MCP Server running on port 8082

[1][14:30:22] ● Processing
[1][14:30:25] ▶ User: "Create a multi-service architecture"
[1][14:30:28] ● Working → Using create_session
[MCP-2][14:30:30] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 3)
[1][14:30:32] ● Working → Using create_session  
[MCP-3][14:30:34] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 4)
[1][14:30:36] ● Working → Using coordinate_sessions
[MCP-2][14:30:38] ▶ Coordination: "Build React frontend components"
[MCP-3][14:30:38] ▶ Coordination: "Create Express.js API endpoints"
[1][14:30:40] ● Idle
[MCP-2][14:30:42] ● Working → Using Write
[MCP-3][14:30:43] ● Working → Using Write
[1][14:30:45] ▶ Auto-continue (1/∞)
```

### MCP Configuration
The MCP server automatically configures itself with these settings:

```json
{
  "mcp": {
    "enabled": true,
    "host": "localhost", 
    "port_range": [8080, 8090]
  }
}
```

Project `.mcp.json` is created automatically:
```json
{
  "mcpServers": {
    "ccmaster": {
      "command": "python",
      "args": ["/path/to/ccmaster/mcp/server.py"],
      "env": {
        "PORT": "8082"
      }
    }
  }
}
```

For detailed MCP implementation details, see [MCP_SESSION_INTEGRATION.md](MCP_SESSION_INTEGRATION.md)

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