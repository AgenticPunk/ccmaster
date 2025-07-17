# CCMaster - Claude Code Session Manager

A CLI tool that launches Claude Code sessions and continuously monitors their activity with real-time status updates.

## Features

- **Automatic Terminal Launch**: Opens new Terminal windows with Claude Code
- **Real-time Status Monitoring**: Shows colored status indicators:
  - 🟡 **Processing** (yellow) - When processing your prompt
  - 🟢 **Working** (green) - When Claude is actively using tools
  - 🔴 **Idle** (red) - When Claude has completed all tasks
- **Tool Activity Tracking**: Displays each tool Claude uses with start/completion markers
- **Session Management**: Tracks all Claude sessions with unique IDs
- **Clean Output**: Shows only essential information with one idle message per interaction
- **Persistent Logs**: All activities are logged for later review

## Installation

1. Clone or download this repository
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
3. If you can't write to `/usr/local/bin`, add the ccmaster bin directory to your PATH:
   ```bash
   export PATH="/path/to/ccmaster/ccmaster/bin:$PATH"
   ```

## Usage

### Start a new session (default command)
```bash
# Start in current directory
ccmaster

# Start in specific directory
ccmaster start -d /path/to/project
```

When you run ccmaster, it will:
1. Open a new Terminal window with Claude
2. Display real-time status updates
3. Continue monitoring until the Claude session ends

Example output:
```
🚀 Starting Claude session in /Users/liuyuantao
📍 Session ID: 20250718_021539

[02:15:43] ● Processing
[02:15:44] → Using Read
[02:15:46] → Using Edit
[02:15:48] → Using Write
[02:15:52] ● Idle
```

Press `Ctrl+C` to stop monitoring (Claude continues running).

### List all sessions
```bash
ccmaster list
```

Shows all sessions with their status, PID, and working directory.

### View session logs
```bash
ccmaster logs SESSION_ID
```

Displays the complete activity log for a specific session.

## How It Works

1. **Hooks Integration**: CCMaster configures Claude's hooks to track:
   - `PreToolUse`: Detects when Claude starts using a tool
   - `UserPromptSubmit`: Detects when you submit a prompt

2. **Status Tracking**: Each session has its own status file in `~/.ccmaster/status/`

3. **Smart Idle Detection**: Shows exactly one idle message per interaction by:
   - Tracking conversation cycles
   - Auto-detecting idle state after 2 seconds of inactivity
   - Preventing duplicate idle notifications

4. **Session Isolation**: Each session operates independently with its own:
   - Status file
   - Log file
   - Process monitoring

## Configuration

Configuration is stored in `~/.ccmaster/config.json`:
```json
{
  "claude_code_command": "claude",
  "default_working_dir": "/Users/username",
  "monitor_interval": 0.5
}
```

## File Structure

```
~/.ccmaster/
├── config.json          # Global configuration
├── sessions.json        # Session registry
├── status/             # Session status files
│   └── SESSION_ID.json
└── logs/               # Session logs
    └── SESSION_ID.log
```

## Troubleshooting

- **Command not found**: Make sure ccmaster is in your PATH
- **No status updates**: Check that Claude's settings allow hooks
- **Multiple idle messages**: Update to the latest version

## Requirements

- macOS (uses AppleScript for Terminal control)
- Python 3.6+
- Claude Code CLI installed and accessible as `claude`