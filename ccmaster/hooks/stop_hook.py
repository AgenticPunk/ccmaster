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
    if len(sys.argv) < 2:
        sys.exit(1)
    
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
    main()