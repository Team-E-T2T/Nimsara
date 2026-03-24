#!/usr/bin/env python3
"""Test the MCP server with simulated Claude Desktop requests"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

# We need to manually load the MCPServer class since the file has a hyphen
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_server", "mcp-server.py")
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)

MCPServer = mcp_module.MCPServer

async def test_mcp_server():
    """Test the MCP server"""
    server = MCPServer()
    
    # Test 1: List tools
    print("=== Test 1: List Tools ===")
    response = await server.handle_list_tools({})
    print(f"Tools available: {len(response['tools'])} tool(s)")
    print(f"Tool name: {response['tools'][0]['name']}")
    
    # Test 2: Convert test.html to PDF
    print("\n=== Test 2: Convert HTML to PDF ===")
    test_html_path = str(Path("test.html").resolve())
    print(f"Converting: {test_html_path}")
    
    response = await server.convert_html_to_pdf(test_html_path)
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 3: Verify PDF was created
    print("\n=== Test 3: Verify PDF ===")
    pdfs = sorted(Path("pdfs").glob("test-*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if pdfs:
        latest_pdf = pdfs[0]
        print(f"Latest PDF: {latest_pdf.name}")
        print(f"Size: {latest_pdf.stat().st_size} bytes")
        print(f"✓ PDF successfully created!")
    else:
        print("✗ No PDF files found")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
