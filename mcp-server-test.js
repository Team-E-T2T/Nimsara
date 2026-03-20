// mcp-server-test.js
// Test version that doesn't require Claude to connect
import * as fs from "fs";
import * as path from "path";
import puppeteer from "puppeteer";

async function convertHtmlToPdf(htmlFilePath) {
    console.log(`\n[INFO] Converting: ${htmlFilePath}`);

    try {
        // Verify file exists
        if (!fs.existsSync(htmlFilePath)) {
            throw new Error(`File not found: ${htmlFilePath}`);
        }

        // Launch browser
        console.log("[INFO] Launching browser...");
        const browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();

        // Load HTML file
        const htmlPath = path.resolve(htmlFilePath);
        const fileUrl = `file://${htmlPath}`;
        console.log(`[INFO] Loading: ${fileUrl}`);
        await page.goto(fileUrl, { waitUntil: "networkidle2" });

        // Create PDF
        const pdfName = `${path.basename(htmlFilePath, ".html")}-${Date.now()}.pdf`;
        const pdfPath = path.join("pdfs", pdfName);

        if (!fs.existsSync("pdfs")) {
            fs.mkdirSync("pdfs", { recursive: true });
            console.log("[INFO] Created /pdfs folder");
        }

        console.log(`[INFO] Generating PDF: ${pdfName}`);
        await page.pdf({ path: pdfPath, format: "A4" });
        await browser.close();

        const pdfUrl = `http://localhost:3000/pdfs/${pdfName}`;
        console.log(`\n✅ SUCCESS!`);
        console.log(`📄 PDF created: ${pdfPath}`);
        console.log(`🔗 URL: ${pdfUrl}\n`);

        return pdfUrl;
    } catch (error) {
        console.error(`\n❌ ERROR: ${error.message}\n`);
        process.exit(1);
    }
}

// Get file path from command line argument
const htmlFile = process.argv[2];

if (!htmlFile) {
    console.log(`
Usage: node mcp-server-test.js <path-to-html-file>

Example:
  node mcp-server-test.js test.html
  node mcp-server-test.js C:\\path\\to\\file.html
    `);
    process.exit(1);
}

convertHtmlToPdf(htmlFile);