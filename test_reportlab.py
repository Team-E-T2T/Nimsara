from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

pdf_dir = Path('pdfs')
pdf_dir.mkdir(exist_ok=True)
pdf_path = pdf_dir / 'test-reportlab.pdf'

c = canvas.Canvas(str(pdf_path), pagesize=letter)
c.drawString(100, 750, 'Test PDF Created Successfully!')
c.drawString(100, 730, f'Generated: {datetime.now()}')
c.save()

print(f'PDF created: {pdf_path.exists()}')
print(f'PDF size: {pdf_path.stat().st_size} bytes')
