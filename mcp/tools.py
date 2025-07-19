"""
MCP Tools for CCMaster Session Management

Provides tools for managing Claude Code sessions, inter-session communication,
and multi-agent coordination.
"""

import json
import os
import subprocess
import sys
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class SessionTools:
    """Tools for managing Claude Code sessions"""
    
    def __init__(self, ccmaster_instance):
        self.ccmaster = ccmaster_instance
        # Team management: identity -> session_id mapping
        self.team_members = {}  # e.g., {"designer": "mcp_20250119_143022", "developer_1": "mcp_20250119_143025"}
        self.session_identities = {}  # Reverse mapping: session_id -> identity
        
        # Initialize team members from stored session data
        self._initialize_team_members()
        
        # Mail system initialization
        self.mailbox_dir = Path(os.path.expanduser("~/.ccmaster/mailbox"))
        self.mailbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Job queue system initialization
        self.job_queue_dir = Path(os.path.expanduser("~/.ccmaster/job_queue"))
        self.job_queue_dir.mkdir(parents=True, exist_ok=True)
        
        self.tools = {
            # Consolidated tools
            "session": self.session,
            "communicate": self.communicate,
            "job": self.job,
            "team": self.team,
            # Keep these unique tools
            "prompt": self.prompt,
            "list_sessions": self.list_sessions,
            "kill_self": self.kill_self
        }
    
    def session(self, action: str, **kwargs) -> Dict[str, Any]:
        """Consolidated session management tool"""
        if action == "get_status":
            return self.get_session_status(**kwargs)
        elif action == "create":
            return self.create_session(**kwargs)
        elif action == "kill":
            return self.kill_session(**kwargs)
        elif action == "watch":
            return self.watch_session(**kwargs)
        elif action == "unwatch":
            return self.unwatch_session(**kwargs)
        elif action == "interrupt":
            return self.interrupt_session(**kwargs)
        elif action == "continue":
            return self.continue_session(**kwargs)
        elif action == "spawn_temp":
            return self.spawn_temp_session(**kwargs)
        elif action == "coordinate":
            return self.coordinate_sessions(**kwargs)
        elif action == "get_logs":
            return self.get_session_logs(**kwargs)
        else:
            return {"error": f"Unknown session action: {action}"}
    
    def communicate(self, action: str, **kwargs) -> Dict[str, Any]:
        """Consolidated communication tool"""
        if action == "send_message":
            return self.send_message_to_session(**kwargs)
        elif action == "send_to_member":
            return self.send_message_to_member(**kwargs)
        elif action == "broadcast":
            return self.broadcast(**kwargs)
        elif action == "send_mail":
            return self.send_mail(**kwargs)
        elif action == "check_mail":
            return self.check_mail(**kwargs)
        elif action == "reply_mail":
            return self.reply_mail(**kwargs)
        elif action == "list_mail":
            return self.list_mail(**kwargs)
        else:
            return {"error": f"Unknown communicate action: {action}"}
    
    def job(self, action: str, **kwargs) -> Dict[str, Any]:
        """Consolidated job management tool"""
        if action == "send_to_session":
            return self.send_job_to_session(**kwargs)
        elif action == "send_to_member":
            return self.send_job_to_member(**kwargs)
        elif action == "list":
            return self.list_jobs(**kwargs)
        elif action == "cancel":
            return self.cancel_job(**kwargs)
        elif action == "get_status":
            return self.job_status(**kwargs)
        elif action == "complete":
            return self.complete_job(**kwargs)
        else:
            return {"error": f"Unknown job action: {action}"}
    
    def team(self, action: str, **kwargs) -> Dict[str, Any]:
        """Consolidated team management tool"""
        if action == "set_identity":
            return self.set_identity_to_session(**kwargs)
        elif action == "list_members":
            return self.list_team_members(**kwargs)
        else:
            return {"error": f"Unknown team action: {action}"}
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for MCP registration"""
        return [
            {
                "name": "session",
                "description": "Manage Claude Code sessions - create, control, monitor",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "kill", "get_status", "get_logs", "watch", "unwatch", "interrupt", "continue", "spawn_temp", "coordinate"],
                            "description": "Action to perform on session"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Target session ID (required for most actions)"
                        },
                        "command": {
                            "type": "string",
                            "description": "Command for spawn_temp action"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout for spawn_temp action",
                            "default": 60
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Task description for coordinate action"
                        },
                        "session_assignments": {
                            "type": "object",
                            "description": "Session assignments for coordinate action"
                        },
                        "working_dir": {
                            "type": "string",
                            "description": "Working directory for create action"
                        },
                        "watch_mode": {
                            "type": "boolean",
                            "description": "Enable watch mode for create action",
                            "default": True
                        },
                        "max_turns": {
                            "type": "integer",
                            "description": "Max auto-continue turns for watch action"
                        },
                        "message": {
                            "type": "string",
                            "description": "Message for continue action"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for interrupt/kill actions"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of log lines to retrieve",
                            "default": 100
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "communicate",
                "description": "Send messages via different methods - direct, broadcast, or mail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["send_message", "send_to_member", "broadcast", "send_mail", "check_mail", "reply_mail", "list_mail"],
                            "description": "Communication action to perform"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Target session ID for send_message"
                        },
                        "member": {
                            "type": "string",
                            "description": "Target member identity for send_to_member"
                        },
                        "to_sessions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Target session IDs for mail"
                        },
                        "to_members": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Target member identities for mail"
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content for message/broadcast methods"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Mail subject (mail method only)"
                        },
                        "body": {
                            "type": "string",
                            "description": "Mail body (mail method only)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high", "urgent"],
                            "description": "Mail priority",
                            "default": "normal"
                        },
                        "whitelist_sessions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Whitelist for broadcast"
                        },
                        "blacklist_sessions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Blacklist for broadcast"
                        },
                        "whitelist_members": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Whitelist members for broadcast"
                        },
                        "blacklist_members": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Blacklist members for broadcast"
                        },
                        "exclude_self": {
                            "type": "boolean",
                            "description": "Exclude sender from broadcast",
                            "default": True
                        },
                        "wait_for_response": {
                            "type": "boolean",
                            "description": "Wait for response (message method)",
                            "default": False
                        },
                        "mail_id": {
                            "type": "string",
                            "description": "Mail ID for reply"
                        },
                        "unread_only": {
                            "type": "boolean",
                            "description": "Filter unread mail only",
                            "default": True
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Limit number of results for check_mail/list_mail",
                            "default": 10
                        },
                        "folder": {
                            "type": "string",
                            "description": "Mail folder for list_mail",
                            "default": "inbox"
                        },
                        "reply_all": {
                            "type": "boolean",
                            "description": "Reply to all recipients",
                            "default": False
                        },
                        "sender_filter": {
                            "type": "string",
                            "description": "Filter by sender for list_mail"
                        },
                        "priority_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by priority for list_mail"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "job",
                "description": "Manage job queue - send, list, cancel, complete jobs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["send_to_session", "send_to_member", "list", "cancel", "get_status", "complete"],
                            "description": "Job action to perform"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Target session ID"
                        },
                        "member": {
                            "type": "string",
                            "description": "Target member identity"
                        },
                        "title": {
                            "type": "string",
                            "description": "Job title (send action)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Job description (send action)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["p0", "p1", "p2"],
                            "description": "Job priority",
                            "default": "p1"
                        },
                        "job_id": {
                            "type": "string",
                            "description": "Job ID for status/cancel/complete"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for cancellation"
                        },
                        "result": {
                            "type": "string",
                            "description": "Job completion result"
                        },
                        "artifacts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Artifacts produced"
                        },
                        "dependencies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Job dependencies"
                        },
                        "status_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by status"
                        },
                        "priority_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by priority for list action"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "team",
                "description": "Manage team identities and members",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["set_identity", "list_members"],
                            "description": "Team management action"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session to assign identity"
                        },
                        "identity": {
                            "type": "string",
                            "description": "Human-readable identity/role"
                        },
                        "include_inactive": {
                            "type": "boolean",
                            "description": "Include inactive members",
                            "default": False
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "list_sessions",
                "description": "List all active Claude Code sessions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_ended": {
                            "type": "boolean",
                            "description": "Include ended sessions in the list",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "prompt",
                "description": "Send a prompt/message to CCMaster console",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The prompt message to display"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "kill_self",
                "description": "Terminate the current session (self-termination)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Reason for self-termination"
                        },
                        "final_message": {
                            "type": "string",
                            "description": "Final message to log before termination"
                        }
                    },
                    "required": ["reason"]
                }
            }
        ]
    
    def _initialize_team_members(self):
        """Initialize team members from stored session identities"""
        try:
            for session_id, session_data in self.ccmaster.sessions.items():
                if 'identity' in session_data:
                    identity = session_data['identity']
                    self.team_members[identity] = session_id
                    self.session_identities[session_id] = identity
        except Exception as e:
            # Log error but don't fail initialization
            if hasattr(self.ccmaster, 'cli_log'):
                self.ccmaster.cli_log(f"Warning: Could not restore team identities: {e}", log_type='warning')
    
    def list_sessions(self, include_ended: bool = False) -> Dict[str, Any]:
        """List all active sessions"""
        sessions = []
        for session_id, session_data in self.ccmaster.sessions.items():
            if not include_ended and session_data.get('status') == 'ended':
                continue
            
            session_info = {
                "session_id": session_id,
                "identity": self.session_identities.get(session_id),
                "working_dir": session_data.get('working_dir'),
                "status": session_data.get('status', 'unknown'),
                "created_at": session_data.get('created_at'),
                "ended_at": session_data.get('ended_at'),
                "is_active": session_id in self.ccmaster.active_sessions
            }
            sessions.append(session_info)
        
        return {
            "sessions": sessions,
            "total_count": len(sessions),
            "active_count": len(self.ccmaster.active_sessions)
        }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status of a session"""
        if session_id not in self.ccmaster.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session_data = self.ccmaster.sessions[session_id]
        current_status = self.ccmaster.current_status.get(session_id, 'unknown')
        
        return {
            "session_id": session_id,
            "status": session_data.get('status', 'unknown'),
            "current_state": current_status,
            "working_dir": session_data.get('working_dir'),
            "created_at": session_data.get('created_at'),
            "ended_at": session_data.get('ended_at'),
            "is_active": session_id in self.ccmaster.active_sessions,
            "watch_mode": self.ccmaster.watch_modes.get(session_id, False),
            "auto_continue_count": self.ccmaster.auto_continue_counts.get(session_id, 0),
            "max_turns": self.ccmaster.max_turns.get(session_id)
        }
    
    def send_message_to_session(self, session_id: str, message: str, wait_for_response: bool = False) -> Dict[str, Any]:
        """Send a message to a specific session"""
        if session_id not in self.ccmaster.active_sessions:
            return {"error": f"Session {session_id} is not active"}
        
        try:
            # Send message through CCMaster's existing mechanism
            success = self.ccmaster.send_continue_to_claude(session_id, message)
            
            result = {
                "success": success,
                "session_id": session_id,
                "message_sent": message,
                "timestamp": datetime.now().isoformat()
            }
            
            if wait_for_response:
                # Wait for session to process the message
                time.sleep(2)  # Simple wait - could be improved with actual response monitoring
                result["session_status"] = self.ccmaster.current_status.get(session_id, 'unknown')
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to send message: {str(e)}"}
    
    def create_session(self, working_dir: str = None, watch_mode: bool = True, max_turns: int = None) -> Dict[str, Any]:
        """Create a new Claude Code session"""
        try:
            if working_dir is None:
                working_dir = os.getcwd()
            else:
                working_dir = os.path.abspath(working_dir)
                # Create directory if it doesn't exist
                os.makedirs(working_dir, exist_ok=True)
            
            # Generate a unique session ID for MCP-created sessions
            # Add "mcp_" prefix to distinguish from regular sessions
            session_id = "mcp_" + datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:21]
            
            # Create session data structure
            session_data = {
                'id': session_id,
                'started_at': datetime.now().isoformat(),
                'working_dir': working_dir,
                'status': 'starting',
                'pid': None,
                'last_activity': datetime.now().isoformat(),
                'created_by': 'mcp',
                'watch_mode': watch_mode,
                'max_turns': max_turns
            }
            
            # Register the session with CCMaster
            self.ccmaster.sessions[session_id] = session_data
            self.ccmaster.save_sessions()
            
            # Add to active sessions with proper tracking info
            self.ccmaster.active_sessions[session_id] = {
                'index': len(self.ccmaster.active_sessions) + 1,
                'working_dir': working_dir,
                'created_at': datetime.now().isoformat()
            }
            
            # Set watch mode and max turns
            self.ccmaster.watch_modes[session_id] = watch_mode
            if max_turns:
                self.ccmaster.max_turns[session_id] = max_turns
            
            # Initialize monitoring structures
            self.ccmaster.current_status[session_id] = 'starting'
            self.ccmaster.auto_continue_counts[session_id] = 0
            self.ccmaster.has_seen_first_prompt[session_id] = False
            
            # Log the session creation
            watch_info = f" (watch: {'ON' if watch_mode else 'OFF'}"
            if max_turns:
                watch_info += f", max: {max_turns}"
            watch_info += ")"
            self.ccmaster.cli_log(f"Creating {session_id}{watch_info}", log_type='info', color='PURPLE')
            
            # Start the actual Claude session in a separate thread
            import threading
            
            def launch_and_monitor():
                """Launch Claude and start monitoring"""
                try:
                    # Create MCP config for the new session
                    if self.ccmaster.mcp_enabled and self.ccmaster.mcp_server:
                        self.ccmaster.create_project_mcp_config(working_dir)
                        self.ccmaster.create_claude_settings(working_dir)
                    
                    # Create hooks config
                    settings_file, backup_file = self.ccmaster.create_hooks_config(session_id)
                    
                    # Launch Claude Code
                    claude_cmd = self.ccmaster.config['claude_code_command'] + ' --dangerously-skip-permissions'
                    
                    # Launch from the working directory to ensure .mcp.json is found
                    env = os.environ.copy()
                    env['CLAUDE_CODE_USER_SETTINGS_FILE'] = settings_file
                    env['CCMASTER_SESSION_ID'] = session_id
                    
                    # Launch Claude Code (remove verbose directory message)
                    
                    # Try iTerm first, then fall back to Terminal
                    # Check if iTerm is available
                    check_iterm = subprocess.run(['pgrep', '-x', 'iTerm2'], capture_output=True)
                    use_iterm = check_iterm.returncode == 0
                    
                    if use_iterm:
                        script = f'''
                        tell application "iTerm"
                            set newWindow to (create window with default profile)
                            tell current session of newWindow
                                write text "cd {working_dir} && {claude_cmd}"
                            end tell
                            return id of newWindow & ", " & 1
                        end tell
                        '''
                    else:
                        # Use Terminal.app - match the working pattern from main ccmaster
                        script = f'''
                        tell application "Terminal"
                            activate
                            set newTab to do script "cd '{working_dir}' && {claude_cmd}"
                            set windowId to id of window 1
                            set tabIndex to 1
                            repeat with t in tabs of window 1
                                if t is newTab then
                                    exit repeat
                                end if
                                set tabIndex to tabIndex + 1
                            end repeat
                            return "" & windowId & "," & tabIndex
                        end tell
                        '''
                    
                    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Parse window info
                        window_info = result.stdout.strip()
                        if window_info:
                            # Handle both comma-space and comma formats
                            if ', ' in window_info:
                                parts = window_info.split(', ')
                            else:
                                parts = window_info.split(',')
                            
                            if len(parts) >= 2:
                                window_id = parts[0].strip()
                                tab_id = parts[1].strip()
                                # Store terminal window info for auto-continue
                                self.ccmaster.sessions[session_id]['terminal_window_id'] = int(window_id)
                                self.ccmaster.sessions[session_id]['terminal_tab_index'] = int(tab_id)
                                self.ccmaster.cli_log(f"Launched Claude (W{window_id}/T{tab_id})", log_type='launch')
                            else:
                                self.ccmaster.cli_log(f"Invalid window info: '{window_info}'", log_type='warning')
                        else:
                            self.ccmaster.cli_log("No window info from AppleScript", log_type='warning')
                    else:
                        self.ccmaster.cli_log(f"AppleScript failed (return code {result.returncode}): {result.stderr.strip()}", log_type='error')
                    
                    # Update session status
                    self.ccmaster.sessions[session_id]['status'] = 'active'
                    self.ccmaster.current_status[session_id] = 'idle'
                    # Save sessions with terminal window info
                    self.ccmaster.save_sessions()
                    
                    # Create status file for the session
                    status_file = Path(self.ccmaster.status_dir) / f"{session_id}.json"
                    with open(status_file, 'w') as f:
                        json.dump({'state': 'idle', 'session_id': session_id}, f)
                    
                    # Log session start event
                    self.ccmaster.log_event(session_id, 'SESSION_START', f'MCP session started in {working_dir}', display=False)
                    
                    # Set up monitoring threads - use simple_monitor_session for multi-session compatibility
                    import time
                    launch_time = time.time()
                    monitor_thread = threading.Thread(
                        target=self.ccmaster.simple_monitor_session,
                        args=(session_id, launch_time),
                        name=f"Monitor-{session_id}",
                        daemon=True
                    )
                    monitor_thread.start()
                    self.ccmaster.session_threads[session_id] = {'monitor': monitor_thread}
                    
                    status_thread = threading.Thread(
                        target=self.ccmaster.monitor_status,
                        args=(session_id,),
                        name=f"Status-{session_id}",
                        daemon=True
                    )
                    status_thread.start()
                    self.ccmaster.session_threads[session_id]['status'] = status_thread
                    
                except Exception as e:
                    self.ccmaster.cli_log(f"Error launching MCP session: {e}", log_type='error')
                    self.ccmaster.sessions[session_id]['status'] = 'error'
                    self.ccmaster.sessions[session_id]['error'] = str(e)
                    self.ccmaster.save_sessions()
            
            # Start the launch thread
            launch_thread = threading.Thread(
                target=launch_and_monitor,
                daemon=True,
                name=f"MCP_Launch_{session_id}"
            )
            launch_thread.start()
            
            # Give it a moment to start
            time.sleep(1)
            
            return {
                "success": True,
                "session_id": session_id,
                "working_dir": working_dir,
                "watch_mode": watch_mode,
                "max_turns": max_turns,
                "created_at": datetime.now().isoformat(),
                "message": f"MCP session {session_id} created and being monitored"
            }
            
        except Exception as e:
            return {"error": f"Failed to create session: {str(e)}"}
    
    def kill_session(self, session_id: str) -> Dict[str, Any]:
        """Kill a specific session"""
        try:
            if session_id not in self.ccmaster.active_sessions:
                return {"error": f"Session {session_id} is not active"}
            
            # Find and kill the Claude process
            claude_pid = self.ccmaster.find_claude_pid_for_session(session_id, 
                                                                   self.ccmaster.sessions[session_id]['created_at'])
            
            if claude_pid:
                subprocess.run(['kill', str(claude_pid)], check=True)
            
            # Clean up session data
            if session_id in self.ccmaster.active_sessions:
                del self.ccmaster.active_sessions[session_id]
            
            if session_id in self.ccmaster.watch_modes:
                del self.ccmaster.watch_modes[session_id]
            
            if session_id in self.ccmaster.current_status:
                del self.ccmaster.current_status[session_id]
            
            # Update session status
            self.ccmaster.sessions[session_id]['status'] = 'killed'
            self.ccmaster.sessions[session_id]['ended_at'] = datetime.now().isoformat()
            self.ccmaster.save_sessions()
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session killed successfully"
            }
            
        except Exception as e:
            return {"error": f"Failed to kill session: {str(e)}"}
    
    def spawn_temp_session(self, command: str, working_dir: str = None, timeout: int = 60) -> Dict[str, Any]:
        """Spawn a temporary session, run a command, and kill it"""
        try:
            # Create temporary session
            session_result = self.create_session(working_dir, watch_mode=False, max_turns=1)
            
            if not session_result.get('success'):
                return session_result
            
            session_id = session_result['session_id']
            
            # Wait for session to start
            time.sleep(3)
            
            # Send command
            message_result = self.send_message_to_session(session_id, command, wait_for_response=True)
            
            if not message_result.get('success'):
                self.kill_session(session_id)
                return message_result
            
            # Wait for execution or timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                status = self.get_session_status(session_id)
                if status.get('current_state') == 'idle':
                    break
                time.sleep(1)
            
            # Get logs before killing
            logs = self.get_session_logs(session_id, lines=50)
            
            # Kill the temporary session
            kill_result = self.kill_session(session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "command": command,
                "execution_time": time.time() - start_time,
                "logs": logs,
                "kill_result": kill_result
            }
            
        except Exception as e:
            return {"error": f"Failed to spawn temp session: {str(e)}"}
    
    def coordinate_sessions(self, task_description: str, session_assignments: Dict[str, str]) -> Dict[str, Any]:
        """Coordinate multiple sessions for a complex task"""
        try:
            results = {}
            
            for session_id, subtask in session_assignments.items():
                if session_id not in self.ccmaster.active_sessions:
                    results[session_id] = {"error": f"Session {session_id} not active"}
                    continue
                
                # Create coordination message
                coordination_msg = f"""
Task Coordination Request:
- Overall Task: {task_description}
- Your Subtask: {subtask}
- Session ID: {session_id}

Please acknowledge and begin working on your assigned subtask.
"""
                
                # Send coordination message
                result = self.send_message_to_session(session_id, coordination_msg)
                results[session_id] = result
            
            return {
                "success": True,
                "task_description": task_description,
                "coordination_results": results,
                "coordinated_sessions": list(session_assignments.keys())
            }
            
        except Exception as e:
            return {"error": f"Failed to coordinate sessions: {str(e)}"}
    
    def get_session_logs(self, session_id: str, lines: int = 100) -> Dict[str, Any]:
        """Get logs from a specific session"""
        try:
            log_file = self.ccmaster.logs_dir / f'{session_id}.log'
            
            if not log_file.exists():
                return {"error": f"Log file for session {session_id} not found"}
            
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            return {
                "success": True,
                "session_id": session_id,
                "log_lines": recent_lines,
                "total_lines": len(all_lines),
                "requested_lines": lines
            }
            
        except Exception as e:
            return {"error": f"Failed to get logs: {str(e)}"}
    
    def prompt(self, message: str) -> Dict[str, Any]:
        """Demo tool: Display a prompt message in CCMaster console"""
        try:
            # Process message to handle newlines properly
            # Split multiline messages and print each line with proper alignment
            lines = message.strip().split('\n')
            
            # Use CCMaster's standardized cli_log if available
            if hasattr(self.ccmaster, 'cli_log'):
                # Print first line with newline before
                self.ccmaster.cli_log(lines[0], log_type='mcp', newline_before=True)
                # Print remaining lines with proper indentation
                for line in lines[1:]:
                    # Clean up extra whitespace but preserve intended formatting
                    cleaned_line = line.strip()
                    if cleaned_line:  # Only print non-empty lines
                        self.ccmaster.cli_log(cleaned_line, log_type='mcp')
            else:
                # Fallback to direct printing if cli_log not available
                timestamp = datetime.now().strftime("%H:%M:%S")
                print()  # Newline before
                for line in lines:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        print(f"[{timestamp}] [MCP] {cleaned_line}")
                sys.stdout.flush()
            
            return {
                "success": True,
                "message": "Prompt displayed in CCMaster console",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "prompt_text": message
            }
            
        except Exception as e:
            return {"error": f"Failed to display prompt: {str(e)}"}
    
    def watch_session(self, session_id: str, max_turns: int = None) -> Dict[str, Any]:
        """Enable watch mode for a specific session"""
        try:
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            if session_id not in self.ccmaster.active_sessions:
                return {"error": f"Session {session_id} is not active"}
            
            # Enable watch mode
            self.ccmaster.watch_modes[session_id] = True
            
            # Set max turns if provided
            if max_turns is not None:
                self.ccmaster.max_turns[session_id] = max_turns
                # Reset auto-continue count
                self.ccmaster.auto_continue_counts[session_id] = 0
            
            # Log the action
            watch_info = f"Watch mode enabled for {session_id}"
            if max_turns:
                watch_info += f" (max: {max_turns} turns)"
            
            self.ccmaster.cli_log(watch_info, log_type='info', color='GREEN')
            
            # Check if session is currently idle and trigger auto-continue if needed
            current_status = self.ccmaster.current_status.get(session_id, 'unknown')
            if current_status == 'idle' and self.ccmaster.has_seen_first_prompt.get(session_id, False):
                # Mark as pending to prevent duplicate auto-continues
                if session_id not in self.ccmaster.pending_continues:
                    self.ccmaster.pending_continues[session_id] = True
                    # Send auto-continue
                    self.ccmaster.send_continue_to_claude(session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "watch_mode": True,
                "max_turns": max_turns,
                "message": watch_info
            }
            
        except Exception as e:
            return {"error": f"Failed to enable watch mode: {str(e)}"}
    
    def unwatch_session(self, session_id: str) -> Dict[str, Any]:
        """Disable watch mode for a specific session"""
        try:
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            if session_id not in self.ccmaster.active_sessions:
                return {"error": f"Session {session_id} is not active"}
            
            # Disable watch mode
            self.ccmaster.watch_modes[session_id] = False
            
            # Clear max turns
            if session_id in self.ccmaster.max_turns:
                del self.ccmaster.max_turns[session_id]
            
            # Clear pending continues if any
            if session_id in self.ccmaster.pending_continues:
                del self.ccmaster.pending_continues[session_id]
            
            # Log the action
            self.ccmaster.cli_log(f"Watch mode disabled for {session_id}", log_type='info', color='YELLOW')
            
            return {
                "success": True,
                "session_id": session_id,
                "watch_mode": False,
                "message": f"Watch mode disabled for {session_id}"
            }
            
        except Exception as e:
            return {"error": f"Failed to disable watch mode: {str(e)}"}
    
    def interrupt_session(self, session_id: str, reason: str = None) -> Dict[str, Any]:
        """Interrupt a session that is currently processing"""
        try:
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            if session_id not in self.ccmaster.active_sessions:
                return {"error": f"Session {session_id} is not active"}
            
            current_status = self.ccmaster.current_status.get(session_id, 'unknown')
            
            # Can only interrupt sessions that are processing or working
            if current_status not in ['processing', 'working']:
                return {
                    "error": f"Session {session_id} is in '{current_status}' state, cannot interrupt",
                    "hint": "Session must be in 'processing' or 'working' state to interrupt"
                }
            
            # Send interrupt signal (Ctrl+C) to the Claude session
            try:
                # Find the Claude process for this session
                session_data = self.ccmaster.sessions[session_id]
                created_at = session_data.get('created_at', session_data.get('started_at'))
                claude_pid = self.ccmaster.find_claude_pid_for_session(session_id, created_at)
                
                if claude_pid:
                    # Send SIGINT (Ctrl+C) to interrupt
                    subprocess.run(['kill', '-INT', str(claude_pid)], check=True)
                    
                    # Log the interruption
                    interrupt_msg = f"Interrupted session {session_id}"
                    if reason:
                        interrupt_msg += f" - Reason: {reason}"
                    self.ccmaster.cli_log(interrupt_msg, log_type='warning', color='YELLOW')
                    
                    # Clear any pending continues for this session
                    if session_id in self.ccmaster.pending_continues:
                        del self.ccmaster.pending_continues[session_id]
                    
                    # Update status to idle after a brief delay
                    import time
                    time.sleep(0.5)
                    self.ccmaster.current_status[session_id] = 'idle'
                    
                    return {
                        "success": True,
                        "session_id": session_id,
                        "previous_status": current_status,
                        "new_status": "idle",
                        "reason": reason,
                        "message": interrupt_msg
                    }
                else:
                    return {"error": f"Could not find Claude process for session {session_id}"}
                    
            except subprocess.CalledProcessError as e:
                return {"error": f"Failed to send interrupt signal: {str(e)}"}
            
        except Exception as e:
            return {"error": f"Failed to interrupt session: {str(e)}"}
    
    def continue_session(self, session_id: str, message: str = None) -> Dict[str, Any]:
        """Send a continue command to a session"""
        try:
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            if session_id not in self.ccmaster.active_sessions:
                return {"error": f"Session {session_id} is not active"}
            
            current_status = self.ccmaster.current_status.get(session_id, 'unknown')
            
            # Can only continue sessions that are idle
            if current_status != 'idle':
                return {
                    "error": f"Session {session_id} is in '{current_status}' state, cannot continue",
                    "hint": "Session must be in 'idle' state to continue"
                }
            
            # Use provided message or default to "continue"
            continue_message = message if message else "continue"
            
            # Check if we already have a pending continue for this session
            if session_id in self.ccmaster.pending_continues:
                return {
                    "warning": f"Session {session_id} already has a pending continue",
                    "session_id": session_id,
                    "status": current_status
                }
            
            # Mark as pending before sending
            self.ccmaster.pending_continues[session_id] = True
            
            # Send the continue command
            success = self.ccmaster.send_continue_to_claude(session_id, continue_message)
            
            if success:
                # Log the action
                self.ccmaster.cli_log(f"Sent continue to {session_id}: {continue_message}", log_type='info', color='GREEN')
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "message_sent": continue_message,
                    "timestamp": datetime.now().isoformat(),
                    "previous_status": current_status,
                    "message": f"Continue command sent to session {session_id}"
                }
            else:
                # Clear pending state on failure
                if session_id in self.ccmaster.pending_continues:
                    del self.ccmaster.pending_continues[session_id]
                
                return {
                    "error": f"Failed to send continue command to session {session_id}",
                    "session_id": session_id
                }
            
        except Exception as e:
            # Clear pending state on exception
            if session_id in self.ccmaster.pending_continues:
                del self.ccmaster.pending_continues[session_id]
            return {"error": f"Failed to continue session: {str(e)}"}
    
    def kill_self(self, reason: str, final_message: str = None) -> Dict[str, Any]:
        """Allow a session to terminate itself"""
        try:
            # Try to get session ID from environment variable first
            session_id = os.environ.get('CCMASTER_SESSION_ID')
            
            if not session_id:
                # If no env var, look for MCP-created sessions that might be calling this
                # This is a limitation - ideally we'd have session context from MCP connection
                return {
                    "error": "Cannot determine session ID for self-termination",
                    "hint": "Set CCMASTER_SESSION_ID environment variable or use kill_session with explicit ID"
                }
            
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            if session_id not in self.ccmaster.active_sessions:
                return {"error": f"Session {session_id} is not active"}
            
            # Log the self-termination request
            termination_msg = f"Session {session_id} requesting self-termination - Reason: {reason}"
            if final_message:
                self.ccmaster.cli_log(f"Final message from {session_id}: {final_message}", log_type='info', color='CYAN')
            self.ccmaster.cli_log(termination_msg, log_type='warning', color='YELLOW')
            
            # Log the event
            self.ccmaster.log_event(session_id, 'SELF_TERMINATION', f'Reason: {reason}', display=False)
            
            # Find and kill the Claude process
            session_data = self.ccmaster.sessions[session_id]
            created_at = session_data.get('created_at', session_data.get('started_at'))
            claude_pid = self.ccmaster.find_claude_pid_for_session(session_id, created_at)
            
            if claude_pid:
                # Kill the process
                subprocess.run(['kill', str(claude_pid)], check=True)
                
                # Clean up session data
                if session_id in self.ccmaster.active_sessions:
                    del self.ccmaster.active_sessions[session_id]
                
                if session_id in self.ccmaster.watch_modes:
                    del self.ccmaster.watch_modes[session_id]
                
                if session_id in self.ccmaster.current_status:
                    del self.ccmaster.current_status[session_id]
                
                if session_id in self.ccmaster.pending_continues:
                    del self.ccmaster.pending_continues[session_id]
                
                # Update session status
                self.ccmaster.sessions[session_id]['status'] = 'self_terminated'
                self.ccmaster.sessions[session_id]['ended_at'] = datetime.now().isoformat()
                self.ccmaster.sessions[session_id]['termination_reason'] = reason
                self.ccmaster.save_sessions()
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "reason": reason,
                    "final_message": final_message,
                    "message": f"Session {session_id} successfully self-terminated"
                }
            else:
                return {"error": f"Could not find Claude process for session {session_id}"}
                
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to terminate process: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to self-terminate: {str(e)}"}
    
    def set_identity_to_session(self, session_id: str, identity: str) -> Dict[str, Any]:
        """Assign a human-readable identity to a session"""
        try:
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            # Check if identity is already taken by another active session
            if identity in self.team_members:
                existing_session = self.team_members[identity]
                if existing_session != session_id and existing_session in self.ccmaster.active_sessions:
                    return {
                        "error": f"Identity '{identity}' is already assigned to active session {existing_session}",
                        "hint": "Choose a different identity or remove the existing assignment"
                    }
            
            # Remove any previous identity for this session
            if session_id in self.session_identities:
                old_identity = self.session_identities[session_id]
                if old_identity in self.team_members:
                    del self.team_members[old_identity]
            
            # Assign new identity
            self.team_members[identity] = session_id
            self.session_identities[session_id] = identity
            
            # Also update CCMaster's session_identities
            self.ccmaster.session_identities[session_id] = identity
            
            # Store identity in session data for persistence
            self.ccmaster.sessions[session_id]['identity'] = identity
            self.ccmaster.save_sessions()
            
            # Log the assignment
            self.ccmaster.cli_log(f"Assigned identity '{identity}' to session {session_id}", log_type='info', color='CYAN')
            
            return {
                "success": True,
                "session_id": session_id,
                "identity": identity,
                "message": f"Session {session_id} is now known as '{identity}'"
            }
            
        except Exception as e:
            return {"error": f"Failed to set identity: {str(e)}"}
    
    def send_message_to_member(self, member: str, message: str, wait_for_response: bool = False) -> Dict[str, Any]:
        """Send a message to a team member by their identity"""
        try:
            # Look up session ID by member identity
            if member not in self.team_members:
                return {
                    "error": f"Team member '{member}' not found",
                    "hint": "Use list_team_members to see available members",
                    "available_members": list(self.team_members.keys())
                }
            
            session_id = self.team_members[member]
            
            # Check if session is still active
            if session_id not in self.ccmaster.active_sessions:
                return {
                    "error": f"Team member '{member}' (session {session_id}) is not active",
                    "hint": "The session may have ended or been terminated"
                }
            
            # Send the message using existing send_message_to_session
            result = self.send_message_to_session(session_id, message, wait_for_response)
            
            # Enhance the result with member identity
            if isinstance(result, dict):
                result["member"] = member
                if result.get("success"):
                    result["message"] = f"Message sent to {member} ({session_id})"
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to send message to member: {str(e)}"}
    
    def list_team_members(self, include_inactive: bool = False) -> Dict[str, Any]:
        """List all team members with their identities and status"""
        try:
            members = []
            
            for identity, session_id in self.team_members.items():
                if session_id not in self.ccmaster.sessions:
                    continue
                
                session_data = self.ccmaster.sessions[session_id]
                is_active = session_id in self.ccmaster.active_sessions
                
                if not include_inactive and not is_active:
                    continue
                
                member_info = {
                    "identity": identity,
                    "session_id": session_id,
                    "status": session_data.get('status', 'unknown'),
                    "current_state": self.ccmaster.current_status.get(session_id, 'unknown') if is_active else 'inactive',
                    "working_dir": session_data.get('working_dir'),
                    "created_at": session_data.get('created_at'),
                    "is_active": is_active
                }
                
                # Add watch mode info if active
                if is_active:
                    member_info["watch_mode"] = self.ccmaster.watch_modes.get(session_id, False)
                    member_info["auto_continue_count"] = self.ccmaster.auto_continue_counts.get(session_id, 0)
                
                members.append(member_info)
            
            # Sort by identity for readability
            members.sort(key=lambda x: x['identity'])
            
            return {
                "team_members": members,
                "active_count": len([m for m in members if m['is_active']]),
                "total_count": len(members),
                "message": f"Team has {len(members)} members ({len([m for m in members if m['is_active']])} active)"
            }
            
        except Exception as e:
            return {"error": f"Failed to list team members: {str(e)}"}
    
    def broadcast(self, message: str, whitelist_sessions: List[str] = None, whitelist_members: List[str] = None,
                  blacklist_sessions: List[str] = None, blacklist_members: List[str] = None, 
                  exclude_self: bool = True) -> Dict[str, Any]:
        """Broadcast a message to multiple sessions"""
        try:
            # Get broadcasting session ID if available
            broadcasting_session = os.environ.get('CCMASTER_SESSION_ID')
            
            # Determine target sessions
            target_sessions = set()
            
            # Start with all active sessions
            for session_id in self.ccmaster.active_sessions:
                target_sessions.add(session_id)
            
            # Apply whitelist filters
            if whitelist_sessions or whitelist_members:
                filtered_sessions = set()
                
                # Add whitelisted sessions
                if whitelist_sessions:
                    for session_id in whitelist_sessions:
                        if session_id in self.ccmaster.active_sessions:
                            filtered_sessions.add(session_id)
                
                # Add sessions of whitelisted members
                if whitelist_members:
                    for member in whitelist_members:
                        if member in self.team_members:
                            session_id = self.team_members[member]
                            if session_id in self.ccmaster.active_sessions:
                                filtered_sessions.add(session_id)
                
                # Use only whitelisted sessions
                target_sessions = filtered_sessions
            
            # Apply blacklist filters
            if blacklist_sessions:
                for session_id in blacklist_sessions:
                    target_sessions.discard(session_id)
            
            if blacklist_members:
                for member in blacklist_members:
                    if member in self.team_members:
                        session_id = self.team_members[member]
                        target_sessions.discard(session_id)
            
            # Exclude self if requested
            if exclude_self and broadcasting_session:
                target_sessions.discard(broadcasting_session)
            
            # Check if any targets remain
            if not target_sessions:
                return {
                    "warning": "No active sessions match the broadcast criteria",
                    "active_sessions": len(self.ccmaster.active_sessions),
                    "filters_applied": {
                        "whitelist_sessions": whitelist_sessions,
                        "whitelist_members": whitelist_members,
                        "blacklist_sessions": blacklist_sessions,
                        "blacklist_members": blacklist_members,
                        "exclude_self": exclude_self
                    }
                }
            
            # Log the broadcast
            broadcast_info = f"Broadcasting to {len(target_sessions)} sessions"
            if broadcasting_session:
                broadcast_info = f"Session {broadcasting_session} broadcasting to {len(target_sessions)} sessions"
            self.ccmaster.cli_log(broadcast_info, log_type='info', color='PURPLE', newline_before=True)
            
            # Send message to each target session
            results = {}
            success_count = 0
            failed_count = 0
            
            for session_id in target_sessions:
                try:
                    # Get session identity for logging
                    identity = self.session_identities.get(session_id, session_id)
                    
                    # Check session status
                    current_status = self.ccmaster.current_status.get(session_id, 'unknown')
                    
                    # Only send to idle sessions
                    if current_status != 'idle':
                        results[session_id] = {
                            "success": False,
                            "identity": identity,
                            "error": f"Session is {current_status}, not idle"
                        }
                        failed_count += 1
                        continue
                    
                    # Send the message
                    success = self.ccmaster.send_continue_to_claude(session_id, message)
                    
                    results[session_id] = {
                        "success": success,
                        "identity": identity,
                        "status": "message sent" if success else "failed to send"
                    }
                    
                    if success:
                        success_count += 1
                        # Log individual broadcast
                        prefix = self.ccmaster.get_session_prefix(session_id)
                        self.ccmaster.cli_log(f"Broadcast received: {message[:50]}{'...' if len(message) > 50 else ''}", 
                                            log_type='info', prefix=prefix)
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    results[session_id] = {
                        "success": False,
                        "identity": self.session_identities.get(session_id, session_id),
                        "error": str(e)
                    }
                    failed_count += 1
            
            # Summary log
            summary = f"Broadcast complete: {success_count} succeeded, {failed_count} failed"
            self.ccmaster.cli_log(summary, log_type='info', color='GREEN' if failed_count == 0 else 'YELLOW')
            
            return {
                "success": True,
                "message": message[:100] + "..." if len(message) > 100 else message,
                "broadcast_from": broadcasting_session,
                "total_recipients": len(target_sessions),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
                "summary": summary
            }
            
        except Exception as e:
            return {"error": f"Failed to broadcast message: {str(e)}"}
    
    def send_mail(self, subject: str, body: str, to_sessions: List[str] = None, 
                  to_members: List[str] = None, priority: str = "normal") -> Dict[str, Any]:
        """Send mail to sessions/members"""
        try:
            # Get sender info
            sender_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            sender_identity = self.session_identities.get(sender_session, sender_session)
            
            # Determine recipients
            recipients = set()
            recipient_names = []
            
            # Add session recipients
            if to_sessions:
                for session_id in to_sessions:
                    if session_id in self.ccmaster.sessions:
                        recipients.add(session_id)
                        identity = self.session_identities.get(session_id, session_id)
                        recipient_names.append(identity)
            
            # Add member recipients
            if to_members:
                for member in to_members:
                    if member in self.team_members:
                        session_id = self.team_members[member]
                        recipients.add(session_id)
                        recipient_names.append(member)
            
            # Default to all active sessions if no recipients specified
            if not recipients and not to_sessions and not to_members:
                for session_id in self.ccmaster.active_sessions:
                    recipients.add(session_id)
                    identity = self.session_identities.get(session_id, session_id)
                    recipient_names.append(identity)
            
            if not recipients:
                return {"error": "No valid recipients found"}
            
            # Create mail data
            mail_id = str(uuid.uuid4())[:8]
            mail_data = {
                "id": mail_id,
                "from": sender_session,
                "from_identity": sender_identity,
                "to": list(recipients),
                "to_names": recipient_names,
                "subject": subject,
                "body": body,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "read_by": [],
                "replies": []
            }
            
            # Save mail to each recipient's inbox
            saved_count = 0
            for recipient in recipients:
                recipient_inbox = self.mailbox_dir / recipient / "inbox"
                recipient_inbox.mkdir(parents=True, exist_ok=True)
                
                mail_file = recipient_inbox / f"{mail_id}.json"
                with open(mail_file, 'w') as f:
                    json.dump(mail_data, f, indent=2)
                saved_count += 1
            
            # Save to sender's sent folder
            sender_sent = self.mailbox_dir / sender_session / "sent"
            sender_sent.mkdir(parents=True, exist_ok=True)
            
            sent_file = sender_sent / f"{mail_id}.json"
            with open(sent_file, 'w') as f:
                json.dump(mail_data, f, indent=2)
            
            # Log the mail send
            self.ccmaster.cli_log(f"Mail sent: '{subject}' to {len(recipients)} recipients", 
                                log_type='info', color='BLUE')
            
            return {
                "success": True,
                "mail_id": mail_id,
                "subject": subject,
                "recipients": recipient_names,
                "recipient_count": len(recipients),
                "priority": priority,
                "message": f"Mail sent successfully to {len(recipients)} recipients"
            }
            
        except Exception as e:
            return {"error": f"Failed to send mail: {str(e)}"}
    
    def check_mail(self, unread_only: bool = True, limit: int = 10) -> Dict[str, Any]:
        """Check mailbox for new messages"""
        try:
            # Get current session
            current_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            if current_session == 'unknown':
                return {"error": "Cannot determine session ID for mail checking"}
            
            # Get inbox path
            inbox_path = self.mailbox_dir / current_session / "inbox"
            if not inbox_path.exists():
                return {
                    "success": True,
                    "mail_count": 0,
                    "mails": [],
                    "message": "No mail in inbox"
                }
            
            # Load all mail files
            mails = []
            mail_files = sorted(inbox_path.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            for mail_file in mail_files[:limit]:
                try:
                    with open(mail_file, 'r') as f:
                        mail_data = json.load(f)
                    
                    # Check if unread
                    is_read = current_session in mail_data.get('read_by', [])
                    if unread_only and is_read:
                        continue
                    
                    # Add read status
                    mail_data['is_read'] = is_read
                    mails.append(mail_data)
                    
                except Exception as e:
                    self.ccmaster.cli_log(f"Error reading mail {mail_file}: {e}", log_type='warning')
            
            # Get unread count
            unread_count = len([m for m in mails if not m['is_read']])
            
            # Log mail check
            if unread_count > 0:
                self.ccmaster.cli_log(f"You have {unread_count} unread mail(s)", log_type='info', color='CYAN')
            
            return {
                "success": True,
                "mail_count": len(mails),
                "unread_count": unread_count,
                "mails": mails,
                "message": f"Found {len(mails)} mail(s), {unread_count} unread"
            }
            
        except Exception as e:
            return {"error": f"Failed to check mail: {str(e)}"}
    
    def reply_mail(self, mail_id: str, body: str, reply_all: bool = False) -> Dict[str, Any]:
        """Reply to a mail message"""
        try:
            # Get current session
            current_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            if current_session == 'unknown':
                return {"error": "Cannot determine session ID for mail reply"}
            
            # Find the original mail
            inbox_path = self.mailbox_dir / current_session / "inbox"
            mail_file = inbox_path / f"{mail_id}.json"
            
            if not mail_file.exists():
                return {"error": f"Mail {mail_id} not found in inbox"}
            
            # Load original mail
            with open(mail_file, 'r') as f:
                original_mail = json.load(f)
            
            # Mark as read if not already
            if current_session not in original_mail.get('read_by', []):
                original_mail.setdefault('read_by', []).append(current_session)
                with open(mail_file, 'w') as f:
                    json.dump(original_mail, f, indent=2)
            
            # Determine recipients
            recipients = []
            if reply_all:
                # Reply to sender and all original recipients except self
                recipients.append(original_mail['from'])
                for recipient in original_mail['to']:
                    if recipient != current_session and recipient not in recipients:
                        recipients.append(recipient)
            else:
                # Reply only to sender
                recipients = [original_mail['from']]
            
            # Create reply subject
            subject = original_mail['subject']
            if not subject.startswith("Re: "):
                subject = f"Re: {subject}"
            
            # Send the reply
            result = self.send_mail(
                subject=subject,
                body=body,
                to_sessions=recipients,
                priority=original_mail.get('priority', 'normal')
            )
            
            if result.get('success'):
                # Add reply reference to original mail
                reply_ref = {
                    "mail_id": result['mail_id'],
                    "from": current_session,
                    "timestamp": datetime.now().isoformat(),
                    "preview": body[:100]
                }
                original_mail.setdefault('replies', []).append(reply_ref)
                
                # Update original mail with reply info
                with open(mail_file, 'w') as f:
                    json.dump(original_mail, f, indent=2)
                
                result['original_mail_id'] = mail_id
                result['message'] = f"Reply sent to {len(recipients)} recipient(s)"
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to reply to mail: {str(e)}"}
    
    def list_mail(self, folder: str = "inbox", unread_only: bool = False, 
                  from_session: str = None, priority: str = None) -> Dict[str, Any]:
        """List mail messages with filtering"""
        try:
            # Get current session
            current_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            if current_session == 'unknown':
                return {"error": "Cannot determine session ID for mail listing"}
            
            # Determine folder path
            if folder == "inbox":
                folder_path = self.mailbox_dir / current_session / "inbox"
            elif folder == "sent":
                folder_path = self.mailbox_dir / current_session / "sent"
            else:  # all
                # List both inbox and sent
                inbox_path = self.mailbox_dir / current_session / "inbox"
                sent_path = self.mailbox_dir / current_session / "sent"
                folder_path = None
            
            mails = []
            
            # Helper function to load and filter mails
            def load_mails_from_folder(path, mail_type):
                if not path.exists():
                    return
                
                for mail_file in sorted(path.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
                    try:
                        with open(mail_file, 'r') as f:
                            mail_data = json.load(f)
                        
                        # Apply filters
                        if from_session and mail_data.get('from') != from_session:
                            continue
                        
                        if priority and mail_data.get('priority') != priority:
                            continue
                        
                        is_read = current_session in mail_data.get('read_by', [])
                        if unread_only and is_read:
                            continue
                        
                        # Add metadata
                        mail_data['is_read'] = is_read
                        mail_data['folder'] = mail_type
                        
                        mails.append(mail_data)
                        
                    except Exception as e:
                        self.ccmaster.cli_log(f"Error reading mail {mail_file}: {e}", log_type='warning')
            
            # Load mails based on folder selection
            if folder_path:
                load_mails_from_folder(folder_path, folder)
            else:
                if inbox_path:
                    load_mails_from_folder(inbox_path, "inbox")
                if sent_path:
                    load_mails_from_folder(sent_path, "sent")
            
            # Sort by timestamp
            mails.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Summary statistics
            total_count = len(mails)
            unread_count = len([m for m in mails if not m.get('is_read', False) and m.get('folder') == 'inbox'])
            
            return {
                "success": True,
                "folder": folder,
                "total_count": total_count,
                "unread_count": unread_count,
                "mails": mails,
                "filters": {
                    "unread_only": unread_only,
                    "from_session": from_session,
                    "priority": priority
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to list mail: {str(e)}"}
    
    def send_job_to_session(self, session_id: str, title: str, description: str, 
                           priority: str = "p1", deadline: str = None, 
                           dependencies: List[str] = None) -> Dict[str, Any]:
        """Send a job to a session's job queue"""
        try:
            # Validate session exists
            if session_id not in self.ccmaster.sessions:
                return {"error": f"Session {session_id} not found"}
            
            # Get sender info
            sender_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            sender_identity = self.session_identities.get(sender_session, sender_session)
            
            # Create job data
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            job_data = {
                "id": job_id,
                "title": title,
                "description": description,
                "priority": priority,
                "status": "pending",
                "created_by": sender_session,
                "created_by_identity": sender_identity,
                "assigned_to": session_id,
                "created_at": datetime.now().isoformat(),
                "deadline": deadline,
                "dependencies": dependencies or [],
                "started_at": None,
                "completed_at": None,
                "result": None,
                "artifacts": []
            }
            
            # Save job to target session's queue
            session_queue_dir = self.job_queue_dir / session_id
            session_queue_dir.mkdir(parents=True, exist_ok=True)
            
            job_file = session_queue_dir / f"{job_id}.json"
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            # Log the job assignment with more details
            target_identity = self.session_identities.get(session_id, session_id)
            self.ccmaster.cli_log(f"📋 Job '{title}' ({priority}) → {target_identity}'s queue", 
                                log_type='info', color='MAGENTA')
            
            # Check if target is idle and notify about automatic execution
            if session_id in self.ccmaster.current_status:
                status = self.ccmaster.current_status.get(session_id)
                if status == 'idle':
                    self.ccmaster.cli_log(f"💡 {target_identity} is idle - job will start automatically", 
                                        log_type='info', color='GREEN')
                else:
                    self.ccmaster.cli_log(f"⏳ {target_identity} is {status} - job queued for when idle", 
                                        log_type='info', color='YELLOW')
            
            return {
                "success": True,
                "job_id": job_id,
                "title": title,
                "assigned_to": target_identity,
                "priority": priority,
                "message": f"Job {job_id} added to {target_identity}'s queue"
            }
            
        except Exception as e:
            return {"error": f"Failed to send job: {str(e)}"}
    
    def send_job_to_member(self, member: str, title: str, description: str,
                          priority: str = "p1", deadline: str = None,
                          dependencies: List[str] = None) -> Dict[str, Any]:
        """Send a job to a team member by their identity"""
        try:
            # Look up session ID by member identity
            if member not in self.team_members:
                return {
                    "error": f"Team member '{member}' not found",
                    "available_members": list(self.team_members.keys())
                }
            
            session_id = self.team_members[member]
            
            # Send job using session ID
            result = self.send_job_to_session(
                session_id=session_id,
                title=title,
                description=description,
                priority=priority,
                deadline=deadline,
                dependencies=dependencies
            )
            
            # Add member info to result
            if result.get('success'):
                result['member'] = member
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to send job to member: {str(e)}"}
    
    def list_jobs(self, session_id: str = None, status_filter: List[str] = None,
                  priority_filter: List[str] = None) -> Dict[str, Any]:
        """List jobs in the queue"""
        try:
            # Use current session if not specified
            if not session_id:
                session_id = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
                if session_id == 'unknown':
                    return {"error": "Cannot determine session ID for job listing"}
            
            # Get session's job queue directory
            session_queue_dir = self.job_queue_dir / session_id
            if not session_queue_dir.exists():
                return {
                    "success": True,
                    "jobs": [],
                    "total_count": 0,
                    "message": "No jobs in queue"
                }
            
            # Load all job files
            jobs = []
            for job_file in session_queue_dir.glob("*.json"):
                try:
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    # Apply filters
                    if status_filter and job_data.get('status') not in status_filter:
                        continue
                    
                    if priority_filter and job_data.get('priority') not in priority_filter:
                        continue
                    
                    jobs.append(job_data)
                    
                except Exception as e:
                    self.ccmaster.cli_log(f"Error reading job {job_file}: {e}", log_type='warning')
            
            # Sort by priority (p0 first) and creation time
            priority_order = {"p0": 0, "p1": 1, "p2": 2}
            jobs.sort(key=lambda x: (
                priority_order.get(x.get('priority', 'p1'), 1),
                x.get('created_at', '')
            ))
            
            # Count by status
            status_counts = {
                "pending": len([j for j in jobs if j.get('status') == 'pending']),
                "doing": len([j for j in jobs if j.get('status') == 'doing']),
                "done": len([j for j in jobs if j.get('status') == 'done']),
                "cancelled": len([j for j in jobs if j.get('status') == 'cancelled'])
            }
            
            return {
                "success": True,
                "jobs": jobs,
                "total_count": len(jobs),
                "status_counts": status_counts,
                "session_id": session_id,
                "session_identity": self.session_identities.get(session_id, session_id)
            }
            
        except Exception as e:
            return {"error": f"Failed to list jobs: {str(e)}"}
    
    def cancel_job(self, job_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel a pending job"""
        try:
            # Get current session
            current_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            
            # Find the job file
            job_file = None
            job_data = None
            
            # Search in current session's queue first
            if current_session != 'unknown':
                session_queue_dir = self.job_queue_dir / current_session
                potential_file = session_queue_dir / f"{job_id}.json"
                if potential_file.exists():
                    job_file = potential_file
            
            # If not found, search all queues
            if not job_file:
                for queue_dir in self.job_queue_dir.iterdir():
                    if queue_dir.is_dir():
                        potential_file = queue_dir / f"{job_id}.json"
                        if potential_file.exists():
                            job_file = potential_file
                            break
            
            if not job_file:
                return {"error": f"Job {job_id} not found"}
            
            # Load job data
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check if job can be cancelled
            if job_data.get('status') not in ['pending', 'doing']:
                return {"error": f"Job {job_id} is {job_data.get('status')}, cannot cancel"}
            
            # Update job status
            job_data['status'] = 'cancelled'
            job_data['cancelled_at'] = datetime.now().isoformat()
            job_data['cancelled_by'] = current_session
            job_data['cancel_reason'] = reason
            
            # Save updated job
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            # Log cancellation
            self.ccmaster.cli_log(f"Job '{job_data['title']}' cancelled{' - ' + reason if reason else ''}", 
                                log_type='warning')
            
            return {
                "success": True,
                "job_id": job_id,
                "title": job_data['title'],
                "previous_status": job_data.get('status'),
                "message": f"Job {job_id} cancelled successfully"
            }
            
        except Exception as e:
            return {"error": f"Failed to cancel job: {str(e)}"}
    
    def job_status(self, job_id: str) -> Dict[str, Any]:
        """Get detailed status of a job"""
        try:
            # Find the job file
            job_file = None
            job_data = None
            
            # Search all queues
            for queue_dir in self.job_queue_dir.iterdir():
                if queue_dir.is_dir():
                    potential_file = queue_dir / f"{job_id}.json"
                    if potential_file.exists():
                        job_file = potential_file
                        break
            
            if not job_file:
                return {"error": f"Job {job_id} not found"}
            
            # Load job data
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Add computed fields
            job_data['assigned_to_identity'] = self.session_identities.get(
                job_data.get('assigned_to'), job_data.get('assigned_to')
            )
            
            # Check dependencies status
            if job_data.get('dependencies'):
                dep_status = []
                for dep_id in job_data['dependencies']:
                    # Try to find dependency job
                    dep_found = False
                    for queue_dir in self.job_queue_dir.iterdir():
                        if queue_dir.is_dir():
                            dep_file = queue_dir / f"{dep_id}.json"
                            if dep_file.exists():
                                with open(dep_file, 'r') as f:
                                    dep_data = json.load(f)
                                dep_status.append({
                                    "id": dep_id,
                                    "status": dep_data.get('status'),
                                    "title": dep_data.get('title')
                                })
                                dep_found = True
                                break
                    
                    if not dep_found:
                        dep_status.append({
                            "id": dep_id,
                            "status": "not_found",
                            "title": "Unknown"
                        })
                
                job_data['dependency_status'] = dep_status
            
            return {
                "success": True,
                "job": job_data
            }
            
        except Exception as e:
            return {"error": f"Failed to get job status: {str(e)}"}
    
    def complete_job(self, job_id: str, result: str, artifacts: List[str] = None) -> Dict[str, Any]:
        """Mark a job as completed"""
        try:
            # Get current session
            current_session = os.environ.get('CCMASTER_SESSION_ID', 'unknown')
            if current_session == 'unknown':
                return {"error": "Cannot determine session ID"}
            
            # Find job in current session's queue
            session_queue_dir = self.job_queue_dir / current_session
            job_file = session_queue_dir / f"{job_id}.json"
            
            if not job_file.exists():
                return {"error": f"Job {job_id} not found in your queue"}
            
            # Load job data
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Check if job can be completed
            if job_data.get('status') == 'done':
                return {"error": f"Job {job_id} is already completed"}
            
            if job_data.get('status') == 'cancelled':
                return {"error": f"Job {job_id} is cancelled"}
            
            # Update job data
            job_data['status'] = 'done'
            job_data['completed_at'] = datetime.now().isoformat()
            job_data['result'] = result
            job_data['artifacts'] = artifacts or []
            
            # Save updated job
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            # Log completion with details
            current_identity = self.session_identities.get(current_session, current_session)
            self.ccmaster.cli_log(f"✅ Job '{job_data['title']}' completed by {current_identity}", 
                                log_type='info', color='GREEN')
            self.ccmaster.cli_log(f"📊 Result: {result[:100]}{'...' if len(result) > 100 else ''}", 
                                log_type='info', color='CYAN')
            
            # Notify the job creator if different from executor
            if job_data.get('created_by') and job_data['created_by'] != current_session:
                creator_identity = self.session_identities.get(job_data['created_by'], job_data['created_by'])
                self.ccmaster.cli_log(f"📨 Notifying {creator_identity} about job completion", 
                                    log_type='info', color='MAGENTA')
            
            return {
                "success": True,
                "job_id": job_id,
                "title": job_data['title'],
                "message": f"Job {job_id} marked as completed"
            }
            
        except Exception as e:
            return {"error": f"Failed to complete job: {str(e)}"}