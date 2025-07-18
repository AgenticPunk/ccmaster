"""
MCP Client Implementation for CCMaster

Provides MCP client functionality to connect to external MCP servers
and the CCMaster MCP server from Claude Code sessions.
"""

import json
try:
    import requests
except ImportError:
    requests = None
import subprocess
import sys
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from .protocol import MCPProtocol, MCPMessage, MCPResponse


class MCPClient:
    """MCP Client for connecting to MCP servers"""
    
    def __init__(self, client_name: str = "ccmaster-client", client_version: str = "1.0.0"):
        self.client_name = client_name
        self.client_version = client_version
        self.protocol = MCPProtocol()
        self.server_url = None
        self.initialized = False
        self.session = requests.Session() if requests else None
        
        # Setup logging
        self.logger = logging.getLogger(f'CCMaster.MCP.Client.{client_name}')
        self.logger.setLevel(logging.INFO)
        
        # Server capabilities
        self.server_capabilities = {}
        self.available_tools = []
        self.available_resources = []
    
    def connect(self, server_url: str) -> bool:
        """Connect to MCP server"""
        if requests is None:
            self.logger.error("requests module not available. Install with: pip install requests")
            return False
            
        try:
            self.server_url = server_url
            
            # Create initialization message
            client_info = {
                "name": self.client_name,
                "version": self.client_version
            }
            
            init_message = self.protocol.create_initialize_message(client_info)
            
            # Send initialization
            response = self._send_message(init_message)
            
            if response and response.get('result'):
                self.server_capabilities = response['result'].get('capabilities', {})
                self.initialized = True
                self.logger.info(f"Connected to MCP server: {server_url}")
                
                # Load available tools and resources
                self._load_server_capabilities()
                return True
            else:
                self.logger.error(f"Failed to initialize connection to {server_url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MCP server"""
        self.initialized = False
        self.server_url = None
        if self.session:
            self.session.close()
    
    def _send_message(self, message: MCPMessage) -> Optional[Dict[str, Any]]:
        """Send message to MCP server"""
        try:
            if not self.server_url:
                return None
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = self.session.post(
                self.server_url,
                data=message.to_json(),
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Message send error: {e}")
            return None
    
    def _load_server_capabilities(self):
        """Load available tools and resources from server"""
        if not self.initialized:
            return
        
        # Get available tools
        tools_message = MCPMessage("tools/list")
        tools_response = self._send_message(tools_message)
        
        if tools_response and tools_response.get('result'):
            self.available_tools = tools_response['result'].get('tools', [])
            self.logger.info(f"Loaded {len(self.available_tools)} tools")
        
        # Get available resources
        resources_message = MCPMessage("resources/list")
        resources_response = self._send_message(resources_message)
        
        if resources_response and resources_response.get('result'):
            self.available_resources = resources_response['result'].get('resources', [])
            self.logger.info(f"Loaded {len(self.available_resources)} resources")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return self.available_tools
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        return self.available_resources
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool on the MCP server"""
        if not self.initialized:
            self.logger.error("Client not connected to server")
            return None
        
        try:
            # Create tool call message
            tool_message = self.protocol.create_tool_call_message(tool_name, arguments)
            
            # Send message
            response = self._send_message(tool_message)
            
            if response and response.get('result'):
                return response['result']
            elif response and response.get('error'):
                self.logger.error(f"Tool call error: {response['error']}")
                return {"error": response['error']}
            else:
                self.logger.error("Invalid response from server")
                return None
                
        except Exception as e:
            self.logger.error(f"Tool call error: {e}")
            return None
    
    def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Read a resource from the MCP server"""
        if not self.initialized:
            self.logger.error("Client not connected to server")
            return None
        
        try:
            # Create resource read message
            params = {"uri": uri}
            resource_message = MCPMessage("resources/read", params)
            
            # Send message
            response = self._send_message(resource_message)
            
            if response and response.get('result'):
                return response['result']
            elif response and response.get('error'):
                self.logger.error(f"Resource read error: {response['error']}")
                return {"error": response['error']}
            else:
                self.logger.error("Invalid response from server")
                return None
                
        except Exception as e:
            self.logger.error(f"Resource read error: {e}")
            return None
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "client_name": self.client_name,
            "client_version": self.client_version,
            "server_url": self.server_url,
            "initialized": self.initialized,
            "server_capabilities": self.server_capabilities,
            "available_tools_count": len(self.available_tools),
            "available_resources_count": len(self.available_resources)
        }


class CCMasterMCPClient:
    """Specialized MCP client for connecting to CCMaster from Claude Code sessions"""
    
    def __init__(self, ccmaster_host: str = "localhost", ccmaster_port: int = 8080):
        self.ccmaster_host = ccmaster_host
        self.ccmaster_port = ccmaster_port
        self.client = MCPClient("claude-session", "1.0.0")
        self.server_url = f"http://{ccmaster_host}:{ccmaster_port}"
    
    def connect(self) -> bool:
        """Connect to CCMaster MCP server"""
        return self.client.connect(self.server_url)
    
    def disconnect(self):
        """Disconnect from CCMaster MCP server"""
        self.client.disconnect()
    
    def list_sessions(self, include_ended: bool = False) -> Optional[Dict[str, Any]]:
        """List all Claude Code sessions"""
        return self.client.call_tool("list_sessions", {"include_ended": include_ended})
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific session"""
        return self.client.call_tool("get_session_status", {"session_id": session_id})
    
    def send_message_to_session(self, session_id: str, message: str, wait_for_response: bool = False) -> Optional[Dict[str, Any]]:
        """Send message to another session"""
        return self.client.call_tool("send_message_to_session", {
            "session_id": session_id,
            "message": message,
            "wait_for_response": wait_for_response
        })
    
    def create_session(self, working_dir: str = None, watch_mode: bool = True, max_turns: int = None) -> Optional[Dict[str, Any]]:
        """Create a new Claude Code session"""
        params = {
            "watch_mode": watch_mode
        }
        if working_dir:
            params["working_dir"] = working_dir
        if max_turns:
            params["max_turns"] = max_turns
        
        return self.client.call_tool("create_session", params)
    
    def kill_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Kill a specific session"""
        return self.client.call_tool("kill_session", {"session_id": session_id})
    
    def spawn_temp_session(self, command: str, working_dir: str = None, timeout: int = 60) -> Optional[Dict[str, Any]]:
        """Spawn a temporary session to run a command"""
        params = {
            "command": command,
            "timeout": timeout
        }
        if working_dir:
            params["working_dir"] = working_dir
        
        return self.client.call_tool("spawn_temp_session", params)
    
    def coordinate_sessions(self, task_description: str, session_assignments: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Coordinate multiple sessions for a task"""
        return self.client.call_tool("coordinate_sessions", {
            "task_description": task_description,
            "session_assignments": session_assignments
        })
    
    def get_session_logs(self, session_id: str, lines: int = 100) -> Optional[Dict[str, Any]]:
        """Get logs from a specific session"""
        return self.client.call_tool("get_session_logs", {
            "session_id": session_id,
            "lines": lines
        })
    
    def get_system_status(self) -> Optional[Dict[str, Any]]:
        """Get CCMaster system status"""
        return self.client.read_resource("ccmaster://status")
    
    def get_all_sessions_data(self) -> Optional[Dict[str, Any]]:
        """Get all sessions data"""
        return self.client.read_resource("ccmaster://sessions")