#!/usr/bin/env python3
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

# Test imports
try:
    import weasyprint
    print("✓ weasyprint available")
except (ImportError, OSError) as e:
    print(f"✗ weasyprint not available: {type(e).__name__}")

try:
    from xhtml2pdf import pisa
    print("✓ xhtml2pdf available")
except ImportError:
    print("✗ xhtml2pdf not available")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    print("✓ reportlab available")
except ImportError:
    print("✗ reportlab not available")

# Test reportlab PDF creation
print("\n--- Testing reportlab PDF creation ---")
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

pdf_dir = Path("pdfs")
pdf_dir.mkdir(exist_ok=True)
pdf_path = pdf_dir / "test-from-mcp-server.pdf"

c = canvas.Canvas(str(pdf_path), pagesize=letter)
c.drawString(100, 750, "PDF converted from: test.html")
c.drawString(100, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
c.save()

print(f"PDF created: {pdf_path.exists()}")
print(f"PDF size: {pdf_path.stat().st_size} bytes")
