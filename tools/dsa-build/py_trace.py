"""Run one Python program and record it line by line for the step viewer.

Usage: python3 py_trace.py prog.py  ->  prints {"trace": {...}, "out": "..."} as JSON.
"""
import io, json, sys, types
from collections import deque

FILE = '<prog>'
MAX_STEPS = 1500


def fmt(v, depth=0):
    if v is None or isinstance(v, (bool, int, float)):
        return repr(v)
    if isinstance(v, str):
        r = repr(v)
        return r if len(r) <= 80 else r[:77] + "…'"
    if depth >= 3:
        return '…'
    if isinstance(v, deque):
        return 'deque(' + fmt(list(v), depth) + ')'
    if isinstance(v, (list, tuple, set)):
        items = list(v) if not isinstance(v, set) else sorted(v, key=repr)
        body = ', '.join(fmt(x, depth + 1) for x in items[:12])
        if len(items) > 12:
            body += f', … +{len(items) - 12}'
        if isinstance(v, tuple):
            return '(' + body + (',)' if len(items) == 1 else ')')
        if isinstance(v, set):
            return '{' + body + '}' if items else 'set()'
        return '[' + body + ']'
    if isinstance(v, dict):
        items = list(v.items())
        body = ', '.join(f'{fmt(a, depth + 1)}: {fmt(b, depth + 1)}' for a, b in items[:10])
        if len(items) > 10:
            body += f', … +{len(items) - 10}'
        return '{' + body + '}'
    d = getattr(v, '__dict__', None)
    name = type(v).__name__
    if d is not None:
        if depth >= 2:
            return name + '(…)' if d else name + '()'
        return name + '(' + ', '.join(f'{k}={fmt(x, depth + 1)}' for k, x in d.items()) + ')'
    return repr(v)[:80]


def visible(name, v):
    if name.startswith('__'):
        return False
    return not isinstance(v, (types.ModuleType, types.FunctionType, type, types.BuiltinFunctionType))


def snap(frames):
    out = {}
    g = frames[0].f_globals
    for k, v in list(g.items()):
        if visible(k, v):
            out['G.' + k] = fmt(v)
    top = frames[-1]
    if top.f_code.co_name != '<module>':
        for k, v in list(top.f_locals.items()):
            if visible(k, v):
                out['L.' + k] = fmt(v)
    return out


def main():
    src = open(sys.argv[1]).read()
    code = compile(src, FILE, 'exec')
    buf = io.StringIO()
    steps, state = [], {'vars': {}, 'stack': None, 'olen': 0, 'trunc': False}

    def label(f):
        return 'main program' if f.f_code.co_name == '<module>' else f.f_code.co_name + '()'

    def on_line(frame):
        if len(steps) >= MAX_STEPS:
            state['trunc'] = True
            raise SystemExit
        frames = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == FILE:
                frames.append(f)
            f = f.f_back
        frames.reverse()
        st = {'l': frame.f_lineno}
        stack = [label(f) for f in frames]
        if stack != state['stack']:
            st['s'] = stack
            state['stack'] = stack
        cur = snap(frames)
        d = {k: v for k, v in cur.items() if state['vars'].get(k) != v}
        for k in state['vars']:
            if k not in cur:
                d[k] = None
        if d:
            st['d'] = d
        state['vars'] = cur
        o = buf.getvalue()
        if len(o) > state['olen']:
            st['o'] = o[state['olen']:]
            state['olen'] = len(o)
        steps.append(st)

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FILE:
            return None
        if event == 'line':
            on_line(frame)
        return tracer

    g = {'__name__': '__main__'}
    real = sys.stdout
    sys.stdout = buf
    sys.settrace(tracer)
    try:
        exec(code, g)
    except SystemExit:
        pass
    finally:
        sys.settrace(None)
        sys.stdout = real
    o = buf.getvalue()
    end = {'o': o[state['olen']:], 't': state['trunc']}
    print(json.dumps({'trace': {'steps': steps, 'end': end}, 'out': o}, ensure_ascii=False))


main()
