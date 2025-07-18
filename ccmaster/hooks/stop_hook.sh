#!/usr/bin/env bash
# Wrapper script for Claude Code compatibility
exec /usr/bin/env python3 "$(dirname "$0")/stop_hook.py" "$@"