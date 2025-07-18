#!/usr/bin/env python3
"""
Simple test script for CCMaster MCP implementation (no external dependencies)
"""

import sys
import json
import time
from pathlib import Path

def test_mcp_basic():
    """Test basic MCP functionality"""
    print("🧪 Testing CCMaster MCP Implementation")
    print("=" * 50)
    
    # Test 1: Check if we can import the modules
    print("1. Testing module imports...")
    try:
        from .protocol import MCPProtocol
        from .server import MCPServer
        from .client import MCPClient
        from .tools import SessionTools
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Test protocol functionality
    print("\n2. Testing MCP protocol...")
    protocol = MCPProtocol()
    
    # Test message creation
    msg = protocol.create_initialize_message({"name": "test", "version": "1.0"})
    print(f"✅ Created initialize message: {msg.method}")
    
    # Test message parsing
    msg_dict = msg.to_dict()
    parsed = protocol.parse_message(json.dumps(msg_dict))
    print(f"✅ Parsed message: {parsed['method']}")
    
    # Test 3: Test client creation
    print("\n3. Testing MCP client...")
    client = MCPClient("test-client", "1.0.0")
    print(f"✅ Created client: {client.client_name}")
    
    # Test 4: Test SessionTools
    print("\n4. Testing SessionTools...")
    
    # Create a mock CCMaster instance
    class MockCCMaster:
        def __init__(self):
            self.sessions = {}
            self.active_sessions = {}
            self.current_status = {}
            self.watch_modes = {}
            self.auto_continue_counts = {}
            self.max_turns = {}
            self.logs_dir = Path("/tmp/ccmaster_test")
            self.logs_dir.mkdir(exist_ok=True)
        
        def create_session(self, working_dir):
            session_id = f"test_session_{int(time.time())}"
            self.sessions[session_id] = {
                'working_dir': working_dir,
                'status': 'active',
                'created_at': time.time()
            }
            return session_id
        
        def save_sessions(self):
            pass
        
        def find_claude_pid_for_session(self, session_id, created_at):
            return None
        
        def send_continue_to_claude(self, session_id, message="continue"):
            return True
    
    mock_cc = MockCCMaster()
    
    # Test SessionTools
    session_tools = SessionTools(mock_cc)
    tool_definitions = session_tools.get_tool_definitions()
    print(f"✅ SessionTools created with {len(tool_definitions)} tools")
    
    # Test tool execution
    result = session_tools.list_sessions()
    print(f"✅ list_sessions returned: {result}")
    
    # Test 5: Test MCP server creation
    print("\n5. Testing MCP server...")
    try:
        # Use a different port for testing
        server = MCPServer(mock_cc, 'localhost', 8081)
        print("✅ MCP server created successfully")
        
        # Test server info
        server_info = server.get_server_info()
        print(f"✅ Server info: {server_info}")
        
    except Exception as e:
        print(f"❌ Server creation error: {e}")
        return False
    
    print("\n🎉 All tests passed! MCP implementation is working correctly.")
    print("\nNext steps:")
    print("1. Start CCMaster: ccmaster watch")
    print("2. The MCP server will start automatically on localhost:8080")
    print("3. Use claude_client.py to interact with sessions")
    
    return True

if __name__ == '__main__':
    success = test_mcp_basic()
    sys.exit(0 if success else 1)