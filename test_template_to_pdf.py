#!/usr/bin/env python3
"""Test the template_to_pdf functionality"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

# Import the MCP server
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_server", "mcp-server.py")
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)

MCPServer = mcp_module.MCPServer

async def test_template_to_pdf():
    """Test template rendering and PDF conversion"""
    server = MCPServer()
    
    # Test data for invoice
    template_data = {
        "invoice_number": "INV-2026-001",
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "customer_address": "123 Main St, Anytown, USA",
        "items": [
            {
                "description": "Web Development Service",
                "quantity": 10,
                "unit_price": 150.00
            },
            {
                "description": "UI/UX Design",
                "quantity": 5,
                "unit_price": 120.00
            },
            {
                "description": "Technical Support",
                "quantity": 20,
                "unit_price": 50.00
            }
        ],
        "total_amount": 3200.00,
        "due_date": "2026-04-24"
    }
    
    print("=== Testing template_to_pdf ===")
    print(f"Template: invoice_template.html")
    print(f"Data keys: {list(template_data.keys())}")
    
    result = await server.template_to_pdf("invoice_template.html", template_data)
    print(f"\nResult: {json.dumps(result, indent=2)}")
    
    # Verify PDF was created
    print("\n=== Verifying PDF ===")
    pdfs = sorted(Path("pdfs").glob("invoice_template-*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if pdfs:
        latest_pdf = pdfs[0]
        print(f"✓ PDF created: {latest_pdf.name}")
        print(f"✓ Size: {latest_pdf.stat().st_size} bytes")
    else:
        print("✗ No PDF files found")

if __name__ == "__main__":
    asyncio.run(test_template_to_pdf())
