/* ===== Code Playground worker: runs Java, C, C++, C#, JavaScript and TypeScript away from the page =====
   The page starts a fresh worker for every run, so each program starts clean, and Stop can end a program
   that never finishes by ending the worker.

   Message in:  { lang, code, stdin, trace, lineMap }    (TypeScript arrives already compiled to JavaScript)
   Message out: { k: 'done', res }   res = { out: [{s, e}], trace, error, compile, notes, stopped }
                { k: 'fail', msg }   when the runner itself could not load */
const ACORN_URL = 'https://cdn.jsdelivr.net/npm/acorn@8.14.0/dist/acorn.js';
let loaded = '';
function load(kind) {
  if (loaded === kind) return;
  if (kind === 'cf') importScripts('cf-parse.js', 'cf-run.js', 'cf-expr.js', 'cf-lib.js');
  else importScripts(ACORN_URL, 'js-trace.js');
  loaded = kind;
}
onmessage = async ev => {
  const d = ev.data || {};
  try {
    if (d.lang === 'js' || d.lang === 'ts') {
      try { load('js'); } catch (e) { postMessage({ k: 'fail', msg: 'The JavaScript reader could not load. Check your internet connection, then try again.' }); return; }
      const ins = JT.instrument(d.code, d.lineMap || null);
      if (ins.error) { postMessage({ k: 'done', res: { out: [], trace: null, error: null, compile: ins.error, notes: [] } }); return; }
      const res = await JT.run(ins.code, { stdin: d.stdin, trace: !!d.trace, maxSteps: d.maxSteps, maxOps: d.maxOps });
      postMessage({ k: 'done', res });
      return;
    }
    load('cf');
    const res = CF.run(d.code, d.lang, { stdin: d.stdin || '', trace: !!d.trace, maxSteps: d.maxSteps, maxOps: d.maxOps });
    postMessage({ k: 'done', res });
  } catch (e) {
    postMessage({ k: 'fail', msg: 'The playground hit a problem of its own while running this program: ' + (e && e.message || e) + '. Try a smaller program, or tell us which code caused it.' });
  }
};
