# CCMaster Hooks

## Claude Code Hook Compatibility

If you see errors like "spawn /bin/sh ENOENT" when using CCMaster with Claude Code, this is because Claude Code's environment might not have access to standard shell paths.

## Solutions

### Option 1: Use bash wrappers (recommended)
The `.sh` wrapper scripts in this directory provide better compatibility with Claude Code's execution environment.

### Option 2: Direct Python execution
If the shell wrappers don't work, CCMaster will fall back to direct Python execution.

### Option 3: Disable hooks temporarily
If hooks are causing issues, you can disable them by:
1. Setting `"hooks_enabled": false` in `~/.ccmaster/config.json`
2. Or removing the hooks section from `~/.claude/settings.json`

## Troubleshooting

1. Check if Python is accessible:
   ```bash
   which python3
   ```

2. Test hook directly:
   ```bash
   python3 /path/to/ccmaster/hooks/stop_hook.py test_session
   ```

3. Check Claude Code settings:
   ```bash
   cat ~/.claude/settings.json | jq .hooks
   ```