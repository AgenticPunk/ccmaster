#!/usr/bin/env python3
"""
Project-level communication system for CCMaster teams
Creates and manages .ccmaster/ directory in project root for team collaboration
"""

import os
import json
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import threading
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    # fcntl not available on Windows
    HAS_FCNTL = False

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ProjectCommunication:
    """Manages project-level communication through .ccmaster/ directory"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.ccmaster_dir = self.project_dir / '.ccmaster'
        self.tasks_dir = self.ccmaster_dir / 'tasks'
        self.messages_dir = self.ccmaster_dir / 'messages'
        self.status_dir = self.ccmaster_dir / 'status'
        self.events_dir = self.ccmaster_dir / 'events'
        self.prompts_dir = self.ccmaster_dir / 'prompts'
        
        # Create directory structure
        self._init_directories()
        
    def _init_directories(self):
        """Initialize .ccmaster directory structure in project"""
        dirs = [
            self.ccmaster_dir,
            self.tasks_dir,  # Single tasks directory
            self.messages_dir,
            self.status_dir,
            self.events_dir,
            self.prompts_dir
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Create README for team members
        readme_path = self.ccmaster_dir / 'README.md'
        if not readme_path.exists():
            readme_content = """# CCMaster Team Communication

This directory contains team communication files for CCMaster PM mode.

## Structure:
- `tasks/` - All task files (status tracked in JSON)
- `messages/` - Direct messages between team members
- `status/` - Real-time status of each team member
- `events/` - Team-wide events and notifications
- `prompts/` - Initial prompts for team members when they start

## Usage:
Team members automatically monitor these directories for updates.
Do not manually edit these files unless debugging.
"""
            readme_path.write_text(readme_content)
    
    def create_task(self, 
                   title: str,
                   description: str,
                   assigned_to: str,
                   created_by: str,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   task_type: str = "feature",
                   acceptance_criteria: List[str] = None,
                   dependencies: List[str] = None) -> Dict[str, Any]:
        """Create a new task and place it in pending directory"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "created_by": created_by,
            "priority": priority.value,
            "type": task_type,
            "acceptance_criteria": acceptance_criteria or [],
            "dependencies": dependencies or [],
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "output": None,
            "blocker": None
        }
        
        # Save to tasks directory
        task_file = self.tasks_dir / f"{task_id}.json"
        self._write_json_atomic(task_file, task)
        
        # Create assignment event
        self._create_event("task_assigned", {
            "task_id": task_id,
            "assigned_to": assigned_to,
            "title": title
        })
        
        return task
    
    def get_tasks_for_session(self, session_id: str, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a specific session"""
        tasks = []
        
        # Get all tasks from single directory
        if self.tasks_dir.exists():
            for task_file in self.tasks_dir.glob("*.json"):
                task = self._read_json_safe(task_file)
                if task and task.get("assigned_to") == session_id:
                    # Filter by status if specified
                    if status is None or task.get("status") == status.value:
                        tasks.append(task)
        
        # Sort by priority and creation time
        priority_order = {p.value: i for i, p in enumerate(TaskPriority)}
        tasks.sort(key=lambda t: (
            priority_order.get(t.get("priority", "medium"), 99),
            t.get("created_at", "")
        ))
        
        return tasks
    
    def update_task_status(self, task_id: str, new_status: TaskStatus, 
                          output: Optional[str] = None,
                          blocker: Optional[str] = None) -> bool:
        """Update task status in the JSON file"""
        # Find task file
        task_file = self.tasks_dir / f"{task_id}.json"
        
        if not task_file.exists():
            return False
        
        task_data = self._read_json_safe(task_file)
        if not task_data:
            return False
        
        # Update task data
        old_status = task_data["status"]
        task_data["status"] = new_status.value
        task_data["updated_at"] = datetime.now().isoformat()
        
        if new_status == TaskStatus.IN_PROGRESS and not task_data.get("started_at"):
            task_data["started_at"] = datetime.now().isoformat()
        elif new_status == TaskStatus.COMPLETED:
            task_data["completed_at"] = datetime.now().isoformat()
            if output:
                task_data["output"] = output
        elif new_status == TaskStatus.BLOCKED:
            task_data["blocker"] = blocker
        
        # Update the same file
        self._write_json_atomic(task_file, task_data)
        
        # Create status change event
        self._create_event("task_status_changed", {
            "task_id": task_id,
            "old_status": old_status,
            "new_status": new_status.value,
            "assigned_to": task_data.get("assigned_to")
        })
        
        return True
    
    def send_message(self, from_session: str, to_session: str, 
                    message: str, message_type: str = "info") -> Dict[str, Any]:
        """Send a message from one session to another"""
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        message_data = {
            "id": message_id,
            "from": from_session,
            "to": to_session,
            "message": message,
            "type": message_type,
            "created_at": datetime.now().isoformat(),
            "read": False
        }
        
        # Save to recipient's message directory
        recipient_dir = self.messages_dir / to_session
        recipient_dir.mkdir(exist_ok=True)
        
        message_file = recipient_dir / f"{message_id}.json"
        self._write_json_atomic(message_file, message_data)
        
        # Create message event
        self._create_event("message_sent", {
            "from": from_session,
            "to": to_session,
            "message_id": message_id
        })
        
        return message_data
    
    def get_unread_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all unread messages for a session"""
        messages = []
        session_dir = self.messages_dir / session_id
        
        if session_dir.exists():
            for msg_file in session_dir.glob("*.json"):
                msg_data = self._read_json_safe(msg_file)
                if msg_data and not msg_data.get("read", True):
                    messages.append(msg_data)
        
        # Sort by creation time
        messages.sort(key=lambda m: m.get("created_at", ""))
        return messages
    
    def mark_message_read(self, session_id: str, message_id: str) -> bool:
        """Mark a message as read"""
        msg_file = self.messages_dir / session_id / f"{message_id}.json"
        if msg_file.exists():
            msg_data = self._read_json_safe(msg_file)
            if msg_data:
                msg_data["read"] = True
                self._write_json_atomic(msg_file, msg_data)
                return True
        return False
    
    def update_session_status(self, session_id: str, status: str, 
                            current_task: Optional[str] = None,
                            details: Optional[str] = None):
        """Update session status in project directory"""
        status_data = {
            "session_id": session_id,
            "status": status,
            "current_task": current_task,
            "details": details,
            "updated_at": datetime.now().isoformat()
        }
        
        status_file = self.status_dir / f"{session_id}.json"
        self._write_json_atomic(status_file, status_data)
    
    def get_team_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all team members"""
        team_status = {}
        
        if self.status_dir.exists():
            for status_file in self.status_dir.glob("*.json"):
                session_id = status_file.stem
                status_data = self._read_json_safe(status_file)
                if status_data:
                    team_status[session_id] = status_data
        
        return team_status
    
    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all team members"""
        self._create_event(event_type, data, broadcast=True)
    
    def _create_event(self, event_type: str, data: Dict[str, Any], broadcast: bool = False):
        """Create an event file for team members to pick up"""
        event_id = f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        event_data = {
            "id": event_id,
            "type": event_type,
            "data": data,
            "broadcast": broadcast,
            "created_at": datetime.now().isoformat()
        }
        
        event_file = self.events_dir / f"{event_id}.json"
        self._write_json_atomic(event_file, event_data)
        
        # Clean up old events (keep last 100)
        self._cleanup_old_events()
    
    def save_initial_prompt(self, session_id: str, prompt: str, role: str = None) -> Path:
        """Save initial prompt for a session to be picked up when launched"""
        prompts_dir = self.ccmaster_dir / 'prompts'
        prompts_dir.mkdir(exist_ok=True)
        
        # Save JSON metadata
        prompt_data = {
            "session_id": session_id,
            "role": role,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
            "consumed": False
        }
        
        json_file = prompts_dir / f"{session_id}_prompt.json"
        self._write_json_atomic(json_file, prompt_data)
        
        # Also save plain text file for direct consumption
        txt_file = prompts_dir / f"{session_id}_prompt.txt"
        txt_file.write_text(prompt, encoding='utf-8')
        
        return txt_file  # Return the txt file path for cat command
    
    def get_initial_prompt(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get initial prompt for a session and mark it as consumed"""
        prompts_dir = self.ccmaster_dir / 'prompts'
        prompt_file = prompts_dir / f"{session_id}_prompt.json"
        
        if prompt_file.exists():
            prompt_data = self._read_json_safe(prompt_file)
            if prompt_data and not prompt_data.get("consumed", True):
                # Mark as consumed
                prompt_data["consumed"] = True
                prompt_data["consumed_at"] = datetime.now().isoformat()
                self._write_json_atomic(prompt_file, prompt_data)
                
                return prompt_data
        
        return None
    
    def _cleanup_old_events(self, keep_count: int = 100):
        """Clean up old event files"""
        if self.events_dir.exists():
            events = sorted(self.events_dir.glob("*.json"), 
                          key=lambda f: f.stat().st_mtime)
            if len(events) > keep_count:
                for event_file in events[:-keep_count]:
                    event_file.unlink(missing_ok=True)
    
    def _write_json_atomic(self, file_path: Path, data: Dict[str, Any]):
        """Write JSON file atomically to prevent corruption"""
        temp_file = file_path.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                # Use file locking to prevent concurrent writes (if available)
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            # Atomic rename
            temp_file.replace(file_path)
        except Exception as e:
            temp_file.unlink(missing_ok=True)
            raise e
    
    def _read_json_safe(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Safely read JSON file with error handling"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            # File might be corrupted or being written
            return None
        return None
    
    def watch_for_updates(self, session_id: str, callback_fn):
        """Watch for updates relevant to a session (tasks, messages, events)"""
        # This would typically use filesystem watching (watchdog library)
        # For now, simple polling implementation
        def poll_updates():
            last_check = datetime.now()
            
            while True:
                # Check for new tasks
                pending_tasks = self.get_tasks_for_session(session_id, TaskStatus.PENDING)
                for task in pending_tasks:
                    if datetime.fromisoformat(task['created_at']) > last_check:
                        callback_fn('new_task', task)
                
                # Check for new messages
                messages = self.get_unread_messages(session_id)
                for msg in messages:
                    if datetime.fromisoformat(msg['created_at']) > last_check:
                        callback_fn('new_message', msg)
                
                # Check for events
                if self.events_dir.exists():
                    for event_file in self.events_dir.glob("*.json"):
                        event = self._read_json_safe(event_file)
                        if event and datetime.fromisoformat(event['created_at']) > last_check:
                            if event.get('broadcast') or session_id in str(event.get('data', {})):
                                callback_fn('event', event)
                
                last_check = datetime.now()
                time.sleep(2)  # Poll every 2 seconds
        
        # Run in background thread
        thread = threading.Thread(target=poll_updates, daemon=True)
        thread.start()
        return thread