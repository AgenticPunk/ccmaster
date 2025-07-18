# Changelog

All notable changes to CCMaster will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-01-18

### Added
- **Multi-Agent Support**: New `--instances` argument to manage multiple Claude sessions simultaneously
  - Launch and monitor multiple Claude sessions with `ccmaster watch --instances N`
  - Each session has independent status tracking and auto-continue
  - Unified view of all sessions with numbered prefixes `[1]`, `[2]`, etc.
  - Press `[w]` to toggle watch mode for all sessions at once
- **Thread-Safe Printing**: Added print lock mechanism for clean multi-session output
- **Terminal Window Monitoring**: Detects when Terminal window is closed and ends session immediately
- **Session-Specific Tracking**: Improved session isolation to prevent CCMaster from controlling wrong sessions

### Changed
- **ASCII Symbols**: Replaced all emoji symbols with clean ASCII/abstract symbols for better compatibility
  - 🚀 → ⟐ (launching/starting)
  - 📍 → ◆ (location marker)
  - 👁️ → ⊙ (watch mode on)
  - 👀 → ○ (watch mode off)
  - 🎯 → ✻ (target/all launched)
  - 🔍 → ◎ (search/process tracking)
  - 💀 → ☠ (death/session end)
  - ⚠️ → ▲ (warning)
  - ❌ → ✖ (error)
  - 🛑 → ■ (stop)
  - 💡 → → (hint/arrow)
  - 🔄 → ↻ (refresh/reset)
- **Message Queue Format**: Standardized to 5-tuple format for consistency across single and multi-agent modes
- **Session ID Format**: Added microseconds to prevent duplicate IDs when creating multiple sessions quickly

### Fixed
- **CLI Log Alignment**: Fixed messy output with overlapping text in raw terminal mode
- **Auto-Continue Behavior**: Now waits for first user prompt before auto-continuing in each session
- **Hook Response Format**: Fixed all hooks to return `{"allow": true}` instead of `{"status": "ok"}`
- **Hook Path Resolution**: Fixed symlink issues when ccmaster is installed in /usr/local/bin
- **Python Syntax Error**: Fixed improper try-except block indentation in pre_tool_use.py
- **Terminal Raw Mode**: Fixed print handling to properly switch between raw and normal modes

## [1.2.0] - 2025-01-18

### Added
- **Auto Permission Skip**: All Claude commands automatically append `--dangerously-skip-permissions` flag
- **Turn Limiting**: Added `--maxturn` argument to limit auto-continue cycles
- **Interactive Controls**: Press `[w]` to toggle watch mode during sessions
- **Terminal Window Detection**: Added window and tab tracking for precise auto-continue targeting

### Changed
- **Hook Format**: Updated to match Claude's expected structure with proper type fields
- **Default Directory**: CCMaster now always uses current working directory by default
- **Safe Print Method**: Implemented for proper terminal raw mode handling

### Fixed
- **Invalid Settings Warning**: Fixed hooks configuration format to match Claude's expectations
- **UserPromptSubmit Hook**: Fixed field name from 'prompt' to 'input'
- **Session Monitoring**: More reliable with 5 consecutive failures required before ending

## [1.1.0] - 2025-01-17

### Added
- **Watch Mode**: Automatic continuation when Claude becomes idle
- **Session History**: View all prompts and detailed logs for any session
- **Per-Session Hooks**: Each session has isolated hook configurations
- **Status Monitoring**: Real-time display of Claude's working status (Idle/Processing/Working)
- **Tool Activity Tracking**: Shows which tools Claude is currently using

### Changed
- **Simplified Architecture**: More reliable process detection and monitoring
- **Multi-tier Fallback**: For auto-continue functionality

## [1.0.0] - 2025-01-17

### Added
- **One-Command Launch**: Automatically opens Terminal and starts Claude Code sessions
- **Session Management**: Create, list, and view logs for all sessions
- **Beautiful Output**: Color-coded status indicators for easy reading
- **macOS Support**: Uses AppleScript for Terminal automation
- **Configuration System**: Customizable settings in ~/.ccmaster/config.json

### Project Structure
```
ccmaster/
├── ccmaster/
│   ├── bin/
│   │   └── ccmaster          # Main executable
│   └── hooks/
│       ├── pre_tool_use.py    # Tool usage tracking
│       ├── user_prompt_submit.py # User prompt capture
│       ├── stop_hook.py       # Response completion detection
│       └── hook_utils.py      # Shared hook utilities
├── setup.sh                   # Installation script
├── README.md                  # English documentation
├── README_CN.md              # Chinese documentation
├── CHANGELOG.md              # This file
└── LICENSE                   # MIT License
```

### Technical Details
- Written in Python 3.6+
- Requires macOS for Terminal automation
- Uses Claude Code CLI hooks system for monitoring
- Thread-safe operations for concurrent session management

---

## Version History

- **2.0.0** - Multi-agent support and professional ASCII symbols
- **1.2.0** - Enhanced automation and reliability improvements
- **1.1.0** - Watch mode and real-time monitoring
- **1.0.0** - Initial release with core functionality

## Future Roadmap

- [ ] Cross-platform support (Windows Terminal, Linux)
- [ ] Web UI for session management
- [ ] Session collaboration features (agents talking to each other)
- [ ] Session templates and presets
- [ ] Integration with version control systems
- [ ] Export session history to various formats
- [ ] Performance metrics and analytics