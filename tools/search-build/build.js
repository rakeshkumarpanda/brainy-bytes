#!/usr/bin/env node
/* =====================================================================
   SUBJECT SEARCH BUILDER

   Makes one small search file per subject in data/search/<subject>.js.
   The subject page loads that file the first time a learner opens
   "Search in <subject>", so the search covers the words written inside
   every chapter, not only the chapter titles in the catalog.

   How it works
     1. Read data/catalog.js to find every live topic page of a subject.
     2. Open each page in headless Chromium, so pages that draw their
        text with JavaScript are indexed too.
     3. Cut the page into pieces at each h1, h2 and h3 heading. Each piece
        keeps the heading, the id the page can jump to, and its plain text.
     4. Write data/search/<subject>.js and data/search/manifest.js.

   Run from the repository root
     node tools/search-build/build.js              (every subject)
     node tools/search-build/build.js python ai    (only these subjects)

   Needs Node 18 or newer and the playwright package with Chromium.
   Run it again after adding or changing a chapter.
   ===================================================================== */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.join(ROOT, 'data', 'search');
const MAX_PIECE = 4000;      // a longer piece is split into parts of about this size
const SKIP_PAGE = /-compact\.html$/; // compact cheatsheets repeat the full cheatsheet

/* long text is cut into parts at a space, so every word stays searchable and snippets stay quick */
function split(x) {
  const out = [];
  while (x.length > MAX_PIECE) {
    let cut = x.lastIndexOf(' ', MAX_PIECE);
    if (cut < MAX_PIECE / 2) cut = MAX_PIECE;
    out.push(x.slice(0, cut));
    x = x.slice(cut + 1);
  }
  out.push(x);
  return out;
}

function loadCatalog() {
  const w = {};
  vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'data', 'catalog.js'), 'utf8'), { window: w });
  return w.CATALOG;
}

/* runs inside the page: returns [{ a: anchor, t: heading, x: text }] */
function extract() {
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SVG', 'svg', 'CANVAS', 'BUTTON', 'SELECT', 'OPTION', 'INPUT', 'TEXTAREA', 'IFRAME', 'NAV', 'ASIDE']);
  const BLOCK = /^(P|LI|TD|TH|DT|DD|PRE|H[1-6]|DIV|SECTION|ARTICLE|BLOCKQUOTE|FIGCAPTION|SUMMARY|DETAILS|TR|UL|OL|TABLE|BR)$/;
  const clean = s => s.replace(/🔊/g, '').replace(/\s+/g, ' ').trim();
  const headCount = el => el.querySelectorAll('h1,h2,h3').length;
  function anchorOf(h) {
    if (h.id) return h.id;
    let el = h.parentElement;
    while (el && el !== document.body) {
      if (el.id && headCount(el) <= 4) return el.id;
      el = el.parentElement;
    }
    const prev = h.previousElementSibling;
    if (prev && prev.id && !prev.children.length) return prev.id;
    return '';
  }
  const pieces = [];
  let cur = { a: '', t: '', x: [] };
  pieces.push(cur);
  const root = document.querySelector('main') && headCount(document.querySelector('main')) ? document.querySelector('main') : document.body;
  (function walk(node) {
    for (let n = node.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) { if (n.nodeValue.trim()) cur.x.push(n.nodeValue); continue; }
      if (n.nodeType !== 1) continue;
      if (SKIP.has(n.tagName) || n.getAttribute('aria-hidden') === 'true' || n.classList.contains('lh-skip')) continue;
      if (/^H[1-3]$/.test(n.tagName)) {
        const t = clean(n.textContent);
        if (t) { cur = { a: anchorOf(n), t, x: [] }; pieces.push(cur); continue; }
      }
      const block = BLOCK.test(n.tagName);
      if (block) cur.x.push(' ');
      walk(n);
      if (block) cur.x.push(' ');
    }
  })(root);
  return pieces.map(p => ({ a: p.a, t: p.t, x: clean(p.x.join('')) })).filter(p => p.t || p.x);
}

async function main() {
  const only = process.argv.slice(2);
  const cat = loadCatalog();
  fs.mkdirSync(OUT, { recursive: true });
  const manifestPath = path.join(OUT, 'manifest.js');
  let manifest = {};
  if (fs.existsSync(manifestPath)) {
    const w = {}; vm.runInNewContext(fs.readFileSync(manifestPath, 'utf8'), { window: w });
    manifest = (w.LH_SEARCH_MANIFEST) || {};
  }
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  /* fonts and remote files only slow the build, the text does not need them */
  await ctx.route(/^https?:/, r => r.abort());
  const page = await ctx.newPage();
  page.on('dialog', d => d.dismiss().catch(() => {}));

  for (const s of cat.subjects) {
    if (only.length && !only.includes(s.id)) continue;
    const topics = [];
    (s.modules || []).forEach(m => (m.topics || []).forEach(t => { if (t.page && !t.soon && !SKIP_PAGE.test(t.page)) topics.push(t); }));
    if (s.page && !topics.length) topics.push({ id: '', title: s.title, page: s.page });
    if (!topics.length) { delete manifest[s.id]; continue; }
    const seen = new Set();
    const T = [], C = [];
    const t0 = Date.now();
    for (const t of topics) {
      if (seen.has(t.page)) continue;
      seen.add(t.page);
      const file = path.join(ROOT, t.page);
      if (!fs.existsSync(file)) { console.warn(`  missing page ${t.page}`); continue; }
      let pieces = [];
      try {
        await page.goto('file://' + file, { waitUntil: 'load', timeout: 30000 });
        await page.waitForTimeout(250);
        pieces = await page.evaluate(extract);
      } catch (e) { console.warn(`  could not read ${t.page}: ${e.message.split('\n')[0]}`); continue; }
      const ti = T.length;
      T.push([t.id, t.title, t.emoji || '📄']);
      /* a piece for the topic itself, from the catalog, so its title, summary and keywords are found */
      C.push([ti, '', t.title, [t.summary || '', ...(t.keywords || [])].join(' · ')]);
      let lastAnchor = '';
      for (const p of pieces) {
        if (!p.x && !p.t) continue;
        const title = (p.t && p.t !== t.title ? p.t : '').replace(/^(\p{Extended_Pictographic}|\uFE0F|\u200D)+\s*/u, '');
        /* text before the first heading belongs to the topic piece */
        if (!title && !p.a) { C[C.length - 1][3] += ' ' + p.x; continue; }
        /* a heading with no id of its own jumps to the closest place above it that has one */
        const a = p.a || lastAnchor;
        lastAnchor = a;
        for (const x of split(p.x)) C.push([ti, a, title, x]);
      }
    }
    const data = { s: s.id, t: T, c: C };
    const body = JSON.stringify(data);
    const v = crypto.createHash('sha1').update(body).digest('hex').slice(0, 10);
    fs.writeFileSync(path.join(OUT, s.id + '.js'),
      `/* Search index for ${s.title}. Made by tools/search-build/build.js, do not edit by hand. */\n` +
      `(window.LH_SEARCH = window.LH_SEARCH || {})[${JSON.stringify(s.id)}] = ${body};\n`);
    manifest[s.id] = v;
    console.log(`${s.id}: ${T.length} pages, ${C.length} pieces, ${(body.length / 1024).toFixed(0)} KB, ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  }
  await browser.close();
  const sorted = Object.fromEntries(Object.keys(manifest).sort().map(k => [k, manifest[k]]));
  fs.writeFileSync(manifestPath,
    `/* Version of each subject search file, so browsers fetch a fresh copy after a rebuild. Made by tools/search-build/build.js. */\n` +
    `window.LH_SEARCH_MANIFEST = ${JSON.stringify(sorted, null, 1)};\n`);
}

main().catch(e => { console.error(e); process.exit(1); });
