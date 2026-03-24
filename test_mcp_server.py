import asyncio
import sys
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import MCPServer

async def test():
    server = MCPServer()
    test_html = Path("test.html")
    
    if not test_html.exists():
        print("Error: test.html not found")
        return
    
    result = await server.convert_html_to_pdf(str(test_html))
    print("Result:", result)
    
    # Check if PDF was created
    pdfs = list(Path("pdfs").glob("test-*.pdf"))
    if pdfs:
        print(f"\nPDF created: {pdfs[-1]}")
        print(f"Size: {pdfs[-1].stat().st_size} bytes")
    else:
        print("\nNo PDF created")

if __name__ == "__main__":
    asyncio.run(test())
