# CCMaster Implementation Guide

This document provides detailed information about CCMaster's internal implementation, architecture design, and technical solutions.

## 📐 Architecture Overview

CCMaster uses an event-driven architecture that monitors Claude Code sessions in real-time through its hooks system:

```
┌──────────────────────────────────────────────────────────────┐
│                      User Interface Layer                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │Command Parser│  │Status Display│  │Keyboard Input(w) │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────┐
│                       Core Logic Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │Session Manager│ │  Watch Mode  │  │ Turn Controller  │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────┐
│                     Monitoring System Layer                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │Process Monitor│ │Status Monitor│  │  Log Collector   │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────┐
│                         Hooks System                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │PreToolUse   │  │UserPromptSubmit│ │    Stop Hook    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 🔧 Core Implementation Principles

### 1. Session Management

Each session has a unique ID (format: `YYYYMMDD_HHMMSS`) used for:
- Isolating hook configurations between sessions
- Tracking session state and logs
- Managing session lifecycle

```python
def start_session_and_monitor(self, working_dir=None, watch_mode=False, max_turns=None):
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create per-session hooks configuration
    settings_file, backup_file = self.create_hooks_config(session_id)
    
    # Launch Claude Code
    applescript = f'''
    tell application "Terminal"
        activate
        set newWindow to do script "cd {working_dir} && {claude_cmd}"
        return id of window 1
    end tell
    '''
```

### 2. Hooks System

CCMaster uses three hooks to monitor Claude Code's state:

#### PreToolUse Hook
- **Trigger**: When Claude is about to use a tool
- **Information**: Tool name
- **State Update**: Set to "working"

```python
def main():
    session_id = sys.argv[1]
    utils = HookUtils(session_id)
    data = utils.read_hook_input()
    tool_name = data.get('tool_name', 'unknown')
    utils.update_status('working', tool=tool_name, action=f'Using {tool_name}')
```

#### UserPromptSubmit Hook
- **Trigger**: When user submits a new prompt
- **Information**: Complete user prompt
- **State Update**: Set to "processing"

```python
def main():
    session_id = sys.argv[1]
    utils = HookUtils(session_id)
    data = utils.read_hook_input()
    user_prompt = data.get('prompt', '')
    
    # Save prompt to dedicated log file
    with open(prompt_log_file, 'a') as f:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt': user_prompt
        }
        f.write(json.dumps(log_entry) + '\n')
```

#### Stop Hook
- **Trigger**: When Claude completes its response
- **Information**: Response completion signal
- **State Update**: Set to "idle"

### 3. Process Monitoring

Enhanced process detection mechanism:

```python
def find_claude_pid(self, max_attempts=10):
    our_pid = os.getpid()
    
    for attempt in range(max_attempts):
        time.sleep(1)
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        for line in result.stdout.strip().split('\n'):
            # Exclude ccmaster itself and python processes
            if self.config['claude_code_command'] in line \
               and 'ccmaster' not in line \
               and 'python' not in line:
                pid = int(line.split()[1])
                if pid != our_pid:
                    return pid
```

### 4. Watch Mode

Core watch mode logic:

```python
# When idle state is detected
if 'Idle' in message:
    if watch_mode and has_seen_first_prompt:
        # Check if max turns reached
        if max_turns is None or auto_continue_count < max_turns:
            auto_continue_pending = True
            continue_countdown = 1
        else:
            # Max turns reached, auto-disable watch mode
            print(f"🛑 Max auto-continue turns ({max_turns}) reached")
            watch_mode = False

# Send auto-continue command
if continue_countdown == 0:
    self.send_prompt_to_terminal(terminal_window_id, "continue")
    auto_continue_count += 1
```

### 5. Keyboard Interaction

Non-blocking input detection:

```python
def check_keyboard_input(self):
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

# In main loop
key = self.check_keyboard_input()
if key == 'w':
    was_at_max_turns = max_turns and auto_continue_count >= max_turns
    watch_mode = not watch_mode
    
    if watch_mode and was_at_max_turns:
        # Reset counter
        auto_continue_count = 0
        # If currently idle, continue immediately
        if self.current_status == 'idle':
            self.send_prompt_to_terminal(terminal_window_id, "continue")
```

### 6. Auto-Continue Control

Sending commands to Terminal via AppleScript:

```python
def send_prompt_to_terminal(self, window_id, prompt):
    clear_script = f'''
    tell application "Terminal"
        activate
        set frontmost of window id {window_id} to true
    end tell
    
    tell application "System Events"
        tell process "Terminal"
            keystroke return  -- Clear any interrupted state
            delay 0.2
            keystroke "{prompt}"
            keystroke return
        end tell
    end tell
    '''
```

## 📊 Data Flow

### State Update Flow

```
Claude Code ──(Hook Event)──> Hook Script ──(Update)──> Status File
                                    │
                                    └──(Log)──> Log File
                                    
CCMaster ──(Monitor)──> Status File ──(Parse)──> Display Update
                              │
                              └──(Queue)──> Real-time Display
```

### Auto-Continue Flow

```
1. Stop Hook triggers ──> State set to "idle"
2. CCMaster detects idle state
3. Check conditions:
   - In watch mode?
   - Has seen first prompt?
   - Under max turns limit?
4. If conditions met ──> 1-second countdown
5. Countdown ends ──> AppleScript sends "continue"
6. Update counter
```

## 🛠 Technical Details

### File Structure

```
~/.ccmaster/
├── config.json              # Global configuration
├── sessions.json            # Session metadata
├── status/                  # Real-time status
│   └── {session_id}.json    # Individual session status
└── logs/                    # Log files
    ├── {session_id}.log     # Session event log
    └── {session_id}_prompts.log  # User prompts log
```

### Status File Format

```json
{
    "state": "working",
    "last_tool": "Edit",
    "current_action": "Using Edit",
    "timestamp": "2024-01-24T14:30:24.123456",
    "session_id": "20240124_143022"
}
```

### Session Metadata Format

```json
{
    "20240124_143022": {
        "id": "20240124_143022",
        "started_at": "2024-01-24T14:30:22.123456",
        "working_dir": "/Users/name/project",
        "status": "running",
        "pid": 12345,
        "last_activity": "2024-01-24T14:35:45.123456"
    }
}
```

## 🔍 Key Technical Decisions

### 1. Why Per-Session Hooks?

- **Isolation**: Each session is independent
- **Security**: Original settings restored after session ends
- **Flexibility**: Multiple CCMaster sessions can run simultaneously

### 2. Why AppleScript?

- Native macOS support, no additional dependencies
- Precise Terminal window control
- Supports keyboard input simulation

### 3. Why Polling Instead of Event Push?

- Claude Code hooks system limitations
- Simplified implementation, avoiding complex IPC
- 0.2-second polling interval is sufficiently responsive

### 4. Turn Limit Design Considerations

- Prevents infinite loops consuming resources
- Gives users explicit control
- Supports manual reset, balancing automation and control

## 🚀 Performance Optimizations

1. **Simplified Process Detection**
   - Uses basic `pgrep` and `ps` commands for reliability
   - No complex PID tracking or retries
   - Tolerant monitoring (5 failures before declaring ended)

2. **Streamlined Auto-Continue**
   - Direct Terminal tab detection using AppleScript
   - Two-tier fallback system for maximum reliability
   - Clear success/failure feedback without complex timing

3. **Efficient Monitoring**
   - Simple background thread checking every 2 seconds
   - No complex process verification or multiple methods
   - Minimal resource usage with straightforward logic

## 🔒 Error Handling

1. **Session Monitoring**
   - Waits 3 seconds for Claude to start before monitoring
   - Requires 5 consecutive failures before declaring session ended
   - Clear feedback when sessions actually end

2. **Auto-Continue Reliability**
   - Primary method: Find Claude tab and send continue
   - Fallback method: Send to frontmost Terminal window
   - Clear error messages when auto-continue fails

3. **Graceful Degradation**
   - If auto-continue fails, user gets clear instructions
   - Session monitoring continues even if auto-continue breaks
   - No complex fallback chains that can introduce bugs

## 📝 Summary

CCMaster cleverly leverages Claude Code's hooks system to achieve complete session monitoring and automation control. Its design emphasizes:

- **User Experience**: Beautiful output, intuitive interaction
- **Reliability**: Robust error handling, multiple safeguards
- **Flexibility**: Configurable parameters, interactive controls
- **Performance**: Optimized polling, minimal resource usage

This design makes CCMaster a powerful tool for enhancing the Claude Code experience.