// Writes frameworks/js from frameworks/ts: the same framework in plain JavaScript.
// Node removes the TypeScript types, then this script tidies what is left and adds .js to local imports.
// Run: node tools/pw-build/frameworks/make_js.mjs
import { stripTypeScriptTypes } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const here = path.dirname(new URL(import.meta.url).pathname);
const from = path.join(here, 'ts'), to = path.join(here, 'js');
fs.rmSync(to, { recursive: true, force: true });

function convert(src) {
  src = src.replace(/^import type .*\n/gm, '').replace(/^type \w+ = \{[^}]*\};\n\n?/gm, '');
  let js = stripTypeScriptTypes(src, { mode: 'strip' });
  js = js.split('\n').map(l => l.trimEnd()).join('\n');
  js = js.replace(/^\s+\w+\s*;\n/gm, '');                                // field declarations that only had a type
  js = js.replace(/(\w) {2,}([,)])/g, '$1$2').replace(/(\w) {2,}=/g, '$1 =').replace(/(\w) {2,}\(/g, '$1(').replace(/\) {2,}\{/g, ') {');
  js = js.replace(/(from '\.\.?\/[\w./-]+?)(?<!\.js)'/g, "$1.js'");   // ESM needs file extensions
  js = js.replace(/^\n+/, '').replace(/\{\n\n(\s+constructor)/g, '{\n$1').replace(/\n{3,}/g, '\n\n');
  return js;
}

for (const rel of fs.readdirSync(from, { recursive: true })) {
  const src = path.join(from, rel);
  if (fs.statSync(src).isDirectory() || rel === 'tsconfig.json') continue;
  let out = rel.replace(/\.ts$/, '.js');
  let body = fs.readFileSync(src, 'utf8');
  if (rel.endsWith('.ts')) body = convert(body);
  if (rel === 'package.json') body = body.replace(/\s+"@types\/node": "[^"]+",/, '').replace(/,\s+"typescript": "[^"]+"/, '');
  if (rel === 'README.md') body = body.replace('in TypeScript', 'in JavaScript');
  fs.mkdirSync(path.dirname(path.join(to, out)), { recursive: true });
  fs.writeFileSync(path.join(to, out), body);
}
console.log('wrote', to);
