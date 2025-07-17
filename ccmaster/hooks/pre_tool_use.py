#!/usr/bin/env python3
"""
Pre-tool-use hook for CCMaster
Reports when Claude Code is about to use a tool
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from hook_utils import HookUtils

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    session_id = sys.argv[1]
    
    utils = HookUtils(session_id)
    
    # Read hook input
    data = utils.read_hook_input()
    
    # Extract tool name from hook data
    # According to docs, PreToolUse gets: tool_name field directly
    tool_name = data.get('tool_name', 'unknown')
    
    # Update status to working
    utils.update_status('working', tool=tool_name, action=f'Using {tool_name}')
    
    # Output must be valid JSON
    print(json.dumps({"status": "ok"}))

if __name__ == '__main__':
    main()