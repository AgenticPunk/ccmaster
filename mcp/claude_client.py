#!/usr/bin/env python3
"""
CCMaster MCP Client for Claude Code Sessions

This script provides a simple command-line interface for Claude Code sessions
to interact with the CCMaster MCP server.

Usage:
    python claude_client.py list-sessions
    python claude_client.py send-message SESSION_ID "Hello from another session"
    python claude_client.py create-session /path/to/working/dir
    python claude_client.py spawn-temp "ls -la"
"""

import sys
import argparse
import json
from client import CCMasterMCPClient


def main():
    parser = argparse.ArgumentParser(description='CCMaster MCP Client for Claude Code Sessions')
    parser.add_argument('--host', default='localhost', help='CCMaster MCP server host')
    parser.add_argument('--port', type=int, default=8080, help='CCMaster MCP server port')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List sessions
    list_parser = subparsers.add_parser('list-sessions', help='List all sessions')
    list_parser.add_argument('--include-ended', action='store_true', help='Include ended sessions')
    
    # Get session status
    status_parser = subparsers.add_parser('status', help='Get session status')
    status_parser.add_argument('session_id', help='Session ID')
    
    # Send message
    send_parser = subparsers.add_parser('send-message', help='Send message to session')
    send_parser.add_argument('session_id', help='Target session ID')
    send_parser.add_argument('message', help='Message to send')
    send_parser.add_argument('--wait', action='store_true', help='Wait for response')
    
    # Create session
    create_parser = subparsers.add_parser('create-session', help='Create new session')
    create_parser.add_argument('working_dir', nargs='?', help='Working directory')
    create_parser.add_argument('--no-watch', action='store_true', help='Disable watch mode')
    create_parser.add_argument('--max-turns', type=int, help='Maximum auto-continue turns')
    
    # Kill session
    kill_parser = subparsers.add_parser('kill-session', help='Kill a session')
    kill_parser.add_argument('session_id', help='Session ID to kill')
    
    # Spawn temp session
    temp_parser = subparsers.add_parser('spawn-temp', help='Spawn temporary session')
    temp_parser.add_argument('command', help='Command to execute')
    temp_parser.add_argument('--working-dir', help='Working directory')
    temp_parser.add_argument('--timeout', type=int, default=60, help='Timeout in seconds')
    
    # Coordinate sessions
    coord_parser = subparsers.add_parser('coordinate', help='Coordinate multiple sessions')
    coord_parser.add_argument('task_description', help='Task description')
    coord_parser.add_argument('assignments', help='JSON string of session assignments')
    
    # Get logs
    logs_parser = subparsers.add_parser('logs', help='Get session logs')
    logs_parser.add_argument('session_id', help='Session ID')
    logs_parser.add_argument('--lines', type=int, default=100, help='Number of lines to get')
    
    # System status
    sys_parser = subparsers.add_parser('system-status', help='Get system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create client and connect
    client = CCMasterMCPClient(args.host, args.port)
    
    if not client.connect():
        print("❌ Failed to connect to CCMaster MCP server")
        print(f"   Make sure CCMaster is running with MCP server on {args.host}:{args.port}")
        sys.exit(1)
    
    try:
        # Execute command
        if args.command == 'list-sessions':
            result = client.list_sessions(args.include_ended)
            print_result(result)
        
        elif args.command == 'status':
            result = client.get_session_status(args.session_id)
            print_result(result)
        
        elif args.command == 'send-message':
            result = client.send_message_to_session(args.session_id, args.message, args.wait)
            print_result(result)
        
        elif args.command == 'create-session':
            result = client.create_session(args.working_dir, not args.no_watch, args.max_turns)
            print_result(result)
        
        elif args.command == 'kill-session':
            result = client.kill_session(args.session_id)
            print_result(result)
        
        elif args.command == 'spawn-temp':
            result = client.spawn_temp_session(args.command, args.working_dir, args.timeout)
            print_result(result)
        
        elif args.command == 'coordinate':
            try:
                assignments = json.loads(args.assignments)
                result = client.coordinate_sessions(args.task_description, assignments)
                print_result(result)
            except json.JSONDecodeError:
                print("❌ Invalid JSON for assignments")
                sys.exit(1)
        
        elif args.command == 'logs':
            result = client.get_session_logs(args.session_id, args.lines)
            print_result(result)
        
        elif args.command == 'system-status':
            result = client.get_system_status()
            print_result(result)
        
    finally:
        client.disconnect()


def print_result(result):
    """Print result in a formatted way"""
    if result is None:
        print("❌ No response from server")
        return
    
    if isinstance(result, dict):
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        elif result.get('success'):
            print("✅ Success")
            # Print additional info if available
            for key, value in result.items():
                if key not in ['success', 'error']:
                    print(f"   {key}: {value}")
        else:
            # Pretty print JSON
            print(json.dumps(result, indent=2))
    else:
        print(result)


if __name__ == '__main__':
    main()