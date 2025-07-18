"""
MCP Protocol Implementation

Handles JSON-RPC 2.0 protocol for Model Context Protocol communication.
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime


class MCPMessage:
    """Base class for MCP messages"""
    
    def __init__(self, method: str, params: Optional[Dict[str, Any]] = None, id: Optional[str] = None):
        self.jsonrpc = "2.0"
        self.method = method
        self.params = params or {}
        self.id = id or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        msg = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id
        }
        return msg
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())


class MCPResponse:
    """MCP response message"""
    
    def __init__(self, id: str, result: Any = None, error: Optional[Dict[str, Any]] = None):
        self.jsonrpc = "2.0"
        self.id = id
        self.result = result
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        msg = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error:
            msg["error"] = self.error
        else:
            msg["result"] = self.result
        return msg
    
    def to_json(self) -> str:
        """Convert response to JSON string"""
        return json.dumps(self.to_dict())


class MCPProtocol:
    """MCP Protocol handler"""
    
    def __init__(self):
        self.version = "2024-11-05"
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {},
            "logging": {}
        }
        self.server_info = {
            "name": "ccmaster",
            "version": "1.0.0"
        }
    
    def create_initialize_message(self, client_info: Dict[str, Any]) -> MCPMessage:
        """Create initialization message"""
        params = {
            "protocolVersion": self.version,
            "capabilities": self.capabilities,
            "clientInfo": client_info
        }
        return MCPMessage("initialize", params)
    
    def create_initialize_response(self, message_id: str) -> MCPResponse:
        """Create initialization response"""
        result = {
            "protocolVersion": self.version,
            "capabilities": self.capabilities,
            "serverInfo": self.server_info
        }
        return MCPResponse(message_id, result)
    
    def create_tool_call_message(self, tool_name: str, arguments: Dict[str, Any]) -> MCPMessage:
        """Create tool call message"""
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        return MCPMessage("tools/call", params)
    
    def create_tool_response(self, message_id: str, content: List[Dict[str, Any]]) -> MCPResponse:
        """Create tool response"""
        result = {
            "content": content,
            "isError": False
        }
        return MCPResponse(message_id, result)
    
    def create_error_response(self, message_id: str, code: int, message: str) -> MCPResponse:
        """Create error response"""
        error = {
            "code": code,
            "message": message
        }
        return MCPResponse(message_id, error=error)
    
    def parse_message(self, data: str) -> Dict[str, Any]:
        """Parse JSON-RPC message"""
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate JSON-RPC message format"""
        required_fields = ["jsonrpc", "method", "id"]
        return all(field in message for field in required_fields) and message["jsonrpc"] == "2.0"