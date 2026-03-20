// mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, Tool } from "@modelcontextprotocol/sdk/types.js";
import * as fs from "fs";
import * as path from "path";
import puppeteer from "puppeteer";

const server = new Server({
  name: "html-to-pdf-server",
  version: "1.0.0",
});

const tools: Tool[] = [
  {
    name: "html_to_pdf",
    description: "Convert HTML file to PDF and return localhost URL",
    inputSchema: {
      type: "object",
      properties: {
        html_file_path: {
          type: "string",
          description: "Path to HTML file (relative or absolute)",
        },
      },
      required: ["html_file_path"],
    },
  },
];

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "html_to_pdf") {
    const { html_file_path } = request.params.arguments as { 
      html_file_path: string 
    };

    try {
      const browser = await puppeteer.launch();
      const page = await browser.newPage();
      const htmlPath = path.resolve(html_file_path);
      const fileUrl = `file://${htmlPath}`;

      await page.goto(fileUrl, { waitUntil: "networkidle2" });

      // Generate filename for PDF
      const pdfName = `${path.basename(
        html_file_path,
        ".html"
      )}-${Date.now()}.pdf`;
      const pdfPath = path.join("pdfs", pdfName);

      // Create pdfs directory if it doesn't exist
      if (!fs.existsSync("pdfs")) {
        fs.mkdirSync("pdfs", { recursive: true });
      }

      await page.pdf({ path: pdfPath, format: "A4" });
      await browser.close();

      const pdfUrl = `http://localhost:3000/pdfs/${pdfName}`;
      return {
        content: [
          {
            type: "text",
            text: `PDF generated successfully: ${pdfUrl}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }

  return {
    content: [{ type: "text", text: "Unknown tool" }],
    isError: true,
  };
});

const transport = new StdioServerTransport();
server.connect(transport);