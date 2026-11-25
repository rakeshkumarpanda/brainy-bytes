/* ===== Code Playground: real Python (CPython in WebAssembly, by Pyodide) in a module worker =====
   It loads once from the jsDelivr CDN, the same Pyodide build the Python chapters use, and the browser keeps it.

   Message in:  { code, stdin, trace, maxSteps, maxOps }
   Message out: { k: 'ready', v }  then for each run  { k: 'chunk', s, e }  while a Run all prints,
                and { k: 'done', res }  with res shaped like the other runners: { out, trace, error, notes, stopped } */
import { loadPyodide } from 'https://cdn.jsdelivr.net/npm/pyodide@314.0.7/pyodide.mjs';

const TRACER = `
import sys, io, json, types, traceback, linecache
_PG_FILE = 'main.py'

def _pg_short(v):
    try:
        if isinstance(v, (types.FunctionType, types.BuiltinFunctionType)):
            return '<function ' + getattr(v, '__name__', '?') + '>'
        if isinstance(v, type):
            return '<class ' + v.__name__ + '>'
        r = repr(v)
    except Exception as e:
        r = '<' + type(v).__name__ + '>'
    return r if len(r) <= 120 else r[:117] + '...'

def _pg_vars(f, module):
    items = f.f_globals if module else f.f_locals
    out = []
    for k, v in list(items.items()):
        if k.startswith('__') or k.startswith('_pg_'):
            continue
        if issubclass(type(v), types.ModuleType):
            continue
        if module and isinstance(v, (types.FunctionType, type, types.BuiltinFunctionType)):
            continue
        out.append([k, _pg_short(v), ''])
    return out

def _pg_tb(e):
    tb = e.__traceback__
    while tb is not None and tb.tb_frame.f_code.co_filename != _PG_FILE:
        tb = tb.tb_next
    return ''.join(traceback.format_exception(type(e), e, tb))

class _PgCut(BaseException):
    pass

def _pg_record(src, stdin_text, max_steps, max_ops):
    steps = []
    out = io.StringIO()
    state = {'ops': 0, 'cut': None}

    def snap(frame, ev, extra=None):
        state['ops'] += 1
        if state['ops'] > max_ops:
            state['cut'] = 'The program ran for a very long time, so the playground stopped it. Check for a loop whose condition never becomes false'
            raise _PgCut()
        if len(steps) >= max_steps:
            state['cut'] = 'Step by step shows the first %d steps. Use Run all to run the whole program' % max_steps
            raise _PgCut()
        frames, f = [], frame
        while f is not None:
            if f.f_code.co_filename == _PG_FILE:
                frames.append(f)
            f = f.f_back
        frames.reverse()
        stack = []
        for f in frames:
            module = f.f_code.co_name == '<module>'
            stack.append({'fn': 'Main program' if module else f.f_code.co_name + '()', 'line': f.f_lineno, 'vars': _pg_vars(f, module)})
        st = {'line': frame.f_lineno, 'ev': ev, 'out': len(out.getvalue()), 'stack': stack}
        if extra:
            st.update(extra)
        steps.append(st)

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != _PG_FILE:
            return None
        if event == 'call':
            if frame.f_code.co_name != '<module>':
                snap(frame, 'call')
        elif event == 'line':
            snap(frame, 'line')
        elif event == 'return' and frame.f_code.co_name != '<module>':
            snap(frame, 'ret', {'ret': _pg_short(arg)})
        return tracer

    err = None
    real_out, real_err, real_in = sys.stdout, sys.stderr, sys.stdin
    sys.stdout, sys.stderr, sys.stdin = out, out, io.StringIO(stdin_text)
    linecache.cache[_PG_FILE] = (len(src), None, src.splitlines(True), _PG_FILE)
    main = types.ModuleType('__main__')
    saved = sys.modules.get('__main__')
    try:
        code = compile(src, _PG_FILE, 'exec')
        sys.modules['__main__'] = main
        sys.settrace(tracer)
        try:
            exec(code, main.__dict__)
        finally:
            sys.settrace(None)
    except _PgCut:
        pass
    except SystemExit:
        pass
    except BaseException as e:
        err = _pg_tb(e)
    finally:
        sys.stdout, sys.stderr, sys.stdin = real_out, real_err, real_in
        sys.modules['__main__'] = saved
    text = out.getvalue()
    res = {'out': [{'s': text, 'e': False}] if text else [], 'trace': steps, 'error': None, 'notes': [], 'stopped': state['cut']}
    if err:
        line = steps[-1]['line'] if steps else 1
        res['out'].append({'s': err, 'e': True})
        res['error'] = {'msg': err.rstrip(), 'line': line}
        steps.append({'line': line, 'ev': 'error', 'out': len(text) + len(err), 'msg': err.rstrip(), 'stack': steps[-1]['stack'] if steps else []})
    steps.append({'line': steps[-1]['line'] if steps else 1, 'ev': 'end', 'out': len(text) + len(err or ''), 'stack': []})
    return json.dumps(res)

def _pg_run(src):
    linecache.cache[_PG_FILE] = (len(src), None, src.splitlines(True), _PG_FILE)
    main = types.ModuleType('__main__')
    saved = sys.modules.get('__main__')
    err = None
    try:
        code = compile(src, _PG_FILE, 'exec')
        sys.modules['__main__'] = main
        exec(code, main.__dict__)
    except SystemExit:
        pass
    except BaseException as e:
        err = _pg_tb(e)
    finally:
        sys.modules['__main__'] = saved
        sys.stdout.flush()
    return err or ''
`;

let stdinText = '';
let sink = null;
const ready = loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/npm/pyodide@314.0.7/' }).then(py => {
  const dOut = new TextDecoder(), dErr = new TextDecoder();
  py.setStdout({ write: buf => { const s = dOut.decode(buf, { stream: true }); if (sink && s) sink(s, false); return buf.length; } });
  py.setStderr({ write: buf => { const s = dErr.decode(buf, { stream: true }); if (sink && s) sink(s, true); return buf.length; } });
  py.setStdin({ stdin: () => { const t = stdinText; stdinText = null; return t; } });
  py.runPython(TRACER);
  postMessage({ k: 'ready', v: py.runPython('import sys; sys.version.split()[0]') });
  return py;
}).catch(e => { postMessage({ k: 'fail', msg: 'Python could not be loaded. Check your internet connection, then try again. (' + (e && e.message || e) + ')' }); throw e; });

onmessage = async ev => {
  const d = ev.data || {};
  let py;
  try { py = await ready; } catch (e) { return; }
  try {
    try { await py.loadPackagesFromImports(d.code); } catch (e) { /* not a Pyodide package: the import fails in Python with a clear message */ }
    if (d.trace) {
      const json = py.globals.get('_pg_record')(d.code, d.stdin || '', d.maxSteps || 3000, d.maxOps || 3000000);
      postMessage({ k: 'done', res: JSON.parse(json) });
      return;
    }
    const out = [];
    let len = 0, cut = false;
    sink = (s, e) => {
      if (cut) return;
      len += s.length;
      if (len > 2e6) { cut = true; s = s.slice(0, Math.max(0, s.length - (len - 2e6))) + '\n'; }
      const last = out[out.length - 1];
      if (last && last.e === e) last.s += s; else out.push({ s, e });
      postMessage({ k: 'chunk', s, e });
    };
    stdinText = d.stdin || '';
    const err = py.globals.get('_pg_run')(d.code);
    sink = null;
    const res = { out, trace: null, error: null, notes: [], stopped: cut ? 'The program printed more than two million characters, so the playground stopped showing more' : null };
    if (err) { out.push({ s: err, e: true }); postMessage({ k: 'chunk', s: err, e: true }); res.error = { msg: err.trimEnd(), line: lastLine(err) }; }
    postMessage({ k: 'done', res });
  } catch (e) {
    sink = null;
    postMessage({ k: 'fail', msg: 'Python stopped with a problem of its own: ' + (e && e.message || e) });
  }
};
function lastLine(tb) {
  const m = [...tb.matchAll(/File "main\.py", line (\d+)/g)];
  return m.length ? +m[m.length - 1][1] : 1;
}
