// Layout check for Manual Testing pages: console errors, sideways scrolling, and overlapping diagram parts.
//   node check.js [page.html ...] [--shots dir]
const path = require('path');
const fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node22/lib/node_modules/playwright'); }

const args = process.argv.slice(2);
const si = args.indexOf('--shots');
const shots = si >= 0 ? args.splice(si, 2)[1] : '';
const dir = path.resolve(__dirname, '../../content/manual-testing');
const pages = args.length ? args : fs.readdirSync(dir).filter(f => f.endsWith('.html') && f !== 'interview-questions.html');

(async () => {
  const browser = await pw.chromium.launch();
  let bad = 0;
  for (const width of [1280, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 } });
    for (const p of pages) {
      const page = await ctx.newPage();
      const errs = [];
      page.on('pageerror', e => errs.push(e.message));
      page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource/.test(m.text())) errs.push(m.text()); });
      await page.goto('file://' + path.join(dir, p));
      await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
      await page.waitForTimeout(300);
      const r = await page.evaluate(() => {
        const out = [];
        const de = document.documentElement;
        if (de.scrollWidth > de.clientWidth + 1) {
          const wide = [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); return b.right > de.clientWidth + 1 && !e.closest('.vz-scroll,.tw,pre,.fg-wrap'); }).slice(0, 3).map(e => e.className || e.tagName);
          out.push('page scrolls sideways: ' + de.scrollWidth + ' > ' + de.clientWidth + ' ' + wide.join(' | '));
        }
        const area = (a, b) => Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
        const inside = (a, b) => a.x >= b.x && a.y >= b.y && a.x + a.width <= b.x + b.width && a.y + a.height <= b.y + b.height;
        const hit = (a, b) => a.x < b.x + b.width - 1 && b.x < a.x + a.width - 1 && a.y < b.y + b.height - 1 && b.y < a.y + a.height - 1;
        document.querySelectorAll('svg.fg-svg').forEach(svg => {
          const title = svg.getAttribute('aria-label');
          const nodes = [...svg.querySelectorAll('.fg-n')].map(g => ({ id: g.dataset.id, actor: g.firstElementChild.tagName === 'circle', shape: g.firstElementChild.getBBox(), texts: [...g.querySelectorAll('text.fg-l, text.fg-s')].map(t => t.getBBox()) }));
          nodes.forEach(n => n.texts.forEach(t => { if (!n.actor && t.width > n.shape.width + 2) out.push(`${title}: text wider than node ${n.id} (${Math.round(t.width)} > ${Math.round(n.shape.width)})`); }));
          for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) if (hit(nodes[i].shape, nodes[j].shape) && !inside(nodes[i].shape, nodes[j].shape) && !inside(nodes[j].shape, nodes[i].shape)) out.push(`${title}: nodes ${nodes[i].id} and ${nodes[j].id} overlap`);
          svg.querySelectorAll('.fg-lb').forEach(lb => {
            const b = lb.getBBox();
            nodes.forEach(n => { if (area(b, n.shape) > 0.25 * b.width * b.height) out.push(`${title}: arrow label "${lb.nextElementSibling.textContent}" covers node ${n.id}`); });
          });
          const labs = [...svg.querySelectorAll('.fg-lb')].map(l => l.getBBox());
          for (let i = 0; i < labs.length; i++) for (let j = i + 1; j < labs.length; j++) if (hit(labs[i], labs[j])) out.push(`${title}: two arrow labels overlap`);
          svg.querySelectorAll('text.fg-t').forEach(t => { const b = t.getBBox(); nodes.forEach(n => { if (area(b, n.shape) > 0.25 * b.width * b.height && !inside(b, n.shape)) out.push(`${title}: free text "${t.textContent}" covers node ${n.id}`); }); });
        });
        document.querySelectorAll('.viz').forEach(v => { if (/^Missing/.test(v.textContent.trim())) out.push('widget failed: ' + v.textContent.trim()); });
        return out;
      });
      const all = errs.map(e => 'error: ' + e).concat(r);
      if (all.length) { bad++; console.log(`✗ ${p} @${width}\n  ` + all.join('\n  ')); } else console.log(`✓ ${p} @${width}`);
      if (shots) { fs.mkdirSync(shots, { recursive: true }); await page.screenshot({ path: path.join(shots, `${p.replace('.html', '')}-${width}.png`), fullPage: true }); }
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
