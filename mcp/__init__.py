"""
CCMaster MCP (Model Context Protocol) Module

This module provides MCP server and client functionality for CCMaster,
enabling inter-session communication and coordination between Claude Code sessions.
"""

__version__ = "1.0.0"

from .server import MCPServer
from .client import MCPClient
from .tools import SessionTools
from .protocol import MCPProtocol

__all__ = ['MCPServer', 'MCPClient', 'SessionTools', 'MCPProtocol']