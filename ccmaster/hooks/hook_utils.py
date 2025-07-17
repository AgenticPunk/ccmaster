#!/usr/bin/env python3
"""
Shared utilities for CCMaster hooks
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class HookUtils:
    def __init__(self, session_id):
        self.session_id = session_id
        # Use session-specific status file to avoid conflicts
        self.status_dir = Path.home() / '.ccmaster' / 'status'
        self.status_dir.mkdir(exist_ok=True, parents=True)
        self.status_file = self.status_dir / f'{session_id}.json'
    
    def update_status(self, state, tool=None, action=None):
        """Update session status"""
        # Create status data for this session
        status_data = {
            'state': state,
            'timestamp': datetime.now().isoformat(),
            'last_tool': tool,
            'current_action': action
        }
        
        # Save status to session-specific file
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def read_hook_input(self):
        """Read input from stdin for hooks"""
        try:
            return json.load(sys.stdin)
        except:
            return {}