# CCMaster Development Prompt

This is the comprehensive prompt that can be used to recreate the CCMaster project from scratch.

## Project Prompt

Create a CLI tool called `ccmaster` that manages Claude Code sessions with the following requirements:

### Core Functionality
1. **Automatic Terminal Launch**: When running `ccmaster`, automatically open a new macOS Terminal window and run `claude` command immediately
2. **Session Management**: Remember and track Claude Code sessions with unique IDs
3. **Continuous Monitoring**: The CLI should NOT exit until the Claude session ends - it should stay alive and monitor the session
4. **Status Tracking**: Monitor whether Claude is working or idle using Claude's hooks feature
5. **Watch Mode**: Automatically send "continue" when Claude becomes idle after completing a response
6. **Interactive Controls**: Press [w] during any session to toggle watch mode on/off

### Status Display Requirements
1. **Real-time Updates**: Print logs about every activity Claude performs
2. **Working/Idle States**: 
   - Show "Working" in GREEN when Claude is busy using tools
   - Show "Idle" in RED when Claude is done and waiting
   - Show "Processing" in YELLOW when processing user prompts
3. **Clean Output**: 
   - Each round of chat should only show ONE "Processing" and ONE "Idle"
   - Tool activities should be shown clearly (e.g., "Using Read", "Completed Read")
   - NO duplicate idle messages - only one idle per interaction cycle
4. **Watch Mode Display**:
   - Show current auto-continue count when active (e.g., "Auto-continue (5/100)")
   - Display remaining turns when toggling watch mode
   - Clear notification when max turns reached

### Watch Mode Features
1. **Basic Watch Mode**: `ccmaster watch` - unlimited auto-continues
2. **Limited Watch Mode**: `ccmaster watch --maxturn 100` - stops after 100 turns
3. **Turn Limit Behavior**:
   - When max turns reached, watch mode automatically disables
   - Pressing [w] resets the counter and re-enables watch mode
   - If Claude is idle when re-enabled, immediately sends continue
4. **Visual Feedback**:
   - All watch mode text in GREEN color
   - Shows "Watch mode: ON/OFF" status
   - Displays turn count in auto-continue messages

### Technical Implementation
1. **Hooks Integration**: Use Claude Code's hooks feature to detect activity:
   - PreToolUse: Set status to "working" when tools are used
   - UserPromptSubmit: Set status to "processing" and capture prompts
   - Stop: Set status to "idle" when Claude finishes responding
   
2. **Session Isolation**: 
   - Each session has its own hooks configuration
   - Backup and restore original Claude settings
   - Support multiple concurrent sessions

3. **Process Monitoring**:
   - Retry mechanism (10 attempts) for finding Claude process
   - Filter out ccmaster and python processes
   - Continue monitoring even if PID not found initially

4. **Keyboard Input**:
   - Non-blocking input detection using select and termios
   - Properly save and restore terminal settings
   - Handle keyboard interrupts gracefully

5. **File Structure**:
   ```
   ccmaster/
   ├── bin/ccmaster         # Main executable
   ├── hooks/              # Hook scripts
   │   ├── pre_tool_use.py
   │   ├── user_prompt_submit.py
   │   ├── stop_hook.py
   │   └── hook_utils.py
   └── setup.sh            # Installation script
   ```

### Commands
- `ccmaster` or `ccmaster start`: Start new session and monitor
- `ccmaster start -d /path`: Start in specific directory
- `ccmaster watch`: Start in watch mode (auto-continue)
- `ccmaster watch -d /path`: Watch mode in specific directory
- `ccmaster watch --maxturn 50`: Watch mode with 50 turn limit
- `ccmaster list`: List all sessions
- `ccmaster logs SESSION_ID`: View session logs
- `ccmaster prompts SESSION_ID`: View user prompts

### Key Challenges Solved
1. **Simplified Session Detection**: Basic process detection without complex PID tracking
2. **Hook Isolation**: Per-session hooks prevent conflicts between sessions
3. **Reliable Auto-Continue**: Direct Terminal tab detection with two-tier fallback system
4. **Robust Session Monitoring**: Tolerant monitoring (5 failures before declaring ended)
5. **Turn Limiting**: Graceful handling of max turns with reset capability
6. **Error Resilience**: Clear error messages and graceful degradation when automation fails

### Output Example
```
🚀 Starting Claude session in /Users/username/project
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

The tool should be simple, clear, and user-friendly, focusing on giving developers real-time visibility into what Claude is doing during a session while providing powerful automation features for long conversations.