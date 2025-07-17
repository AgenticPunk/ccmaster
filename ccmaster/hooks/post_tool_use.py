#!/usr/bin/env python3
"""
Post-tool-use hook for CCMaster
Reports when Claude Code has finished using a tool
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
    
    # Extract tool name
    tool_name = data.get('tool', {}).get('name', 'unknown')
    
    # Don't update status on PostToolUse - let other hooks handle idle detection
    # utils.update_status('completed_tool', tool=tool_name, action=f'Finished {tool_name}')
    
    # Output must be valid JSON
    print(json.dumps({"status": "ok"}))

if __name__ == '__main__':
    main()