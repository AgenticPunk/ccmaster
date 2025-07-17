# CCMaster Development Prompt

This is the comprehensive prompt that can be used to recreate the CCMaster project from scratch.

## Project Prompt

Create a CLI tool called `ccmaster` that manages Claude Code sessions with the following requirements:

### Core Functionality
1. **Automatic Terminal Launch**: When running `ccmaster`, automatically open a new macOS Terminal window and run `claude` command immediately
2. **Session Management**: Remember and track Claude Code sessions with unique IDs
3. **Continuous Monitoring**: The CLI should NOT exit until the Claude session ends - it should stay alive and monitor the session
4. **Status Tracking**: Monitor whether Claude is working or idle using Claude's hooks feature

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

### Technical Implementation
1. **Hooks Integration**: Use Claude Code's hooks feature to detect activity:
   - PreToolUse: Set status to "working" when tools are used
   - PostToolUse: Don't set to idle (to avoid duplicates)
   - UserPromptSubmit: Set status to "processing"
   
2. **Session Isolation**: Each session should have its own status file to prevent conflicts

3. **Smart Idle Detection**: 
   - Track conversation cycles to prevent duplicate idle messages
   - Auto-detect idle after 2 seconds of inactivity
   - Only show idle once per interaction

4. **File Structure**:
   ```
   ccmaster/
   ├── bin/ccmaster         # Main executable
   ├── hooks/              # Hook scripts
   │   ├── pre_tool_use.py
   │   ├── post_tool_use.py
   │   └── user_prompt_submit.py
   └── setup.sh            # Installation script
   ```

### Commands
- `ccmaster` or `ccmaster start`: Start new session and monitor
- `ccmaster start -d /path`: Start in specific directory
- `ccmaster list`: List all sessions
- `ccmaster logs SESSION_ID`: View session logs

### Key Challenges Solved
1. **Path Resolution**: Use `.resolve()` to handle symlinks properly
2. **Hook Configuration**: Create proper Claude settings in `~/.claude/settings.json`
3. **Duplicate Messages**: Use cycle tracking and session-specific status files
4. **Clean Display**: Separate tool activities from status updates

### Output Example
```
🚀 Starting Claude session in /Users/username
📍 Session ID: 20250718_021539

[02:15:43] ● Processing
[02:15:44] → Using Read
[02:15:45] ✓ Completed Read
[02:15:48] ● Idle
```

The tool should be simple, clear, and user-friendly, focusing on giving developers real-time visibility into what Claude is doing during a session.