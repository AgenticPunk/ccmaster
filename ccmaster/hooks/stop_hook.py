#!/usr/bin/env python3
"""
Stop hook for CCMaster
Reports when Claude finishes responding completely
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from hook_utils import HookUtils

def main():
    # Always allow even if no session ID
    if len(sys.argv) < 2:
        print(json.dumps({"allow": True}))
        sys.exit(0)
    
    session_id = sys.argv[1]
    
    utils = HookUtils(session_id)
    
    # Read hook input
    data = utils.read_hook_input()
    
    # Update status to idle when Claude stops
    utils.update_status('idle', action='Response complete')
    
    # Output must be valid JSON with allow field
    # Always allow stop
    print(json.dumps({"allow": True}))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # On any error, allow the operation to continue
        from datetime import datetime
        error_log = Path.home() / '.ccmaster' / 'hook_errors.log'
        with open(error_log, 'a') as f:
            f.write(f"\n[{datetime.now()}] Stop Hook Error: {str(e)}\n")
        print(json.dumps({"allow": True}))
        sys.exit(0)