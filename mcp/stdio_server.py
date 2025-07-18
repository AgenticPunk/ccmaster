#!/usr/bin/env python3
"""
CCMaster MCP STDIO Server

This is a wrapper that allows CCMaster MCP server to be used as a stdio-based
MCP server by Claude Code. It acts as a bridge between stdio and the HTTP-based
CCMaster MCP server.
"""

import sys
import json
import argparse
import logging
import threading
import time
from typing import Dict, Any, Optional

# Delay requests import to allow --help to work without it
requests = None


class StdioMCPBridge:
    """Bridge between stdio MCP and HTTP MCP server"""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.server_url = f"http://{host}:{port}"
        self.running = True
        
        # Setup logging to stderr (stdout is reserved for MCP messages)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
        self.logger = logging.getLogger('CCMaster.MCP.StdioBridge')
        
        # Session for HTTP requests
        self.session = requests.Session()
        
    def send_to_server(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to HTTP MCP server"""
        try:
            response = self.session.post(
                self.server_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Cannot connect to CCMaster MCP server at {self.server_url}")
            self.logger.error("Make sure CCMaster is running with 'ccmaster watch'")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id", "unknown"),
                "error": {
                    "code": -32603,
                    "message": f"Cannot connect to CCMaster MCP server at {self.server_url}. Make sure CCMaster is running."
                }
            }
        except Exception as e:
            self.logger.error(f"Error communicating with server: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id", "unknown"),
                "error": {
                    "code": -32603,
                    "message": f"Server communication error: {str(e)}"
                }
            }
    
    def send_response(self, response: Dict[str, Any]):
        """Send response to stdout"""
        try:
            # Write response to stdout with newline
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
    
    def handle_message(self, line: str):
        """Handle a single message from stdin"""
        try:
            # Parse the JSON-RPC message
            message = json.loads(line)
            
            # Log the incoming message (to stderr)
            self.logger.debug(f"Received: {message.get('method', 'unknown')}")
            
            # Forward to HTTP server
            response = self.send_to_server(message)
            
            # Send response back via stdout
            if response:
                self.send_response(response)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON received: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON"
                }
            }
            self.send_response(error_response)
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            self.send_response(error_response)
    
    def run(self):
        """Main loop - read from stdin and process messages"""
        self.logger.info(f"Starting CCMaster MCP STDIO bridge to {self.server_url}")
        
        # Send a test connection to verify server is running
        test_response = self.send_to_server({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "test"
        })
        
        if test_response and not test_response.get("error"):
            self.logger.info("Successfully connected to CCMaster MCP server")
        else:
            self.logger.warning("CCMaster MCP server may not be running")
        
        try:
            while self.running:
                # Read line from stdin
                line = sys.stdin.readline()
                
                if not line:  # EOF
                    break
                
                line = line.strip()
                if not line:  # Empty line
                    continue
                
                # Handle the message
                self.handle_message(line)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down STDIO bridge")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.running = False
            self.session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CCMaster MCP STDIO Server Bridge')
    parser.add_argument('--host', default='localhost', help='CCMaster MCP server host')
    parser.add_argument('--port', type=int, default=8080, help='CCMaster MCP server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Check for requests module when actually running (not just --help)
    global requests
    try:
        import requests as req
        requests = req
    except ImportError:
        print("ERROR: requests module required for MCP stdio server", file=sys.stderr)
        print("Install with: pip install requests", file=sys.stderr)
        sys.exit(1)
    
    # Set debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run the bridge
    bridge = StdioMCPBridge(args.host, args.port)
    bridge.run()


if __name__ == '__main__':
    main()