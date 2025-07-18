#!/bin/bash
# Setup script for CCMaster

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Read version from VERSION file
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")

echo "Setting up CCMaster v${VERSION}..."

# Create symlink in /usr/local/bin
if [ -w /usr/local/bin ]; then
    ln -sf "$SCRIPT_DIR/ccmaster/bin/ccmaster" /usr/local/bin/ccmaster
    echo "Created symlink: /usr/local/bin/ccmaster"
else
    echo "Cannot write to /usr/local/bin. You can:"
    echo "1. Run with sudo: sudo $0"
    echo "2. Add $SCRIPT_DIR/ccmaster/bin to your PATH manually"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"$SCRIPT_DIR/ccmaster/bin:\$PATH\""
fi

# Make sure hooks are executable
chmod +x "$SCRIPT_DIR/ccmaster/bin/ccmaster"
chmod +x "$SCRIPT_DIR/ccmaster/hooks"/*.py

# Initialize CCMaster config
CONFIG_DIR="$HOME/.ccmaster"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Create or update config file with required settings
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating initial configuration..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "claude_code_command": "claude",
  "monitor_interval": 0.5
}
EOF
else
    # Check if claude_code_command exists in config
    if ! grep -q "claude_code_command" "$CONFIG_FILE"; then
        echo "Updating configuration with missing claude_code_command..."
        # Create a backup
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
        # Add claude_code_command to existing config
        python3 -c "
import json
import sys
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    config['claude_code_command'] = 'claude'
    if 'monitor_interval' not in config:
        config['monitor_interval'] = 0.5
    with open('$CONFIG_FILE', 'w') as f:
        json.dump(config, f, indent=2)
    print('Configuration updated successfully')
except Exception as e:
    print(f'Error updating config: {e}', file=sys.stderr)
    sys.exit(1)
"
    fi
fi

# Check for Python dependencies
echo "Checking Python dependencies..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: 'requests' module not found"
    echo "   MCP integration requires the requests module."
    echo "   Install with: pip3 install requests"
    echo ""
fi

echo "CCMaster v${VERSION} setup complete!"
echo ""
echo "Usage:"
echo "  ccmaster start               - Start a new Claude Code session"
echo "  ccmaster watch               - Start in watch mode (auto-continue)"
echo "  ccmaster watch -d /path      - Watch mode in specific directory"
echo "  ccmaster watch --maxturn 10  - Limit auto-continues to 10 turns"
echo "  ccmaster watch --instances 2 - Start multiple Claude sessions"
echo "  ccmaster list                - List all sessions"
echo "  ccmaster logs SESSION        - View session logs"
echo "  ccmaster prompts SESSION     - View user prompts"
echo "  ccmaster mcp status          - Check MCP server status"
echo "  ccmaster mcp remove          - Remove CCMaster from project .mcp.json"
echo "  ccmaster version             - Show version information"
echo ""
echo "MCP Integration:"
echo "  When you run 'ccmaster watch', it will automatically:"
echo "  1. Find an available port (8080-8090) and start MCP server"
echo "  2. Create .mcp.json in your project directory with the correct port"
echo "  3. Claude Code will detect it and enable MCP tools"
echo "  4. Use tools like: /mcp__ccmaster__list_sessions"
echo ""
echo "Note: MCP server uses dynamic port allocation to avoid conflicts"