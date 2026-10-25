"""Check the "Watch CPython run your code" animation (assets/pyviz.js) against the real CPython.

It writes thousands of small random programs in the subset the animation supports, then compares, for each one:
  the tokens (type and text) with the tokenize module
  the tree with ast.dump(ast.parse(code))
  every instruction name, argument and argument text with dis (only the co_consts index of LOAD_CONST is skipped)
  what the program prints, and the error it ends with, with exec

Usage:  python3.14 tools/py-build/check_pyvm.py [count]
Needs:  the same Python version the pages describe (3.14) and Node.js.
"""
import ast
import contextlib
import dis
import io
import json
import os
import random
import subprocess
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NAMES = ['a', 'b', 'total', 'x']
FUNCS = ['print', 'abs', 'len', 'max', 'min', 'str', 'int', 'float', 'round']
OPS = ['+', '-', '*', '/', '//', '%', '**']
CMPS = ['<', '<=', '==', '!=', '>', '>=']


def lit(r):
    k = r.random()
    if k < 0.35:
        return str(r.choice([0, 1, 2, 3, 5, 7, 10, 40, 100, 255, 256, 300, 1000]))
    if k < 0.45:
        return str(r.choice([2 ** 40, 10 ** 12, 99999999999, 123456789]))
    if k < 0.65:
        return r.choice(['1.5', '0.1', '2.0', '1e3', '3.25', '0.0001', '1e16', '7.5', '1e-5', '.5'])
    if k < 0.85:
        return r.choice(['"ab"', "'hi'", '"it\'s"', "'x'", '""', '"a b"'])
    return r.choice(['True', 'False', 'None'])


def expr(r, d=0):
    k = r.random()
    if d > 2 or k < 0.3:
        return lit(r) if r.random() < 0.6 else r.choice(NAMES)
    if k < 0.65:
        op = r.choice(OPS)
        # Keep powers small so that CPython itself never has to build a huge number.
        right = r.choice(['2', '3', '0', '-1', '0.5', '"a"', 'a']) if op == '**' else expr(r, d + 1)
        e = f'{expr(r, d + 1)} {op} {right}'
        return f'({e})' if r.random() < 0.4 else e
    if k < 0.75:
        return f'-{expr(r, d + 1)}' if r.random() < 0.5 else f'-({expr(r, d + 1)})'
    if k < 0.85:
        return f'({expr(r, 3)} {r.choice(CMPS)} {expr(r, 3)})'
    f = r.choice(FUNCS)
    n = 1 if f in ('abs', 'len', 'str', 'int', 'float', 'round') else r.randint(0, 3)
    return f'{f}({", ".join(expr(r, d + 1) for _ in range(n))})'


def program(r):
    lines = []
    for _ in range(r.randint(1, 5)):
        if r.random() < 0.7:
            lines.append(f'{r.choice(NAMES)} = {expr(r)}')
        else:
            lines.append(f'print({", ".join(expr(r) for _ in range(r.randint(1, 3)))})')
    return '\n'.join(lines)


def real(src):
    toks = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        name = tokenize.tok_name[t.type]
        if name in ('NEWLINE', 'NL', 'ENDMARKER'):
            toks.append([name, ''])
        else:
            toks.append([name, t.string])
    code = compile(src, 'main.py', 'exec')
    ins = []
    for i in dis.get_instructions(code):
        arg = None if i.opname == 'LOAD_CONST' else i.arg
        ins.append([i.opname, arg, i.argrepr, i.line_number if i.starts_line else None])
    out = io.StringIO()
    err = None
    with contextlib.redirect_stdout(out):
        try:
            exec(code, {'__name__': '__main__'})
        except Exception as e:
            tb = e.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            err = [type(e).__name__, str(e), tb.tb_lineno]
    lines = out.getvalue().split('\n')[:-1]
    return {'tokens': toks, 'dump': ast.dump(ast.parse(src)), 'ins': ins, 'out': lines, 'err': err}


NODE = r'''
const P = require(process.argv[1]);
const progs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const res = progs.map(src => {
  const r = P.analyse(src);
  if (r.error) return { fail: r.error };
  const e = r.exec.error;
  return {
    tokens: r.tokens.map(t => [t.type, ['NEWLINE', 'NL', 'ENDMARKER'].includes(t.type) ? '' : t.text]),
    dump: r.dump,
    ins: r.code.map(c => [c.op, c.op === 'LOAD_CONST' ? null : (c.arg === undefined ? null : c.arg), c.rep, c.starts ? c.line : null]),
    out: r.exec.out, err: e ? (e.type === 'Demo' ? ['Demo', e.msg] : [e.type, e.msg, e.line]) : null
  };
});
process.stdout.write(JSON.stringify(res));
'''


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    r = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 2026)
    progs, want = [], []
    for _ in range(n):
        src = program(r)
        try:
            w = real(src)
        except (OverflowError, ValueError, MemoryError):
            continue
        progs.append(src)
        want.append(w)
    p = subprocess.run(['node', '-e', NODE, os.path.join(ROOT, 'assets', 'pyviz.js')], input=json.dumps(progs), capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stderr)
    got = json.loads(p.stdout)
    bad = skipped = 0
    for src, w, g in zip(progs, want, got):
        if 'fail' in g and g['fail']['type'] == 'Demo':
            skipped += 1
            continue
        if 'fail' in g:
            bad += 1
            print('--- could not analyse\n' + src + '\n', g['fail'])
            continue
        if g['err'] and g['err'][0] == 'Demo':
            skipped += 1
            g['out'] = w['out']  # the demo stops on purpose for huge or complex results
            g['err'] = w['err']
        for k in ('tokens', 'dump', 'ins', 'out', 'err'):
            if w[k] != g[k]:
                bad += 1
                print(f'--- {k} differs\n{src}\nCPython: {json.dumps(w[k])}\nPYVM:    {json.dumps(g[k])}\n')
                break
        if bad > 15:
            break
    print(f'{len(progs)} programs, {bad} differences, {skipped} stopped by the demo limits, Python {sys.version.split()[0]}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
