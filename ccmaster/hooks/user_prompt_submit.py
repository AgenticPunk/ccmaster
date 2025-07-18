#!/usr/bin/env python3
"""
User-prompt-submit hook for CCMaster
Reports when user submits a new prompt
"""

import sys
import json
from pathlib import Path
from datetime import datetime
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
    
    # Debug: log the entire data structure
    debug_file = Path.home() / '.ccmaster' / 'user_prompt_debug.log'
    with open(debug_file, 'a') as f:
        f.write(f"\n--- UserPromptSubmit Hook ---\n")
        f.write(f"Session: {session_id}\n")
        f.write(f"Data keys: {list(data.keys())}\n")
        f.write(f"Full data: {json.dumps(data, indent=2)}\n")
    
    # Extract user prompt from hook data
    # The prompt is in the 'input' field for UserPromptSubmit
    user_prompt = data.get('input', data.get('prompt', ''))
    
    # Log the user input to a separate file
    prompt_log_file = Path.home() / '.ccmaster' / 'logs' / f'{session_id}_prompts.log'
    prompt_log_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(prompt_log_file, 'a') as f:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt': user_prompt
        }
        f.write(json.dumps(log_entry) + '\n')
    
    # Update status to processing with the prompt
    status_data = {
        'state': 'processing',
        'timestamp': datetime.now().isoformat(),
        'prompt': user_prompt,
        'current_action': 'Processing user prompt'
    }
    
    # Save status directly
    status_file = Path.home() / '.ccmaster' / 'status' / f'{session_id}.json'
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    # Output must be valid JSON with allow field
    # Always allow user prompts
    print(json.dumps({"allow": True}))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # On any error, allow the operation to continue
        error_log = Path.home() / '.ccmaster' / 'hook_errors.log'
        with open(error_log, 'a') as f:
            f.write(f"\n[{datetime.now()}] UserPromptSubmit Error: {str(e)}\n")
        print(json.dumps({"allow": True}))
        sys.exit(0)