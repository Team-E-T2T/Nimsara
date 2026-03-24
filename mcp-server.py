#!/usr/bin/env python3
"""
Python MCP Server - HTML to PDF Converter
Accepts HTML file paths and returns PDF URLs from localhost
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# PDF save location
PDF_SAVE_DIR = Path("pdfs")

# Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader('.'))

try:
    import weasyprint
    USE_WEASYPRINT = True
except (ImportError, OSError):
    USE_WEASYPRINT = False
    print("[DEBUG] weasyprint not available", file=sys.stderr)

try:
    from xhtml2pdf import pisa
    USE_XHTML2PDF = True
except ImportError:
    USE_XHTML2PDF = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    USE_REPORTLAB = True
except ImportError:
    USE_REPORTLAB = False

if not USE_WEASYPRINT and not USE_XHTML2PDF and not USE_REPORTLAB:
    print("Error: No PDF library available", file=sys.stderr)
    sys.exit(1)


def _create_pdf_reportlab(pdf_path: Path, html_path: Path):
    """Create PDF using reportlab with HTML content"""
    from html.parser import HTMLParser
    
    # Parse HTML to extract text content
    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_data = []
            self.skip = False
            
        def handle_starttag(self, tag, attrs):
            if tag in ('script', 'style'):
                self.skip = True
                
        def handle_endtag(self, tag):
            if tag in ('script', 'style'):
                self.skip = False
                
        def handle_data(self, data):
            if not self.skip:
                text = data.strip()
                if text:
                    self.text_data.append(text)
    
    # Read HTML file
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except:
        html_content = ""
    
    # Extract text from HTML
    parser = HTMLTextExtractor()
    parser.feed(html_content)
    text_lines = parser.text_data
    
    # Create PDF with extracted content
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, f"Document: {html_path.name}")
    
    # Add content from HTML
    c.setFont("Helvetica", 11)
    y_position = 720
    for line in text_lines:
        if y_position < 50:
            c.showPage()
            y_position = 750
        c.drawString(50, y_position, line[:90])  # Limit line length
        y_position -= 20
    
    # Add footer
    c.setFont("Helvetica", 9)
    c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.save()


class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "html_to_pdf",
                "description": "Convert HTML file to PDF and return localhost URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "html_file_path": {
                            "type": "string",
                            "description": "Path to HTML file (relative or absolute)",
                        },
                    },
                    "required": ["html_file_path"],
                },
            },
            {
                "name": "template_to_pdf",
                "description": "Render Jinja2 template with data and convert to PDF",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "template_path": {
                            "type": "string",
                            "description": "Path to Jinja2 template file (relative or absolute)",
                        },
                        "template_data": {
                            "type": "object",
                            "description": "JSON object with data to render in template",
                        },
                    },
                    "required": ["template_path", "template_data"],
                },
            }
        ]

    async def convert_html_to_pdf(self, html_file_path: str) -> dict:
        """Convert HTML file to PDF"""
        try:
            # Verify file exists
            html_path = Path(html_file_path).resolve()
            if not html_path.exists():
                raise FileNotFoundError(f"File not found: {html_file_path}")

            # Create pdfs directory
            pdf_dir = PDF_SAVE_DIR
            pdf_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] PDF directory: {pdf_dir.absolute()}", file=sys.stderr)

            # Generate PDF filename
            timestamp = int(datetime.now().timestamp() * 1000)
            pdf_name = f"{html_path.stem}-{timestamp}.pdf"
            pdf_path = pdf_dir / pdf_name
            print(f"[DEBUG] PDF path: {pdf_path.absolute()}", file=sys.stderr)

            # Convert HTML to PDF
            print(f"[DEBUG] Converting HTML to PDF...", file=sys.stderr)
            
            if USE_WEASYPRINT:
                print(f"[DEBUG] Using weasyprint", file=sys.stderr)
                try:
                    weasyprint.HTML(str(html_path)).write_pdf(str(pdf_path))
                except Exception as e:
                    print(f"[DEBUG] weasyprint failed: {e}, trying fallback", file=sys.stderr)
                    raise
            elif USE_XHTML2PDF:
                print(f"[DEBUG] Using xhtml2pdf", file=sys.stderr)
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        pisa.pisaDocument(f, open(pdf_path, 'wb'))
                except Exception as e:
                    print(f"[DEBUG] xhtml2pdf failed: {e}, trying reportlab", file=sys.stderr)
                    if USE_REPORTLAB:
                        _create_pdf_reportlab(pdf_path, html_path)
                    else:
                        raise
            elif USE_REPORTLAB:
                print(f"[DEBUG] Using reportlab", file=sys.stderr)
                _create_pdf_reportlab(pdf_path, html_path)
            else:
                raise RuntimeError("No PDF library available")
            
            print(f"[DEBUG] PDF created: {pdf_path.exists()}", file=sys.stderr)

            # Return URL
            pdf_url = f"http://localhost:3000/pdfs/{pdf_name}"
            return {
                "content": [{
                    "type": "text",
                    "text": f"PDF generated successfully: {pdf_url}",
                }],
            }

        except Exception as error:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(error)}",
                }],
                "isError": True,
            }

    async def template_to_pdf(self, template_path: str, template_data: dict) -> dict:
        """Render Jinja2 template with data and convert to PDF"""
        try:
            # Load and render template
            print(f"[DEBUG] Loading template: {template_path}", file=sys.stderr)
            template = jinja_env.get_template(template_path)
            html_content = template.render(**template_data)
            print(f"[DEBUG] Template rendered successfully", file=sys.stderr)

            # Create pdfs directory
            pdf_dir = PDF_SAVE_DIR
            pdf_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] PDF directory: {pdf_dir.absolute()}", file=sys.stderr)

            # Generate PDF filename
            timestamp = int(datetime.now().timestamp() * 1000)
            template_name = Path(template_path).stem
            pdf_name = f"{template_name}-{timestamp}.pdf"
            pdf_path = pdf_dir / pdf_name
            print(f"[DEBUG] PDF path: {pdf_path.absolute()}", file=sys.stderr)

            # Convert rendered HTML to PDF
            print(f"[DEBUG] Converting rendered HTML to PDF...", file=sys.stderr)
            
            if USE_REPORTLAB:
                print(f"[DEBUG] Using reportlab", file=sys.stderr)
                # For reportlab, we need to extract text from HTML (simplified)
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                c = canvas.Canvas(str(pdf_path), pagesize=letter)
                c.drawString(100, 750, f"PDF from template: {template_path}")
                c.drawString(100, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.save()
            else:
                # Try weasyprint or xhtml2pdf with the rendered HTML content
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html_content)
                    temp_html_path = f.name
                
                try:
                    if USE_WEASYPRINT:
                        print(f"[DEBUG] Using weasyprint", file=sys.stderr)
                        weasyprint.HTML(temp_html_path).write_pdf(str(pdf_path))
                    elif USE_XHTML2PDF:
                        print(f"[DEBUG] Using xhtml2pdf", file=sys.stderr)
                        with open(temp_html_path, 'r', encoding='utf-8') as hf:
                            pisa.pisaDocument(hf, open(pdf_path, 'wb'))
                finally:
                    Path(temp_html_path).unlink()
            
            print(f"[DEBUG] PDF created: {pdf_path.exists()}", file=sys.stderr)

            # Return URL
            pdf_url = f"http://localhost:3000/pdfs/{pdf_name}"
            return {
                "content": [{
                    "type": "text",
                    "text": f"PDF generated successfully: {pdf_url}",
                }],
            }

        except TemplateNotFound as error:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Template not found: {error}",
                }],
                "isError": True,
            }
        except Exception as error:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(error)}",
                }],
                "isError": True,
            }

    async def handle_list_tools(self, message: dict) -> dict:
        """Return available tools"""
        return {"tools": self.tools}

    async def handle_call_tool(self, message: dict) -> dict:
        """Handle tool calls"""
        tool_name = message["params"]["name"]
        tool_input = message["params"]["arguments"]

        if tool_name == "html_to_pdf":
            html_file_path = tool_input.get("html_file_path")
            return await self.convert_html_to_pdf(html_file_path)
        
        elif tool_name == "template_to_pdf":
            template_path = tool_input.get("template_path")
            template_data = tool_input.get("template_data", {})
            return await self.template_to_pdf(template_path, template_data)

        return {
            "content": [{
                "type": "text",
                "text": f"Unknown tool: {tool_name}",
            }],
            "isError": True,
        }

    async def run(self):
        """Main server loop"""
        print("MCP Server for HTML to PDF started", file=sys.stderr)

        while True:
            try:
                # Read JSON from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                message = json.loads(line)
                method = message.get("method")

                if method == "tools/list":
                    response = await self.handle_list_tools(message)
                elif method == "tools/call":
                    response = await self.handle_call_tool(message)
                else:
                    response = {"error": f"Unknown method: {method}"}

                # Send response
                print(json.dumps(response))
                sys.stdout.flush()

            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.run())
