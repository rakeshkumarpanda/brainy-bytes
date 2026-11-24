"""Helpers the SQL topic files use, on top of tools/cv-build/cvkit.py.

    K = SKit()
    K.sql(key, src, db='shop', setup='', title='', notes={})   a runnable SQL block. The build runs it with sql.js
        (the same SQLite the page loads) and stores the real output. notes maps a line number to a short note.
        err=True means the last statement is meant to fail (for example a constraint), and the build checks it does.
    K.lab(id, lv, title, task, solution, db='shop', hint, why, ordered=False)
        a hands on challenge. The reader writes SQL, the page runs it and compares the rows with the rows the
        model solution gives. ordered=True also compares the row order.
    K.talk(lesson_id, text)          the background voice talk for one lesson (data/talk/sql/<slug>.js)
    pk(name, **cfg)                  a playful step animation from assets/sqlwidgets.js
    value(db, sql)                   one value worked out with SQLite at build time, for worked problem checks
    rows(db, sql)                    (columns, rows) at build time, for tables written into the prose
    grid(db, sql, title)             an HTML table of real rows from a sample database
"""
import html as _h
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'cv-build'))
from cvkit import Kit  # noqa: E402

DATA = os.path.join(HERE, 'data')
_cache = {}


def dataset(name):
    if name not in _cache:
        _cache[name] = open(os.path.join(DATA, name + '.sql'), encoding='utf-8').read() if name else ''
    return _cache[name]


def _db(name, setup=''):
    c = sqlite3.connect(':memory:')
    c.execute('PRAGMA foreign_keys = ON')
    c.executescript(dataset(name) + '\n' + setup)
    return c


def value(db, sql, setup=''):
    r = _db(db, setup).execute(sql).fetchone()
    return r[0]


def rows(db, sql, setup=''):
    cur = _db(db, setup).execute(sql)
    return [d[0] for d in cur.description], cur.fetchall()


def _fmt(v):
    if v is None:
        return '<i class="sq-null">NULL</i>'
    if isinstance(v, float) and v.is_integer():
        return str(int(v)) if abs(v) > 1e15 else f'{v:.1f}'
    return _h.escape(str(v))


def grid(db, sql, title='', setup=''):
    cols, rs = rows(db, sql, setup)
    h = ''.join(f'<th>{_h.escape(c)}</th>' for c in cols)
    b = ''.join('<tr>' + ''.join(f'<td>{_fmt(v)}</td>' for v in r) + '</tr>' for r in rs)
    cap = f'<div class="sq-gcap">{title}</div>' if title else ''
    return f'<div class="sq-grid">{cap}<div class="tw"><table class="cvt sq-t"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div></div>'


def pk(name, **cfg):
    c = _h.escape(json.dumps(cfg, ensure_ascii=False)) if cfg else ''
    return f'<div class="viz" data-viz="pk" data-pk="{name}"' + (f' data-cfg="{c}"' if c else '') + '></div>'


class SKit(Kit):
    def __init__(self):
        super().__init__()
        self.runs, self.labs, self.talks = {}, [], {}

    def sql(self, key, src, db='shop', setup='', title='', notes=None, err=False):
        if key in self.runs:
            raise SystemExit(f'sql block {key} is written twice')
        src = src.strip('\n')
        n = len(src.split('\n'))
        for k in (notes or {}):
            if not 1 <= k <= n:
                raise SystemExit(f'sql block {key}: note for line {k}, but it has {n} lines')
        self.runs[key] = {'src': src, 'db': db, 'setup': setup.strip('\n'), 'title': title,
                          'notes': {str(k): v for k, v in (notes or {}).items()}, 'err': err}
        return f'<div class="sq-run" data-q="{key}"></div>'

    def lab(self, id, lv, title, task, solution, db='shop', hint='', why='', ordered=False, setup='', starter=''):
        self.labs.append({'id': id, 'lv': lv, 'title': title, 'task': task, 'solution': solution.strip('\n'), 'db': db,
                          'hint': hint, 'why': why, 'ordered': ordered, 'setup': setup.strip('\n'),
                          'starter': starter.strip('\n')})
        return f'<div class="sq-lab" data-lab="{id}"></div>'

    def talk(self, lesson_id, text):
        self.talks[lesson_id] = ' '.join(text.split())

    def topic(self, **t):
        t = super().topic(**t)
        t.update(runs=self.runs, labs=self.labs, talks=self.talks)
        return t
