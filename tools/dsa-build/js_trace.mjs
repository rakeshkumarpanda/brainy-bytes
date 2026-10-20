// Run one JavaScript program under the Node inspector and record it line by line for the step viewer.
// Usage: node js_trace.mjs prog.js  ->  prints {"trace": {...}, "out": "..."} as JSON.
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const file = path.resolve(process.argv[2]);
const url = pathToFileURL(file).href;
const MAX_STEPS = 1500;
const HIDE = new Set(['exports', 'require', 'module', '__filename', '__dirname']);

// Runs inside the traced program to turn a value into short text.
const FMT = `function fmt(v, d) {
  d = d || 0;
  if (v === null) return 'null';
  if (v === undefined) return 'undefined';
  const t = typeof v;
  if (t === 'string') { const s = "'" + v + "'"; return s.length > 80 ? s.slice(0, 77) + "…'" : s; }
  if (t === 'number' || t === 'boolean' || t === 'bigint') return String(v);
  if (t === 'function') return 'ƒ ' + (v.name || '');
  if (d >= 3) return '…';
  if (Array.isArray(v)) { const b = v.slice(0, 12).map(x => fmt(x, d + 1)); if (v.length > 12) b.push('… +' + (v.length - 12)); return '[' + b.join(', ') + ']'; }
  if (v instanceof Map) { const e = [...v.entries()]; const b = e.slice(0, 10).map(([a, c]) => fmt(a, d + 1) + ' => ' + fmt(c, d + 1)); if (e.length > 10) b.push('… +' + (e.length - 10)); return 'Map(' + v.size + ') {' + b.join(', ') + '}'; }
  if (v instanceof Set) { const e = [...v]; const b = e.slice(0, 12).map(x => fmt(x, d + 1)); if (e.length > 12) b.push('… +' + (e.length - 12)); return 'Set(' + v.size + ') {' + b.join(', ') + '}'; }
  const name = v.constructor && v.constructor !== Object ? v.constructor.name : '';
  if (name && d >= 1) return name;
  const ks = Object.keys(v);
  const b = ks.slice(0, 10).map(k => k + ': ' + fmt(v[k], d + 1));
  if (ks.length > 10) b.push('… +' + (ks.length - 10));
  return (name ? name + ' ' : '') + '{' + b.join(', ') + '}';
}`;

const child = spawn(process.execPath, ['--inspect-brk=127.0.0.1:0', file], { stdio: ['ignore', 'pipe', 'pipe'] });
let out = '', olen = 0;
child.stdout.on('data', b => { out += b; });
let wsUrl = await new Promise((res, rej) => {
  let err = '';
  child.stderr.on('data', b => { err += b; const m = err.match(/ws:\/\/[^\s]+/); if (m) res(m[0]); });
  child.on('exit', () => rej(new Error('node exited: ' + err)));
});

const ws = new WebSocket(wsUrl);
await new Promise(r => ws.addEventListener('open', r));
let id = 0;
const pending = new Map();
const pauses = [];
let waiter = null;
let myScript = null;
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Debugger.scriptParsed' && m.params.url === url) myScript = m.params.scriptId;
  if (m.method === 'Debugger.paused') { pauses.push(m.params); if (waiter) { const w = waiter; waiter = null; w(); } }
});
let closed = false;
ws.addEventListener('close', () => { closed = true; if (waiter) { const w = waiter; waiter = null; w(); } });
const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const nextPause = () => new Promise(res => { if (pauses.length || closed) res(); else waiter = res; });

await send('Runtime.enable');
await send('Debugger.enable');
await send('Debugger.setBlackboxPatterns', { patterns: ['^node:', 'internal/'] });
send('Runtime.runIfWaitingForDebugger');

async function fmtObj(objectId) {
  const r = await send('Runtime.callFunctionOn', { objectId, functionDeclaration: `function(){ ${FMT}; return fmt(this, 0); }`, returnByValue: true });
  return r.result && r.result.result ? r.result.result.value : '?';
}
async function scopeVars(scope, prefix, into) {
  const r = await send('Runtime.getProperties', { objectId: scope.object.objectId, ownProperties: true });
  for (const p of (r.result && r.result.result) || []) {
    if (HIDE.has(p.name) || !p.value) continue;
    const v = p.value;
    if (v.type === 'function' || v.type === 'undefined') continue;
    if (v.type === 'object' && v.subtype !== 'null') into[prefix + p.name] = await fmtObj(v.objectId);
    else if (v.type === 'string') into[prefix + p.name] = "'" + v.value + "'";
    else if (v.subtype === 'null') into[prefix + p.name] = 'null';
    else into[prefix + p.name] = v.unserializableValue || String(v.value);
  }
}
async function thisVars(obj, into) {
  if (!obj || obj.type !== 'object' || !obj.objectId || obj.subtype === 'null') return;
  if (obj.className === 'Object' || obj.className === 'global') return;
  const r = await send('Runtime.getProperties', { objectId: obj.objectId, ownProperties: true });
  for (const p of (r.result && r.result.result) || []) {
    if (!p.value || !p.enumerable) continue;
    const v = p.value;
    if (v.type === 'function') continue;
    if (v.type === 'object' && v.subtype !== 'null') into['L.this.' + p.name] = await fmtObj(v.objectId);
    else if (v.type === 'string') into['L.this.' + p.name] = "'" + v.value + "'";
    else if (v.subtype === 'null') into['L.this.' + p.name] = 'null';
    else if (v.type !== 'undefined') into['L.this.' + p.name] = v.unserializableValue || String(v.value);
  }
}
const label = f => {
  const n = f.functionName;
  if (!n) return 'main program';
  return n === 'constructor' ? 'constructor' : n + '()';
};

const steps = [];
let prevVars = {}, prevStack = null, trunc = false, lastLine = {}, lastDepth = 0;
for (;;) {
  await nextPause();
  if (!pauses.length) break;
  const p = pauses.shift();
  const mine = f => f.location.scriptId === myScript;
  const frames = p.callFrames.filter(mine);
  if (!frames.length) { if (steps.length) { await send('Debugger.resume'); break; } await send('Debugger.stepInto'); continue; }
  if (!mine(p.callFrames[0])) { await send('Debugger.stepOut'); continue; }
  const top = frames[0];
  const line = top.location.lineNumber + 1;
  const depth = frames.length;
  // the module wrapper sits at the bottom; its line 1 pause is the start of the program
  const stack = frames.slice().reverse().map(f => (f === frames[frames.length - 1] ? 'main program' : label(f)));
  // fix class constructor names: V8 calls them by the class name
  for (let k = 1; k < stack.length; k++) {
    const f = frames[frames.length - 1 - k];
    if (f.functionName && /^[A-Z]/.test(f.functionName) && f.this && f.this.className === f.functionName) stack[k] = f.functionName + '()';
  }
  const sameAsLast = lastLine[depth] === line && (depth < lastDepth || (depth === lastDepth && steps.length && steps[steps.length - 1].l === line));
  lastDepth = depth;
  if (sameAsLast) { await send('Debugger.stepInto'); continue; }
  lastLine[depth] = line;
  for (const k of Object.keys(lastLine)) if (+k > depth) delete lastLine[k];
  if (steps.length >= MAX_STEPS) { trunc = true; break; }
  const cur = {};
  const bottom = frames[frames.length - 1];
  for (const s of bottom.scopeChain) if (s.type === 'local' || s.type === 'block' || s.type === 'script') await scopeVars(s, 'G.', cur);
  if (top !== bottom) {
    for (const s of top.scopeChain) if (s.type === 'local' || s.type === 'block' || s.type === 'catch') await scopeVars(s, 'L.', cur);
    await thisVars(top.this, cur);
  }
  await new Promise(r => setTimeout(r, 4));
  const st = { l: line };
  if (JSON.stringify(stack) !== JSON.stringify(prevStack)) { st.s = stack; prevStack = stack; }
  const d = {};
  for (const k in cur) if (prevVars[k] !== cur[k]) d[k] = cur[k];
  for (const k in prevVars) if (!(k in cur)) d[k] = null;
  if (Object.keys(d).length) st.d = d;
  prevVars = cur;
  if (out.length > olen) { st.o = out.slice(olen); olen = out.length; }
  steps.push(st);
  await send('Debugger.stepInto');
}
if (trunc) { try { await send('Debugger.disable'); } catch (e) { /* gone */ } }
try { ws.close(); } catch (e) { /* gone */ }
await new Promise(r => { if (child.exitCode !== null) r(); else child.on('exit', r); setTimeout(() => { child.kill(); r(); }, 400); });
// the wrapper line 1 pause is not a real line of the program
if (steps.length && steps[0].l === 1 && !steps[0].d && steps.length > 1 && steps[1].l !== 1) { const s0 = steps.shift(); if (s0.s && !steps[0].s) steps[0].s = s0.s; }
process.stdout.write(JSON.stringify({ trace: { steps, end: { o: out.slice(olen), t: trunc } }, out }));
