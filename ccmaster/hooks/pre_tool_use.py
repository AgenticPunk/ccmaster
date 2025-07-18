#!/usr/bin/env python3
"""
Pre-tool-use hook for CCMaster
Reports when Claude Code is about to use a tool
"""

import sys
import json
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent))
from hook_utils import HookUtils

def main():
    # Debug mode - write errors to file
    error_log = Path.home() / '.ccmaster' / 'hook_errors.log'
    
    try:
        if len(sys.argv) < 2:
            with open(error_log, 'a') as f:
                f.write(f"\n[{datetime.now()}] PreToolUse: No session ID provided\n")
            print(json.dumps({"allow": True}))
            sys.exit(0)
    
        session_id = sys.argv[1]
        
        utils = HookUtils(session_id)
        
        # Read hook input
        data = utils.read_hook_input()
        
        # Extract tool name from hook data
        # According to docs, PreToolUse gets: tool_name field directly
        tool_name = data.get('tool_name', 'unknown')
        
        # Update status to working
        utils.update_status('working', tool=tool_name, action=f'Using {tool_name}')
        
        # Output must be valid JSON with allow field
        # Always allow tool use
        print(json.dumps({"allow": True}))
        
    except Exception as e:
        # On any error, log it and allow operation
        with open(error_log, 'a') as f:
            f.write(f"\n[{datetime.now()}] PreToolUse Error: {str(e)}\n")
        print(json.dumps({"allow": True}))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # On any error, allow the operation to continue
        error_log = Path.home() / '.ccmaster' / 'hook_errors.log'
        with open(error_log, 'a') as f:
            f.write(f"\n[{datetime.now()}] PreToolUse Error: {str(e)}\n")
        print(json.dumps({"allow": True}))
        sys.exit(0)