"""Run one Python program and record it line by line for the "Line by line" viewer on the Python pages.

The same file runs in two places:
  at build time:  python3.14 pytrace.py main.py [stdin file]  ->  prints the recording as JSON
  in the browser: assets/pyplay.js loads this source into Pyodide and calls record(source, stdin_text)

A recording is {"steps": [...], "tail": text, "err": traceback text or null, "cut": bool}. Each step is
{"l": line, "ev": "line" | "call" | "return", "s": call stack labels, "d": {name: repr or null}, "o": new output}.
s, d and o appear only when something changed, to keep pages small. "tail" is output printed after the last step.
"""
import io
import json
import linecache
import sys
import traceback
import types

FILE = 'main.py'
MAX_STEPS = 600


def fmt(v, depth=0):
    try:
        if isinstance(v, (types.ModuleType, types.FunctionType, type, types.BuiltinFunctionType)):
            return '<' + type(v).__name__ + ' ' + getattr(v, '__name__', '?') + '>'
        r = repr(v)
    except Exception as e:  # a broken __repr__ must not stop the recording
        r = '<' + type(v).__name__ + ' (repr failed: ' + type(e).__name__ + ')>'
    return r if len(r) <= 90 else r[:87] + '...'


def visible(name, v):
    if name.startswith('__') or name in ('_record_',):
        return False
    return not isinstance(v, types.ModuleType)


def record(src, stdin_text=''):
    steps, out = [], io.StringIO()
    state = {'vars': {}, 'stack': None, 'olen': 0, 'cut': False}

    def label(f):
        return 'module' if f.f_code.co_name == '<module>' else f.f_code.co_name + '()'

    def snap(frame, event):
        if len(steps) >= MAX_STEPS:
            state['cut'] = True
            raise KeyboardInterrupt
        frames, f = [], frame
        while f is not None:
            if f.f_code.co_filename == FILE:
                frames.append(f)
            f = f.f_back
        frames.reverse()
        st = {'l': frame.f_lineno, 'ev': event}
        stack = [label(f) for f in frames]
        if stack != state['stack']:
            st['s'] = stack
            state['stack'] = stack
        cur = {}
        for k, v in list(frames[0].f_globals.items()):
            if visible(k, v):
                cur['G.' + k] = fmt(v)
        top = frames[-1]
        if top.f_code.co_name != '<module>':
            for k, v in list(top.f_locals.items()):
                if visible(k, v):
                    cur['L.' + k] = fmt(v)
        d = {k: v for k, v in cur.items() if state['vars'].get(k) != v}
        for k in state['vars']:
            if k not in cur:
                d[k] = None
        if d:
            st['d'] = d
        state['vars'] = cur
        o = out.getvalue()
        if len(o) > state['olen']:
            st['o'] = o[state['olen']:]
            state['olen'] = len(o)
        steps.append(st)

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FILE:
            return None
        if event in ('line', 'call', 'return') and not (event == 'call' and frame.f_code.co_name == '<module>'):
            snap(frame, event)
        return tracer

    err = None
    real_out, real_in = sys.stdout, sys.stdin
    sys.stdout, sys.stdin = out, io.StringIO(stdin_text)
    # Tracebacks read source lines through linecache, so give it the program text.
    linecache.cache[FILE] = (len(src), None, src.splitlines(True), FILE)
    try:
        code = compile(src, FILE, 'exec')
        sys.settrace(tracer)
        try:
            exec(code, {'__name__': '__main__'})
        finally:
            sys.settrace(None)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except BaseException as e:
        tb = e.__traceback__
        while tb is not None and tb.tb_frame.f_code.co_filename != FILE:
            tb = tb.tb_next
        err = ''.join(traceback.format_exception(type(e), e, tb)).rstrip()
    finally:
        sys.stdout, sys.stdin = real_out, real_in
    o = out.getvalue()
    return {'steps': steps, 'tail': o[state['olen']:], 'err': err, 'cut': state['cut']}


if __name__ == '__main__':
    source = open(sys.argv[1], encoding='utf-8').read()
    given = open(sys.argv[2], encoding='utf-8').read() if len(sys.argv) > 2 else ''
    print(json.dumps(record(source, given), ensure_ascii=False))
