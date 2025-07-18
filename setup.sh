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
echo "  ccmaster version             - Show version information"