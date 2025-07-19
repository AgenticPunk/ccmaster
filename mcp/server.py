"""
MCP Server Implementation for CCMaster

Provides MCP server functionality to expose CCMaster's session management
capabilities to Claude Code sessions and external clients.
"""

import json
import socket
import threading
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from .protocol import MCPProtocol, MCPMessage, MCPResponse
from .tools import SessionTools


class MCPServerHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP server"""
    
    def __init__(self, mcp_server, *args, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests (MCP messages)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Process MCP message
            response = self.mcp_server.handle_message(post_data.decode('utf-8'))
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to suppress HTTP request logs"""
        # Suppress verbose HTTP logs to keep output clean
        # These logs would show "POST / HTTP/1.1" 200 - which adds noise
        pass


class MCPServer:
    """MCP Server for CCMaster"""
    
    def __init__(self, ccmaster_instance, host='localhost', port=8080):
        self.ccmaster = ccmaster_instance
        self.host = host
        self.port = port
        self.protocol = MCPProtocol()
        self.session_tools = SessionTools(ccmaster_instance)
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Setup logging with custom handler for thread-safe printing
        self.logger = logging.getLogger('CCMaster.MCP')
        self.logger.setLevel(logging.INFO)
        
        # Remove default handlers to prevent duplicate output
        self.logger.handlers = []
        
        # Add custom handler that uses thread-safe printing
        class ThreadSafeMCPHandler(logging.Handler):
            def __init__(self, ccmaster):
                super().__init__()
                self.ccmaster = ccmaster
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    # Only show important messages, filter out HTTP requests
                    if "HTTP/1.1" not in msg and "POST /" not in msg:
                        # Use ccmaster's cli_log for proper alignment
                        if hasattr(self.ccmaster, 'cli_log'):
                            self.ccmaster.cli_log(f"MCP: {msg}", log_type='info')
                        else:
                            # Fallback only if cli_log not available
                            if hasattr(self.ccmaster, 'print_lock'):
                                with self.ccmaster.print_lock:
                                    timestamp = time.strftime('%H:%M:%S')
                                    print(f"[{timestamp}] ◆ MCP: {msg}")
                except Exception:
                    self.handleError(record)
        
        handler = ThreadSafeMCPHandler(self.ccmaster)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.propagate = False  # Prevent propagation to root logger
        
        # Register tools
        self.tools = {}
        self.register_tools()
        
        # Client connections
        self.clients = {}
    
    def register_tools(self):
        """Register all available tools"""
        for tool_name, tool_func in self.session_tools.tools.items():
            self.tools[tool_name] = tool_func
        
        # Update protocol capabilities
        self.protocol.capabilities["tools"] = {
            "listChanged": True
        }
    
    def start(self):
        """Start the MCP server"""
        try:
            def handler_factory(*args, **kwargs):
                return MCPServerHandler(self, *args, **kwargs)
            
            self.server = HTTPServer((self.host, self.port), handler_factory)
            self.running = True
            
            self.logger.info(f"Starting MCP server on {self.host}:{self.port}")
            
            # Start server in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def stop(self):
        """Stop the MCP server"""
        if self.server:
            self.logger.info("Stopping MCP server")
            self.running = False
            self.server.shutdown()
            self.server.server_close()
            
            if self.server_thread:
                self.server_thread.join(timeout=5)
    
    def handle_message(self, message_data: str) -> str:
        """Handle incoming MCP message"""
        try:
            # Parse message
            message = self.protocol.parse_message(message_data)
            
            if not self.protocol.validate_message(message):
                error_response = self.protocol.create_error_response(
                    message.get('id', 'unknown'), -32600, "Invalid Request"
                )
                return error_response.to_json()
            
            method = message.get('method')
            params = message.get('params', {})
            message_id = message.get('id')
            
            # Handle different methods
            if method == 'initialize':
                return self.handle_initialize(message_id, params)
            elif method == 'tools/list':
                return self.handle_tools_list(message_id)
            elif method == 'tools/call':
                return self.handle_tool_call(message_id, params)
            elif method == 'resources/list':
                return self.handle_resources_list(message_id)
            elif method == 'resources/read':
                return self.handle_resource_read(message_id, params)
            else:
                error_response = self.protocol.create_error_response(
                    message_id, -32601, f"Method not found: {method}"
                )
                return error_response.to_json()
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            error_response = self.protocol.create_error_response(
                'unknown', -32603, f"Internal error: {str(e)}"
            )
            return error_response.to_json()
    
    def handle_initialize(self, message_id: str, params: Dict[str, Any]) -> str:
        """Handle initialization request"""
        client_info = params.get('clientInfo', {})
        client_id = f"{client_info.get('name', 'unknown')}_{len(self.clients)}"
        
        # Store client info
        self.clients[client_id] = {
            'info': client_info,
            'connected_at': time.time()
        }
        
        # Use standardized cli_log for client connection message
        if hasattr(self.ccmaster, 'cli_log'):
            self.ccmaster.cli_log(f"Client connected: {client_id}", log_type='info')
        else:
            self.logger.info(f"Client connected: {client_id}")
        
        response = self.protocol.create_initialize_response(message_id)
        return response.to_json()
    
    def handle_tools_list(self, message_id: str) -> str:
        """Handle tools list request"""
        tool_definitions = self.session_tools.get_tool_definitions()
        
        result = {
            "tools": tool_definitions
        }
        
        response = MCPResponse(message_id, result)
        return response.to_json()
    
    def handle_tool_call(self, message_id: str, params: Dict[str, Any]) -> str:
        """Handle tool call request"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name not in self.tools:
            error_response = self.protocol.create_error_response(
                message_id, -32601, f"Tool not found: {tool_name}"
            )
            return error_response.to_json()
        
        try:
            # Call the tool
            tool_func = self.tools[tool_name]
            result = tool_func(**arguments)
            
            # Format response
            content = [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
            
            response = self.protocol.create_tool_response(message_id, content)
            return response.to_json()
            
        except Exception as e:
            self.logger.error(f"Tool call error: {e}")
            error_response = self.protocol.create_error_response(
                message_id, -32603, f"Tool execution error: {str(e)}"
            )
            return error_response.to_json()
    
    def handle_resources_list(self, message_id: str) -> str:
        """Handle resources list request"""
        resources = [
            {
                "uri": "ccmaster://sessions",
                "name": "Active Sessions",
                "description": "List of all active Claude Code sessions",
                "mimeType": "application/json"
            },
            {
                "uri": "ccmaster://status",
                "name": "System Status",
                "description": "CCMaster system status and metrics",
                "mimeType": "application/json"
            }
        ]
        
        result = {
            "resources": resources
        }
        
        response = MCPResponse(message_id, result)
        return response.to_json()
    
    def handle_resource_read(self, message_id: str, params: Dict[str, Any]) -> str:
        """Handle resource read request"""
        uri = params.get('uri')
        
        if uri == "ccmaster://sessions":
            # Return session data
            sessions_data = self.session_tools.list_sessions(include_ended=True)
            content = [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(sessions_data, indent=2)
                }
            ]
        elif uri == "ccmaster://status":
            # Return system status
            status_data = {
                "server_info": self.protocol.server_info,
                "active_sessions": len(self.ccmaster.active_sessions),
                "total_sessions": len(self.ccmaster.sessions),
                "connected_clients": len(self.clients),
                "uptime": time.time() - getattr(self, 'start_time', time.time())
            }
            content = [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(status_data, indent=2)
                }
            ]
        else:
            error_response = self.protocol.create_error_response(
                message_id, -32602, f"Resource not found: {uri}"
            )
            return error_response.to_json()
        
        result = {
            "contents": content
        }
        
        response = MCPResponse(message_id, result)
        return response.to_json()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "host": self.host,
            "port": self.port,
            "running": self.running,
            "connected_clients": len(self.clients),
            "available_tools": list(self.tools.keys())
        }