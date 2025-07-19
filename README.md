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

# Show job queue summary across all sessions
ccmaster jobs

# Check MCP server status
ccmaster mcp status

# Remove CCMaster from project .mcp.json  
ccmaster mcp remove
```

### Interactive Controls

During a session, you can use keyboard shortcuts:
- **[w]** - Toggle watch mode on/off
  - When max turns is reached, pressing [w] resets the counter and immediately continues
- **[j]** - Show job queue summary across all sessions
- **[q]** - Quit CCMaster

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

CCMaster supports both pre-planned (`--instances`) and dynamic (MCP-created) session management:

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
2. **Project Configuration**: Creates/updates `.mcp.json` in your project directory with the latest server details
3. **Configuration Updates**: Always ensures `.mcp.json` has the latest CCMaster tools and configuration
4. **Fallback Support**: If Claude CLI fails, directly creates/updates `.mcp.json` file
5. **Claude Integration**: Claude Code automatically detects and connects to the MCP server
6. **Session Management**: All sessions (original and MCP-created) are tracked and monitored

CCMaster will:
- Update existing `.mcp.json` files to the latest configuration while preserving other servers
- Show all available MCP tools after configuration
- Create the configuration file even if the Claude CLI is not available

### Multi-Agent Session Creation
Claude can create new sessions on-demand using MCP tools:

```bash
# Create a new session for a specific task
/mcp__ccmaster__session action="create" working_dir="/path/to/project" watch_mode=true max_turns=50

# Output shows new session being tracked:
[1][14:30:22] ● Processing  
[MCP-2][14:30:25] 🚀 Launched Claude in Terminal (Window: 4211, Tab: 3)
[MCP-2][14:30:26] ● Idle
```

### Available MCP Tools
CCMaster provides 7 consolidated tools for comprehensive session management:

**1. `session` - Session Management**
Manage Claude Code sessions with various actions:
- `action="create"` - Create new Claude Code sessions programmatically
- `action="kill"` - Terminate specific sessions cleanly
- `action="get_status"` - Get real-time status of any session
- `action="get_logs"` - Access session logs and conversation history
- `action="watch"` - Enable watch mode for a specific session with optional max turns
- `action="unwatch"` - Disable watch mode for a specific session
- `action="interrupt"` - Interrupt a session that is currently processing (sends Ctrl+C)
- `action="continue"` - Send a continue command to an idle session with optional custom message
- `action="spawn_temp"` - Create, execute, and cleanup temporary sessions
- `action="coordinate"` - Orchestrate multiple sessions for complex tasks

**2. `communicate` - Multi-Method Communication**
Send messages via different methods:
- `action="send_message"` - Send prompts/commands directly to a session
- `action="send_to_member"` - Send a message to a team member by their identity
- `action="broadcast"` - Send a message to multiple sessions simultaneously with filtering
- `action="send_mail"` - Send asynchronous mail that won't interrupt work
- `action="check_mail"` - Check mailbox for unread messages (auto-checks when idle)
- `action="reply_mail"` - Reply to a mail message with optional reply-all
- `action="list_mail"` - List mail messages with filtering by folder, sender, priority

**3. `job` - Job Queue Management**
Manage prioritized job queues:
- `action="send_to_session"` - Send a prioritized job to a session's queue
- `action="send_to_member"` - Send a job to a team member's queue by identity
- `action="list"` - List jobs in queue with status and priority filtering
- `action="cancel"` - Cancel a pending job with reason
- `action="get_status"` - Get detailed status of a specific job including dependencies
- `action="complete"` - Mark a job as completed with results and artifacts

**4. `team` - Team Management**
Manage team identities and members:
- `action="set_identity"` - Assign a human-readable identity/role to a session (e.g., 'designer', 'developer_1')
- `action="list_members"` - List all team members with their identities and session information

**5. `list_sessions` - Quick Session Overview**
List all active and ended sessions with detailed status (no action parameter needed)

**6. `prompt` - Console Messaging**
Send messages to the CCMaster console (useful for debugging/demos)

**7. `kill_self` - Self-Termination**
Allow a session to terminate itself when task is complete or unrecoverable

### Advanced Multi-Agent Workflows

**1. Dynamic Session Creation**
```bash
# Claude can create specialized sessions on demand:
/mcp__ccmaster__session action="create" working_dir="/frontend" watch_mode=true
/mcp__ccmaster__session action="create" working_dir="/backend" watch_mode=true
/mcp__ccmaster__session action="create" working_dir="/docs" watch_mode=false max_turns=1
```

**2. Task Coordination**
```bash
# Assign different parts of a project to different sessions:
/mcp__ccmaster__session action="coordinate" 
  task_description="Build e-commerce platform" 
  session_assignments='{
    "mcp_20250119_143022": "Build React frontend with cart and checkout",
    "mcp_20250119_143025": "Create Node.js API with payment integration", 
    "mcp_20250119_143028": "Set up PostgreSQL database and migrations"
  }'
```

**3. Cross-Session Communication**
```bash
# Send status updates between sessions:
/mcp__ccmaster__communicate action="send_message" 
  session_id="mcp_20250119_143022" 
  message="API endpoints are ready. Please update frontend to use /api/products and /api/cart"
  wait_for_response=true
```

**4. Session Monitoring & Control**
```bash
# Monitor all sessions:
/mcp__ccmaster__list_sessions include_ended=false

# Check specific session status:
/mcp__ccmaster__session action="get_status" session_id="mcp_20250119_143022"

# Get recent logs from a session:
/mcp__ccmaster__session action="get_logs" session_id="mcp_20250119_143022" lines=50

# Enable watch mode on a sub-agent:
/mcp__ccmaster__session action="watch" session_id="mcp_20250119_143022" max_turns=20

# Disable watch mode when task is complete:
/mcp__ccmaster__session action="unwatch" session_id="mcp_20250119_143022"
```

**5. Intelligent Agent Control**
Agents can dynamically control sub-agent behavior:
```bash
# Create a specialized agent and enable watch mode
/mcp__ccmaster__session action="create" working_dir="/backend" watch_mode=false
# Agent evaluates complexity and decides to enable watch mode
/mcp__ccmaster__session action="watch" session_id="mcp_20250119_143022" max_turns=50

# After monitoring progress, agent can adjust:
/mcp__ccmaster__session action="unwatch" session_id="mcp_20250119_143022"
# Send final instructions manually
/mcp__ccmaster__communicate action="send_message" session_id="mcp_20250119_143022" message="Complete the remaining tests"
```

**6. Fine-Grained Session Control**
Manage session execution with interrupt and continue:
```bash
# Interrupt a session that's taking too long or going off-track
/mcp__ccmaster__session action="interrupt" session_id="mcp_20250119_143022" reason="Refocusing on core requirements"

# Continue a session with specific guidance
/mcp__ccmaster__session action="continue" session_id="mcp_20250119_143022" message="Focus on implementing the authentication module first"

# Coordinate multiple sessions with precise control
/mcp__ccmaster__session action="get_status" session_id="mcp_20250119_143022"
# If status is "working" on wrong task, interrupt and redirect
/mcp__ccmaster__session action="interrupt" session_id="mcp_20250119_143022" 
/mcp__ccmaster__session action="continue" session_id="mcp_20250119_143022" message="Please prioritize the API endpoints instead"
```

**7. Session Self-Termination**
Sessions can terminate themselves when their task is complete:
```bash
# A session completes its assigned task and self-terminates
/mcp__ccmaster__kill_self reason="Task completed successfully" final_message="API endpoints implemented and tested"

# A session encounters an unrecoverable error
/mcp__ccmaster__kill_self reason="Missing required dependencies" final_message="Cannot proceed without database credentials"

# Coordinated workflow with self-termination
# Main agent creates temporary helper sessions that clean up after themselves
/mcp__ccmaster__session action="create" working_dir="/tests" watch_mode=false
# Helper session runs tests and terminates when done
/mcp__ccmaster__kill_self reason="Test suite completed" final_message="All 45 tests passed"
```

**8. Team-Based Session Management**
Manage sessions as team members with human-readable identities:
```bash
# Create a development team
/mcp__ccmaster__session action="create" working_dir="/frontend" watch_mode=true
/mcp__ccmaster__team action="set_identity" session_id="mcp_20250119_143022" identity="frontend_dev"

/mcp__ccmaster__session action="create" working_dir="/backend" watch_mode=true  
/mcp__ccmaster__team action="set_identity" session_id="mcp_20250119_143025" identity="backend_dev"

/mcp__ccmaster__session action="create" working_dir="/design" watch_mode=false
/mcp__ccmaster__team action="set_identity" session_id="mcp_20250119_143028" identity="designer"

# List team members
/mcp__ccmaster__team action="list_members"
# Output shows:
# Team has 3 members (3 active)
# - designer: idle in /design
# - frontend_dev: working in /frontend  
# - backend_dev: processing in /backend

# Communicate with team members by role
/mcp__ccmaster__communicate action="send_to_member" member="designer" message="Please create mockups for the new dashboard"
/mcp__ccmaster__communicate action="send_to_member" member="frontend_dev" message="The API endpoints are ready at /api/v2"
/mcp__ccmaster__communicate action="send_to_member" member="backend_dev" message="Frontend needs the user profile endpoint ASAP"

# Control team members
/mcp__ccmaster__session action="watch" session_id="designer"  # Can still use session_id
/mcp__ccmaster__session action="interrupt" session_id="backend_dev" reason="Switching priorities"
/mcp__ccmaster__session action="continue" session_id="backend_dev" message="Focus on user profile endpoint first"
```

**9. Advanced Team Coordination**
Build complex multi-agent workflows with team semantics:
```bash
# Project manager creates specialized team
/mcp__ccmaster__session action="create" working_dir="/project" watch_mode=true
/mcp__ccmaster__team action="set_identity" session_id="mcp_20250119_143030" identity="architect"

# Architect creates the development team
/mcp__ccmaster__session action="create" working_dir="/services/auth" watch_mode=true
/mcp__ccmaster__team action="set_identity" session_id="mcp_20250119_143031" identity="auth_specialist"

/mcp__ccmaster__session action="create" working_dir="/services/payment" watch_mode=true
/mcp__ccmaster__team action="set_identity" session_id="mcp_20250119_143032" identity="payment_specialist"

# Team collaboration with identities showing in logs
# Console output shows:
[architect][14:30:22] ● Processing
[auth_specialist][14:30:25] ● Idle
[payment_specialist][14:30:26] ● Working → Using Write

# Architect coordinates the team
/mcp__ccmaster__communicate action="send_to_member" member="auth_specialist" message="Implement OAuth2 with refresh tokens"
/mcp__ccmaster__communicate action="send_to_member" member="payment_specialist" message="Integrate Stripe for subscriptions"

# Monitor team progress
/mcp__ccmaster__team action="list_members" include_inactive=false
# Each member's status, working directory, and activity is shown
```

**10. Broadcasting Messages**
Send messages to multiple sessions simultaneously:
```bash
# Broadcast to all active sessions (excludes self by default)
/mcp__ccmaster__communicate action="broadcast" message="Team meeting in 5 minutes - please save your work"

# Broadcast to specific team members only
/mcp__ccmaster__communicate action="broadcast" message="Frontend team, please review the new API docs" whitelist_members='["frontend_dev", "designer"]'

# Broadcast to all except specific members
/mcp__ccmaster__communicate action="broadcast" message="Server restart in 10 minutes" blacklist_members='["qa_tester"]'

# Complex broadcast with multiple filters
/mcp__ccmaster__communicate action="broadcast" \
  message="Critical security update - apply patch immediately" \
  whitelist_members='["backend_dev", "auth_specialist", "payment_specialist"]' \
  blacklist_sessions='["mcp_20250119_143099"]' \
  exclude_self=true

# Include self in broadcast (useful for announcements)
/mcp__ccmaster__communicate action="broadcast" message="Project deadline moved to Friday" exclude_self=false

# Emergency broadcast - interrupt and notify
# First interrupt all working sessions
/mcp__ccmaster__list_sessions  # Get session list
/mcp__ccmaster__session action="interrupt" session_id="backend_dev" reason="Emergency broadcast"
/mcp__ccmaster__session action="interrupt" session_id="frontend_dev" reason="Emergency broadcast"
# Then broadcast when they're idle
/mcp__ccmaster__communicate action="broadcast" message="URGENT: Production server is down - all hands on deck"
```

**Broadcast Scenarios:**
```bash
# Scenario 1: Daily standup reminder
/mcp__ccmaster__communicate action="broadcast" message="Daily standup starting - share your updates"

# Scenario 2: Coordinated deployment
/mcp__ccmaster__communicate action="broadcast" message="Starting deployment process - freeze all commits" whitelist_members='["backend_dev", "frontend_dev", "devops"]'

# Scenario 3: Selective team communication  
/mcp__ccmaster__communicate action="broadcast" message="Design review meeting - join video call" whitelist_members='["designer", "frontend_dev", "product_manager"]'

# Scenario 4: System maintenance
/mcp__ccmaster__communicate action="broadcast" message="System maintenance in 30 minutes - please commit your changes"

# Console output during broadcast:
[architect][14:45:00] Broadcasting to 5 sessions
[frontend_dev][14:45:01] Broadcast received: System maintenance in 30 minutes...
[backend_dev][14:45:01] Broadcast received: System maintenance in 30 minutes...
[designer][14:45:01] Broadcast received: System maintenance in 30 minutes...
[qa_tester][14:45:01] Broadcast received: System maintenance in 30 minutes...
[devops][14:45:01] Broadcast received: System maintenance in 30 minutes...
[architect][14:45:02] Broadcast complete: 5 succeeded, 0 failed
```

**11. Asynchronous Mail System**
Send non-interrupting mail messages between team members:

```bash
# Send mail to specific team members
/mcp__ccmaster__communicate action="send_mail" \
  subject="API Design Review" \
  body="Please review the proposed API design at /docs/api-v2.md and provide feedback" \
  to_members='["frontend_dev", "backend_dev"]' \
  priority="normal"

# Send urgent mail to all sessions
/mcp__ccmaster__communicate action="send_mail" \
  subject="Critical Security Update" \
  body="Security vulnerability found in auth module. Please apply patch ASAP." \
  priority="urgent"

# Check your mailbox
/mcp__ccmaster__communicate action="check_mail" unread_only=true limit=5
# Output:
# You have 3 unread mail(s)
# - From: architect - "Critical Security Update" (urgent)
# - From: frontend_dev - "Re: API Design Review" (normal)
# - From: qa_tester - "Test Results for v2.1" (normal)

# Read and reply to mail
/mcp__ccmaster__communicate action="reply_mail" \
  mail_id="a1b2c3d4" \
  body="Thanks for the update. I've applied the security patch and all tests are passing."

# List all mail with filters
/mcp__ccmaster__communicate action="list_mail" folder="inbox" priority="urgent" unread_only=true

# Mail workflow example
# 1. Project manager sends task assignments via mail
/mcp__ccmaster__communicate action="send_mail" \
  subject="Sprint 3 Task Assignments" \
  body="Frontend: Dashboard redesign\nBackend: Payment API\nQA: Test automation setup" \
  to_members='["frontend_dev", "backend_dev", "qa_tester"]'

# 2. Team members check mail when idle (automatic notification)
[frontend_dev][10:30:45] ● Idle
[frontend_dev][10:30:45] 📬 You have 1 unread mail(s)

# 3. Developer reads mail and starts working
/mcp__ccmaster__communicate action="check_mail"
# Sees task assignment, begins work

# 4. Developer sends progress update via mail
/mcp__ccmaster__communicate action="send_mail" \
  subject="Dashboard Progress Update" \
  body="Completed 60% of dashboard redesign. New mockups in /design/dashboard-v2/" \
  to_members='["architect", "designer"]'
```

**Mail System Features:**
- **Non-interrupting**: Mail doesn't interrupt active work
- **Auto-notification**: Sessions see mail count when idle
- **Priority levels**: low, normal, high, urgent
- **Reply chains**: Track conversation threads
- **Persistent storage**: Mail saved in ~/.ccmaster/mailbox/
- **Smart filtering**: By sender, priority, read status

**Mail vs Broadcast vs Message:**
```bash
# Mail: Asynchronous, non-interrupting, persistent
/mcp__ccmaster__communicate action="send_mail" subject="Weekly Report" body="Please submit by Friday"

# Broadcast: Immediate, interrupts idle sessions only
/mcp__ccmaster__communicate action="broadcast" message="Server restart in 5 minutes"

# Message: Direct, waits for idle, one recipient
/mcp__ccmaster__communicate action="send_to_member" member="backend_dev" message="Can you check the API?"
```

**12. Job Queue System (Fully Automated)**
CCMaster automatically executes jobs when sessions become idle - no manual intervention needed!

**IMPORTANT**: Job automation only works when CCMaster is actively monitoring sessions. Jobs will NOT execute if:
- CCMaster is not running (you must have an active `ccmaster watch` session)
- The session was started outside of CCMaster
- CCMaster monitoring has been stopped

```bash
# First, ensure CCMaster is monitoring sessions:
ccmaster watch  # Or ccmaster watch --instances 3 for multiple sessions

# Then send high-priority job to a team member
/mcp__ccmaster__job action="send_to_member" \
  member="backend_dev" \
  title="Fix Critical Auth Bug" \
  description="Users cannot login. Error 500 on POST /api/auth/login. Check auth middleware and database connection." \
  priority="p0"

# CCMaster will:
# 1. Add job to backend_dev's queue
# 2. Show if they're idle (job starts immediately) or busy (queued)
# 3. Automatically start the job when they become idle (only if CCMaster is monitoring)
# 4. Provide clear instructions to complete the job
# 5. Show completion notifications when done

# Send job with dependencies
/mcp__ccmaster__job action="send_to_session" \
  session_id="mcp_20250119_143022" \
  title="Deploy Frontend" \
  description="Build and deploy the frontend to production after backend is ready" \
  priority="p1" \
  dependencies='["job_abc123", "job_def456"]'

# Check job queue summary across all sessions
ccmaster jobs  # CLI command to see all pending/active jobs

# List pending jobs in your queue
/mcp__ccmaster__job action="list" status_filter='["pending"]' priority_filter='["p0", "p1"]'
# Output:
# Jobs in queue (3 pending):
# - [p0] Fix Critical Auth Bug (created by: architect)
# - [p1] Optimize Database Queries (created by: lead_dev)
# - [p1] Update API Documentation (created by: frontend_dev)

# Check job status with dependencies
/mcp__ccmaster__job action="get_status" job_id="job_xyz789"
# Shows job details, status, dependencies, and progress

# Cancel a job
/mcp__ccmaster__job action="cancel" job_id="job_xyz789" reason="Requirements changed"

# Complete a job after finishing work
/mcp__ccmaster__job action="complete" \
  job_id="job_abc123" \
  result="Fixed auth bug - issue was expired SSL certificate" \
  artifacts='["/logs/auth-fix.log", "/src/auth/middleware.js"]'
```

**Job Queue Workflow (Fully Automated):**
```bash
# 1. Manager assigns prioritized tasks
/mcp__ccmaster__job action="send_to_member" member="frontend_dev" title="Dashboard Redesign" description="..." priority="p1"
# Output:
# 📋 Job 'Dashboard Redesign' (p1) → frontend_dev's queue
# ⏳ frontend_dev is working - job queued for when idle

/mcp__ccmaster__job action="send_to_member" member="backend_dev" title="API Rate Limiting" description="..." priority="p0"
# Output:
# 📋 Job 'API Rate Limiting' (p0) → backend_dev's queue
# 💡 backend_dev is idle - job will start automatically

# 2. Sessions automatically start jobs when idle (no manual intervention!)
[backend_dev][10:30:45] ● Idle
[backend_dev][10:30:45] 🔨 Starting job: API Rate Limiting (p0)
[backend_dev][10:30:45] 📋 Job ID: job_abc123 | Created by: architect
[backend_dev][10:30:46] ● Processing

# Claude receives clear instructions:
# [AUTOMATED JOB EXECUTION]
# Job: API Rate Limiting
# Priority: p0
# Job ID: job_abc123
#
# Description:
# Implement rate limiting for all API endpoints...
#
# Please complete this job and when finished, use:
# /mcp__ccmaster__job action="complete" job_id="job_abc123" result="<summary>"

# 3. Higher priority jobs execute first
# p0 (critical) → p1 (normal) → p2 (low)

# 4. Monitor job queues with keyboard shortcut
# Press [j] during session monitoring to see all job queues
# Or use: ccmaster jobs

# 5. Dependencies ensure proper order
/mcp__ccmaster__job action="send_to_member" \
  member="devops" \
  title="Deploy to Production" \
  description="Deploy after all tests pass" \
  priority="p0" \
  dependencies='["job_test1", "job_test2", "job_test3"]'
```

**Job System Features:**
- **Fully Automated**: CCMaster monitors idle sessions and starts jobs automatically
- **Priority-based execution**: p0 (critical), p1 (normal), p2 (low)
- **Smart Monitoring**: Checks for jobs when sessions become idle and every 20 seconds
- **Clear Instructions**: Each job includes completion instructions for Claude
- **Status Notifications**: Real-time updates when jobs are assigned, started, and completed
- **Dependency management**: Jobs wait for dependencies to complete
- **Status tracking**: pending → doing → done/cancelled
- **Non-interrupting**: Jobs queue up without disrupting current work
- **Result tracking**: Complete jobs with results and artifacts
- **Queue Visibility**: Press [j] anytime or use `ccmaster jobs` to see all queues

**Requirements for Automatic Job Execution:**
1. **Active CCMaster Monitoring**: You must have `ccmaster watch` running
2. **Session Created by CCMaster**: Jobs only execute in sessions launched by CCMaster
3. **Session Must Be Idle**: Jobs start when Claude finishes current work
4. **MCP Tools Available**: Session must have access to CCMaster MCP tools

**Communication Methods Comparison:**
```bash
# Job: Queued, prioritized, auto-executes when idle
/mcp__ccmaster__job action="send_to_member" member="developer" title="Refactor auth module" priority="p1"

# Mail: Async notification, manual action required
/mcp__ccmaster__communicate action="send_mail" subject="Code review request" body="Please review PR #123"

# Broadcast: Immediate to all idle sessions
/mcp__ccmaster__communicate action="broadcast" message="Emergency meeting in 5 minutes"

# Message: Direct, single recipient, waits for idle
/mcp__ccmaster__communicate action="send_to_member" member="designer" message="Update mockups"
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