// Render a subject cheatsheet page to a PDF with headless Chromium.
// Usage: node tools/cv-build/sheet-pdf.js <cheatsheet.html> <out.pdf> "<Subject name>"
// Called by tools/cv-build/cheatsheet.py. Prints the page count on success.
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const [src, out, name] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(src), { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await page.evaluate(() => document.fonts.ready).catch(() => {});
  await page.emulateMedia({ media: 'print', colorScheme: 'light' });
  const compact = await page.evaluate(() => document.body.classList.contains('compactp'));
  const foot = `<div style="width:100%;font:9px sans-serif;color:#667;padding:0 14mm;display:flex;justify-content:space-between">
    <span>Brainy Bytes · ${name}</span><span><span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;
  const buf = await page.pdf({
    format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>', footerTemplate: foot,
    margin: compact ? { top: '8mm', bottom: '11mm', left: '8mm', right: '8mm' } : { top: '12mm', bottom: '14mm', left: '11mm', right: '11mm' }
  });
  fs.writeFileSync(out, buf);
  const pages = (buf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
  console.log(pages ? pages + ' pages' : 'PDF written');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
