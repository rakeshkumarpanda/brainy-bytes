// Print one subject of data/catalog.js as JSON, for tools/path-build/build.py.
// Usage: node tools/path-build/catalog-dump.js <subject id>
const fs = require('fs');
const path = require('path');
global.window = global;
global.document = {};
const src = fs.readFileSync(path.join(__dirname, '..', '..', 'data', 'catalog.js'), 'utf8');
// the catalog is a plain script with one top level const, so evaluate it with that const turned into a global
(0, eval)(src.replace(/^const (\w+)\s*=/m, 'var $1 ='));
const cat = Object.values(global).find(v => v && Array.isArray(v.subjects));
const s = cat.subjects.find(x => x.id === process.argv[2]);
if (!s) { console.error('no subject ' + process.argv[2]); process.exit(1); }
console.log(JSON.stringify({
  id: s.id, title: s.title, layout: s.layout || '',
  modules: (s.modules || []).map(m => ({
    id: m.id, title: m.title, step: m.step || 0, level: m.level || '', part: m.part || '',
    topics: m.topics.map(t => ({ id: t.id, title: t.title, page: t.page || '', soon: !!t.soon, summary: t.summary || '' }))
  }))
}));
