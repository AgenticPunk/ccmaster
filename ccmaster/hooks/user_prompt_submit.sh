#!/usr/bin/env bash
# Wrapper script for Claude Code compatibility
exec /usr/bin/env python3 "$(dirname "$0")/user_prompt_submit.py" "$@"