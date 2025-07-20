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
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from .project_communication import ProjectCommunication, TaskStatus, TaskPriority


class SessionTools:
    """Tools for managing Claude Code sessions"""
    
    def __init__(self, ccmaster_instance):
        self.ccmaster = ccmaster_instance
        
        # Initialize project communication lazily when needed
        self.project_comm = None
        self._project_comm_initialized = False
        
        self.tools = {
            "list_sessions": self.list_sessions,
            "get_session_status": self.get_session_status,
            "send_message_to_session": self.send_message_to_session,
            "create_session": self.create_session,
            "kill_session": self.kill_session,
            "spawn_temp_session": self.spawn_temp_session,
            "coordinate_sessions": self.coordinate_sessions,
            "get_session_logs": self.get_session_logs,
            "prompt": self.prompt,
            "get_team_info": self.get_team_info,
            "broadcast_to_team": self.broadcast_to_team,
            "wait_for_dependency": self.wait_for_dependency,
            "notify_completion": self.notify_completion,
            # New task-based tools
            "create_task": self.create_task,
            "get_my_tasks": self.get_my_tasks,
            "update_task_status": self.update_task_status,
            "get_team_messages": self.get_team_messages
        }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for MCP registration"""
        return [
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
                "name": "get_session_status",
                "description": "Get current status of a specific session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to check"
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "send_message_to_session",
                "description": "Send a message/prompt to a specific session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Target session ID"
                        },
                        "message": {
                            "type": "string",
                            "description": "Message to send to the session"
                        },
                        "wait_for_response": {
                            "type": "boolean",
                            "description": "Wait for session to respond",
                            "default": False
                        }
                    },
                    "required": ["session_id", "message"]
                }
            },
            {
                "name": "create_session",
                "description": "Create a new Claude Code session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "working_dir": {
                            "type": "string",
                            "description": "Working directory for the session"
                        },
                        "watch_mode": {
                            "type": "boolean",
                            "description": "Enable watch mode for auto-continuation",
                            "default": True
                        },
                        "max_turns": {
                            "type": "integer",
                            "description": "Maximum auto-continue turns"
                        },
                        "initial_prompt": {
                            "type": "string",
                            "description": "Initial prompt to send to the new session"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role of this team member (e.g., 'Frontend Developer', 'Backend Developer')"
                        }
                    }
                }
            },
            {
                "name": "kill_session",
                "description": "Kill/terminate a specific session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to kill"
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "spawn_temp_session",
                "description": "Spawn a temporary session, run a command, and kill it",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "working_dir": {
                            "type": "string",
                            "description": "Working directory for the session"
                        },
                        "command": {
                            "type": "string",
                            "description": "Command to execute in the session"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds",
                            "default": 60
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "coordinate_sessions",
                "description": "Coordinate multiple sessions for a complex task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task to coordinate"
                        },
                        "session_assignments": {
                            "type": "object",
                            "description": "Session ID to task mapping"
                        }
                    },
                    "required": ["task_description", "session_assignments"]
                }
            },
            {
                "name": "get_session_logs",
                "description": "Get logs from a specific session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to get logs from"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of recent lines to get",
                            "default": 100
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "prompt",
                "description": "Send a prompt/message to CCMaster console (demo tool)",
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
                "name": "get_team_info",
                "description": "Get information about all team members (sessions) including their roles and status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "broadcast_to_team",
                "description": "Broadcast a message to all active team members",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to broadcast to all team members"
                        },
                        "sender_role": {
                            "type": "string",
                            "description": "Role of the sender (e.g., 'Frontend Developer')"
                        },
                        "exclude_session": {
                            "type": "string",
                            "description": "Session ID to exclude from broadcast (usually the sender)"
                        }
                    },
                    "required": ["message", "sender_role"]
                }
            },
            {
                "name": "wait_for_dependency",
                "description": "Wait for another team member to complete a specific task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dependency_session": {
                            "type": "string",
                            "description": "Session ID of the team member you're waiting for"
                        },
                        "dependency_description": {
                            "type": "string",
                            "description": "Description of what you're waiting for"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Maximum time to wait in seconds",
                            "default": 300
                        }
                    },
                    "required": ["dependency_session", "dependency_description"]
                }
            },
            {
                "name": "notify_completion",
                "description": "Notify team members that a specific task or component is completed",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the completed task"
                        },
                        "output_details": {
                            "type": "string",
                            "description": "Details about the output (files created, APIs available, etc.)"
                        },
                        "notify_sessions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of session IDs to notify. If empty, notifies all team members"
                        }
                    },
                    "required": ["task_description", "output_details"]
                }
            },
            {
                "name": "create_task",
                "description": "Create a structured task in the project .ccmaster/tasks directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Short title for the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of what needs to be done"
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Session ID of the team member to assign this task to"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level",
                            "default": "medium"
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["feature", "bug", "refactor", "test", "docs"],
                            "description": "Type of task",
                            "default": "feature"
                        },
                        "acceptance_criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of criteria that must be met for the task to be considered complete"
                        }
                    },
                    "required": ["title", "description", "assigned_to"]
                }
            },
            {
                "name": "get_my_tasks",
                "description": "Get tasks assigned to a specific session from .ccmaster/tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to get tasks for"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "blocked", "completed", "cancelled"],
                            "description": "Filter by task status (optional)"
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "update_task_status",
                "description": "Update the status of a task in .ccmaster/tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to update"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "blocked", "completed", "cancelled"],
                            "description": "New status for the task"
                        },
                        "output": {
                            "type": "string",
                            "description": "Output details (for completed tasks)"
                        },
                        "blocker": {
                            "type": "string",
                            "description": "Description of what's blocking the task (for blocked status)"
                        }
                    },
                    "required": ["task_id", "status"]
                }
            },
            {
                "name": "get_team_messages",
                "description": "Get unread messages for a session from .ccmaster/messages",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to get messages for"
                        }
                    },
                    "required": ["session_id"]
                }
            }
        ]
    
    def _ensure_project_comm(self):
        """Lazily initialize project communication when first needed"""
        if not self._project_comm_initialized:
            self._project_comm_initialized = True
            try:
                working_dir = os.getcwd()
                self.project_comm = ProjectCommunication(working_dir)
                if hasattr(self.ccmaster, 'cli_log'):
                    self.ccmaster.cli_log("Project communication initialized in .ccmaster/", log_type='info', color='\033[92m')
            except Exception as e:
                if hasattr(self.ccmaster, 'logger'):
                    self.ccmaster.logger.warning(f"Could not initialize project communication: {e}")
    
    def list_sessions(self, include_ended: bool = False) -> Dict[str, Any]:
        """List all active sessions"""
        sessions = []
        for session_id, session_data in self.ccmaster.sessions.items():
            if not include_ended and session_data.get('status') == 'ended':
                continue
            
            session_info = {
                "session_id": session_id,
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
            # Log the message being sent for debugging
            self.ccmaster.logger.info(f"Sending message to session {session_id}: {message[:100]}...")
            
            # Send message through CCMaster's existing mechanism which now uses file-based approach
            success = self.ccmaster.send_continue_to_claude(session_id, message)
            
            result = {
                "success": success,
                "session_id": session_id,
                "message_sent": message,
                "timestamp": datetime.now().isoformat()
            }
            
            if wait_for_response:
                # Wait for session to process the message
                time.sleep(3)  # Increased wait time for file-based approach
                result["session_status"] = self.ccmaster.current_status.get(session_id, 'unknown')
            
            return result
            
        except Exception as e:
            self.ccmaster.logger.error(f"Error sending message to session {session_id}: {str(e)}")
            return {"error": f"Failed to send message: {str(e)}"}
    
    def create_session(self, working_dir: str = None, watch_mode: bool = True, max_turns: int = None, initial_prompt: str = None, role: str = None) -> Dict[str, Any]:
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
                'max_turns': max_turns,
                'role': role or 'Team Member',
                'initial_prompt': initial_prompt
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
                    
                    # Save initial prompt if provided
                    if initial_prompt:
                        self._ensure_project_comm()
                        if self.project_comm:
                            # Save prompt to project communication system
                            prompt_file = self.project_comm.save_initial_prompt(session_id, initial_prompt, role)
                            self.ccmaster.cli_log(f"Saved initial prompt for {role or 'Team Member'} to project .ccmaster/", log_type='info')
                        
                        # Wait a bit for Claude to fully start
                        time.sleep(3)
                        
                        # Send the initial prompt using the new system
                        self.ccmaster.cli_log(f"Sending initial prompt to {role or 'Team Member'}", log_type='info')
                        success = self.ccmaster.send_continue_to_claude(session_id, initial_prompt)
                        if success:
                            self.ccmaster.cli_log(f"Initial prompt sent successfully", log_type='info', color='\033[92m')  # GREEN
                        else:
                            self.ccmaster.cli_log(f"Failed to send initial prompt", log_type='warning')
                    elif initial_prompt:
                        # Fallback to old method if project communication not available
                        time.sleep(3)
                        success = self.ccmaster.send_continue_to_claude(session_id, initial_prompt)
                        if success:
                            self.ccmaster.cli_log(f"Initial prompt sent (using temp file)", log_type='info')
                        else:
                            self.ccmaster.cli_log(f"Failed to send initial prompt", log_type='warning')
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
                "role": role or 'Team Member',
                "initial_prompt_sent": bool(initial_prompt),
                "created_at": datetime.now().isoformat(),
                "message": f"MCP session {session_id} created for {role or 'Team Member'}"
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
    
    def get_team_info(self) -> Dict[str, Any]:
        """Get information about all team members including roles and status"""
        try:
            team_members = []
            
            for session_id, session_data in self.ccmaster.sessions.items():
                if session_data.get('status') == 'ended':
                    continue
                
                # Get session info with role
                member_info = {
                    "session_id": session_id,
                    "role": session_data.get('role', 'Unknown'),
                    "status": session_data.get('status', 'unknown'),
                    "current_state": self.ccmaster.current_status.get(session_id, 'unknown'),
                    "working_dir": session_data.get('working_dir'),
                    "created_at": session_data.get('started_at'),
                    "is_active": session_id in self.ccmaster.active_sessions,
                    "display_index": self.ccmaster.active_sessions.get(session_id, {}).get('index', 0)
                }
                
                # Add PM indicator
                if session_data.get('role') == 'Project Manager':
                    member_info['is_pm'] = True
                
                team_members.append(member_info)
            
            # Sort by display index
            team_members.sort(key=lambda x: x.get('display_index', 999))
            
            return {
                "success": True,
                "team_members": team_members,
                "total_members": len(team_members),
                "active_members": len([m for m in team_members if m['is_active']]),
                "project_directory": os.getcwd()
            }
            
        except Exception as e:
            return {"error": f"Failed to get team info: {str(e)}"}
    
    def broadcast_to_team(self, message: str, sender_role: str, exclude_session: str = None) -> Dict[str, Any]:
        """Broadcast a message to all active team members"""
        try:
            broadcast_results = {}
            recipients = []
            
            # Format broadcast message
            formatted_message = f"""
[TEAM BROADCAST from {sender_role}]
{message}
[END BROADCAST]
"""
            
            # Send to all active sessions except the sender
            for session_id in self.ccmaster.active_sessions:
                if exclude_session and session_id == exclude_session:
                    continue
                
                result = self.send_message_to_session(session_id, formatted_message)
                broadcast_results[session_id] = result
                
                if result.get('success'):
                    session_data = self.ccmaster.sessions.get(session_id, {})
                    recipients.append({
                        "session_id": session_id,
                        "role": session_data.get('role', 'Unknown')
                    })
            
            # Also log to console for visibility
            self.ccmaster.cli_log(f"📢 Broadcast from {sender_role}: {message}", log_type='mcp', color='\033[95m')  # PURPLE
            
            return {
                "success": True,
                "message": "Broadcast sent to team",
                "sender_role": sender_role,
                "recipients": recipients,
                "broadcast_results": broadcast_results
            }
            
        except Exception as e:
            return {"error": f"Failed to broadcast: {str(e)}"}
    
    def wait_for_dependency(self, dependency_session: str, dependency_description: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for another team member to complete a task"""
        try:
            if dependency_session not in self.ccmaster.sessions:
                return {"error": f"Dependency session {dependency_session} not found"}
            
            dependency_role = self.ccmaster.sessions[dependency_session].get('role', 'Unknown')
            
            # Log the waiting status
            self.ccmaster.cli_log(
                f"⏳ Waiting for {dependency_role} ({dependency_session}) to complete: {dependency_description}", 
                log_type='mcp', 
                color='\033[93m'  # YELLOW
            )
            
            # Send notification to the dependency session
            notify_msg = f"""
[DEPENDENCY REQUEST]
Another team member is waiting for you to complete:
{dependency_description}

Please prioritize this task if possible.
"""
            self.send_message_to_session(dependency_session, notify_msg)
            
            # Wait for completion with timeout
            start_time = time.time()
            check_interval = 5  # Check every 5 seconds
            
            while time.time() - start_time < timeout:
                # Check if dependency session is still active
                if dependency_session not in self.ccmaster.active_sessions:
                    return {
                        "success": False,
                        "reason": "dependency_session_ended",
                        "message": f"{dependency_role} session ended before completing the task"
                    }
                
                # Check status
                status = self.ccmaster.current_status.get(dependency_session, 'unknown')
                
                # Simple heuristic: if idle after being active, might be done
                # In real implementation, would need better completion detection
                if status == 'idle':
                    self.ccmaster.cli_log(
                        f"✓ {dependency_role} appears to have completed the task", 
                        log_type='mcp', 
                        color='\033[92m'  # GREEN
                    )
                    
                    return {
                        "success": True,
                        "dependency_session": dependency_session,
                        "dependency_role": dependency_role,
                        "wait_time": time.time() - start_time,
                        "message": "Dependency appears to be completed"
                    }
                
                time.sleep(check_interval)
            
            # Timeout reached
            return {
                "success": False,
                "reason": "timeout",
                "message": f"Timeout waiting for {dependency_role} to complete: {dependency_description}",
                "wait_time": timeout
            }
            
        except Exception as e:
            return {"error": f"Failed to wait for dependency: {str(e)}"}
    
    def notify_completion(self, task_description: str, output_details: str, notify_sessions: List[str] = None) -> Dict[str, Any]:
        """Notify team members about task completion"""
        try:
            # Get sender info
            # This would need to be passed or determined from context
            # For now, we'll include it in the notification
            
            notification_msg = f"""
[TASK COMPLETED]
Task: {task_description}
Output: {output_details}

You can now proceed with any tasks that depend on this completion.
[END NOTIFICATION]
"""
            
            results = {}
            notified = []
            
            # If specific sessions provided, notify only those
            if notify_sessions:
                target_sessions = [s for s in notify_sessions if s in self.ccmaster.active_sessions]
            else:
                # Notify all active sessions
                target_sessions = list(self.ccmaster.active_sessions.keys())
            
            for session_id in target_sessions:
                result = self.send_message_to_session(session_id, notification_msg)
                results[session_id] = result
                
                if result.get('success'):
                    session_data = self.ccmaster.sessions.get(session_id, {})
                    notified.append({
                        "session_id": session_id,
                        "role": session_data.get('role', 'Unknown')
                    })
            
            # Log to console
            self.ccmaster.cli_log(
                f"✅ Task Completed: {task_description}", 
                log_type='mcp', 
                color='\033[92m'  # GREEN
            )
            
            return {
                "success": True,
                "task_description": task_description,
                "output_details": output_details,
                "notified_sessions": notified,
                "notification_results": results
            }
            
        except Exception as e:
            return {"error": f"Failed to notify completion: {str(e)}"}
    
    def create_task(self, title: str, description: str, assigned_to: str, 
                   priority: str = "medium", task_type: str = "feature",
                   acceptance_criteria: List[str] = None) -> Dict[str, Any]:
        """Create a task in the project .ccmaster/tasks directory"""
        try:
            self._ensure_project_comm()
            if not self.project_comm:
                return {"error": "Project communication not initialized. Not in a project directory?"}
            
            # Get PM session ID (could be passed or determined from context)
            created_by = "pm_session"  # Default for now
            
            # Convert priority string to enum
            priority_enum = TaskPriority.MEDIUM
            if priority.lower() == "low":
                priority_enum = TaskPriority.LOW
            elif priority.lower() == "high":
                priority_enum = TaskPriority.HIGH
            elif priority.lower() == "urgent":
                priority_enum = TaskPriority.URGENT
            
            task = self.project_comm.create_task(
                title=title,
                description=description,
                assigned_to=assigned_to,
                created_by=created_by,
                priority=priority_enum,
                task_type=task_type,
                acceptance_criteria=acceptance_criteria
            )
            
            self.ccmaster.cli_log(
                f"✅ Task created: {task['id']} - {title} (assigned to: {assigned_to})",
                log_type='mcp',
                color='\033[92m'  # GREEN
            )
            
            # Also send a message to notify the assignee
            if hasattr(self, 'send_message_to_session'):
                msg = f"New task assigned: {title}\nPriority: {priority}\nCheck your tasks with /mcp__ccmaster__get_my_tasks"
                self.send_message_to_session(assigned_to, msg)
            
            return {
                "success": True,
                "task": task
            }
            
        except Exception as e:
            return {"error": f"Failed to create task: {str(e)}"}
    
    def get_my_tasks(self, session_id: str, status: str = None) -> Dict[str, Any]:
        """Get tasks assigned to a specific session"""
        try:
            self._ensure_project_comm()
            if not self.project_comm:
                return {"error": "Project communication not initialized. Not in a project directory?"}
            
            # Convert status string to enum if provided
            status_enum = None
            if status:
                status_map = {
                    "pending": TaskStatus.PENDING,
                    "in_progress": TaskStatus.IN_PROGRESS,
                    "blocked": TaskStatus.BLOCKED,
                    "completed": TaskStatus.COMPLETED,
                    "cancelled": TaskStatus.CANCELLED
                }
                status_enum = status_map.get(status.lower())
            
            tasks = self.project_comm.get_tasks_for_session(session_id, status_enum)
            
            # Update session status in project directory
            if self.project_comm:
                current_task = None
                for task in tasks:
                    if task['status'] == 'in_progress':
                        current_task = task['id']
                        break
                
                self.project_comm.update_session_status(
                    session_id,
                    'working' if current_task else 'idle',
                    current_task=current_task
                )
            
            return {
                "success": True,
                "session_id": session_id,
                "task_count": len(tasks),
                "tasks": tasks
            }
            
        except Exception as e:
            return {"error": f"Failed to get tasks: {str(e)}"}
    
    def update_task_status(self, task_id: str, status: str, 
                          output: str = None, blocker: str = None) -> Dict[str, Any]:
        """Update the status of a task"""
        try:
            self._ensure_project_comm()
            if not self.project_comm:
                return {"error": "Project communication not initialized. Not in a project directory?"}
            
            # Convert status string to enum
            status_map = {
                "pending": TaskStatus.PENDING,
                "in_progress": TaskStatus.IN_PROGRESS,
                "blocked": TaskStatus.BLOCKED,
                "completed": TaskStatus.COMPLETED,
                "cancelled": TaskStatus.CANCELLED
            }
            
            status_enum = status_map.get(status.lower())
            if not status_enum:
                return {"error": f"Invalid status: {status}"}
            
            success = self.project_comm.update_task_status(
                task_id=task_id,
                new_status=status_enum,
                output=output,
                blocker=blocker
            )
            
            if success:
                self.ccmaster.cli_log(
                    f"✅ Task {task_id} status updated to: {status}",
                    log_type='mcp',
                    color='\033[92m'  # GREEN
                )
                
                # If task is completed, notify PM
                if status_enum == TaskStatus.COMPLETED:
                    self.project_comm.broadcast_event("task_completed", {
                        "task_id": task_id,
                        "output": output
                    })
            
            return {
                "success": success,
                "task_id": task_id,
                "new_status": status
            }
            
        except Exception as e:
            return {"error": f"Failed to update task status: {str(e)}"}
    
    def get_team_messages(self, session_id: str) -> Dict[str, Any]:
        """Get unread messages for a session"""
        try:
            self._ensure_project_comm()
            if not self.project_comm:
                return {"error": "Project communication not initialized. Not in a project directory?"}
            
            messages = self.project_comm.get_unread_messages(session_id)
            
            # Mark messages as read
            for msg in messages:
                self.project_comm.mark_message_read(session_id, msg['id'])
            
            return {
                "success": True,
                "session_id": session_id,
                "message_count": len(messages),
                "messages": messages
            }
            
        except Exception as e:
            return {"error": f"Failed to get messages: {str(e)}"}