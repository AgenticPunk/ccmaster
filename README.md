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

# List all sessions
ccmaster list

# View session logs
ccmaster logs 20240124_143022

# View user prompts for a session
ccmaster prompts 20240124_143022
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

### Key Components

1. **Session Manager** (`ccmaster/bin/ccmaster`)
   - Main orchestrator
   - Manages Terminal windows via AppleScript
   - Handles real-time monitoring
   - Implements watch mode logic

2. **Hook System** (`ccmaster/hooks/`)
   - `pre_tool_use.py` - Tracks tool usage
   - `user_prompt_submit.py` - Captures user prompts
   - `stop_hook.py` - Detects when Claude finishes responding
   - Each session gets its own hook configuration

3. **Status Tracking**
   - Real-time status files in `~/.ccmaster/status/`
   - Session logs in `~/.ccmaster/logs/`
   - User prompts in separate log files

## 🔧 Configuration

Configuration file location: `~/.ccmaster/config.json`

```json
{
  "claude_code_command": "claude",
  "monitor_interval": 0.5
}
```

Note: CCMaster always uses the current working directory by default when starting a session.

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

### Session ends immediately
This usually happens when Claude process detection fails. CCMaster now includes:
- Retry mechanism (10 attempts)
- Better process filtering to exclude ccmaster itself
- Debug logging for troubleshooting

### Auto-continue not working
- Ensure you're in watch mode (green "Watch mode: ON" message)
- Check that Claude has completed its response (shows "Idle" status)
- Verify Terminal permissions for automation

### Can't toggle watch mode
- Make sure the ccmaster window has focus
- The [w] key only works in the ccmaster monitoring window

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.