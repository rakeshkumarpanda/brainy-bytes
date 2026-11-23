/* ===== SQL in the browser for the SQL subject pages (tools/sql-build/build.py) =====
   Loads SQLite (sql.js 1.16.0, vendored in assets/vendor/sqljs) and the sample databases (assets/sqldata.js),
   then turns three kinds of placeholders into live tools:

     .sq-run[data-q]    a runnable query: edit it, Run it, or run it one statement at a time with Step
     .sq-lab[data-lab]  a hands on lab: write SQL, Check compares your rows with the rows of the model answer
     the playground     a full SQL editor with a database picker and a table browser, opened from the
                        "SQL playground" button on every page (key: Ctrl or Cmd + Enter runs)

   The output shown before you press Run was recorded at build time with the same SQLite build.
   Other scripts use window.SQ: SQ.ready (a promise of the SQL module), SQ.open(name, extraSql), SQ.run(db, src),
   SQ.table(html helpers) and SQ.hl(sql) for highlighting.
*/
(() => {
  const me = document.currentScript && document.currentScript.src;
  const BASE = me ? me.replace(/[^/]*$/, '') : '../../assets/';
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = (s, r = document) => r.querySelector(s);
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  };

  let readyP = null;
  function ready() {
    if (!readyP) readyP = initSqlJs({ locateFile: f => BASE + 'vendor/sqljs/' + f, useOldExtensionFunctions: false });
    return readyP;
  }
  const DATA = window.SQDATA || {};
  function open(SQL, name, extra) { return SQRUN.open(SQL, (DATA[name] || '') + '\n' + (extra || '')); }

  /* ---------- highlighting ---------- */
  const KW = new Set(('select from where and or not in is null like glob between exists case when then else end as on join inner left right full outer cross natural using group by having order asc desc limit offset distinct all union intersect except insert into values update set delete create table view index unique primary key foreign references check default constraint drop alter add column rename to if begin commit rollback transaction savepoint release with recursive over partition window rows range groups unbounded preceding following current row filter returning conflict do nothing replace trigger after before instead of for each explain query plan pragma integer text real blob numeric strict cascade restrict no action deferrable initially deferred immediate exclusive cast collate nocase vacuum analyze materialized escape true false varchar char int date grant revoke').split(' '));
  const FN = new Set('count sum avg min max total group_concat string_agg round abs length lower upper trim ltrim rtrim substr substring replace instr coalesce ifnull nullif iif typeof date time datetime julianday strftime unixepoch printf format random row_number rank dense_rank ntile lag lead first_value last_value nth_value percent_rank cume_dist json json_extract json_object json_array json_each json_group_array cast hex quote char unicode likely sqlite_version changes total_changes last_insert_rowid concat concat_ws sign ceil floor sqrt power pow mod ln log exp pi'.split(' '));
  function hl(src) {
    const re = /(--[^\n]*|\/\*[\s\S]*?\*\/)|('(?:[^']|'')*'?)|("(?:[^"]|"")*"?)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)|([\s\S])/g;
    let out = '', m;
    while ((m = re.exec(src))) {
      if (m[1]) out += `<span class="sh-c">${esc(m[1])}</span>`;
      else if (m[2]) out += `<span class="sh-s">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="sh-i">${esc(m[3])}</span>`;
      else if (m[4]) out += `<span class="sh-n">${m[4]}</span>`;
      else if (m[5]) {
        const w = m[5].toLowerCase();
        out += KW.has(w) ? `<span class="sh-k">${esc(m[5])}</span>` : FN.has(w) && src[re.lastIndex] === '(' ? `<span class="sh-f">${esc(m[5])}</span>` : esc(m[5]);
      } else out += esc(m[6]);
    }
    return out;
  }

  /* ---------- an editor: a textarea over a highlighted copy, with line numbers ---------- */
  function editor(host, text, onRun) {
    host.innerHTML = `<div class="sq-ed"><div class="sq-gut" aria-hidden="true"></div><div class="sq-area"><pre class="sq-hl" aria-hidden="true"></pre><textarea spellcheck="false" autocomplete="off" autocapitalize="off" aria-label="SQL editor"></textarea></div></div>`;
    const ta = $('textarea', host), pre = $('.sq-hl', host), gut = $('.sq-gut', host);
    let marks = {}, cur = null;
    function paint() {
      const v = ta.value;
      pre.innerHTML = hl(v) + '\n';
      const n = v.split('\n').length;
      let g = '';
      for (let i = 1; i <= n; i++) g += `<span class="${marks[i] ? 'mk' : ''}${cur && i >= cur[0] && i <= cur[1] ? ' now' : ''}">${i}</span>`;
      gut.innerHTML = g;
      ta.style.height = 'auto';
      ta.style.height = Math.max(ta.scrollHeight, 44) + 'px';
    }
    ta.value = text;
    ta.addEventListener('input', paint);
    ta.addEventListener('keydown', e => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); onRun && onRun(); }
      if (e.key === 'Tab' && !e.shiftKey) {
        e.preventDefault();
        const s = ta.selectionStart;
        ta.setRangeText('  ', s, ta.selectionEnd, 'end');
        paint();
      }
    });
    paint();
    return {
      get value() { return ta.value; },
      set value(v) { ta.value = v; paint(); },
      mark(m) { marks = m || {}; paint(); },
      now(range) { cur = range; paint(); },
      focus() { ta.focus(); },
      ta
    };
  }

  /* ---------- results ---------- */
  function cell(v) {
    if (v === null) return '<i class="sq-null">NULL</i>';
    return esc(v);
  }
  function grid(cols, rows, more) {
    const h = cols.map(c => `<th>${esc(c)}</th>`).join('');
    const b = rows.map(r => `<tr>${r.map(v => `<td>${cell(v)}</td>`).join('')}</tr>`).join('');
    return `<div class="tw"><table class="cvt sq-t"><thead><tr>${h}</tr></thead><tbody>${b || `<tr><td colspan="${cols.length}" class="sq-none">No rows</td></tr>`}</tbody></table></div>`
      + `<div class="sq-cnt">${more ? `Showing ${rows.length} of ${more} rows` : `${rows.length} ${rows.length === 1 ? 'row' : 'rows'}`}</div>`;
  }
  const friendly = [
    [/no such table: (\w+)/i, m => `There is no table called <b>${esc(m[1])}</b>. Check the spelling, or open the table list in the playground.`],
    [/no such column: ([\w.]+)/i, m => `There is no column called <b>${esc(m[1])}</b> here. Check the spelling and which table it belongs to.`],
    [/syntax error/i, () => 'SQLite could not read this statement. Look near the word it names: a missing comma, quote or bracket is the usual cause.'],
    [/UNIQUE constraint failed/i, () => 'A UNIQUE or PRIMARY KEY rule stopped this: that value is already in the table.'],
    [/NOT NULL constraint failed/i, () => 'A NOT NULL rule stopped this: the column needs a value.'],
    [/CHECK constraint failed/i, () => 'A CHECK rule stopped this: the value broke the rule written on the table.'],
    [/FOREIGN KEY constraint failed/i, () => 'A FOREIGN KEY rule stopped this: the row points to a parent that does not exist, or a child still points to it.'],
    [/misuse of aggregate/i, () => 'An aggregate such as COUNT or SUM was used where only plain values are allowed. Filter groups with HAVING instead of WHERE.']
  ];
  function errBox(msg) {
    let tip = '';
    for (const [re, f] of friendly) { const m = re.exec(msg); if (m) { tip = f(m); break; } }
    return `<div class="sq-err"><b>Error</b> <code>${esc(msg)}</code>${tip ? `<div>${tip}</div>` : ''}</div>`;
  }
  function records(out, compact) {
    if (!out.length) return '<div class="sq-cnt">Nothing to run.</div>';
    return out.map((o, i) => {
      const head = out.length > 1 || compact ? `<div class="sq-stm"><span>${i + 1}</span><code>${esc(o.sql.length > 110 ? o.sql.slice(0, 107) + '...' : o.sql)}</code></div>` : '';
      if (o.error) return head + errBox(o.error);
      if (o.cols.length) return head + grid(o.cols, o.rows, o.more);
      return head + `<div class="sq-ok">Done.${o.changes !== undefined ? ` ${o.changes} ${o.changes === 1 ? 'row' : 'rows'} changed.` : ''}</div>`;
    }).join('');
  }

  /* where each statement sits in the source, as [first line, last line] */
  function lineRanges(src, out) {
    const res = [];
    let from = 0;
    out.forEach(o => {
      const k = src.indexOf(o.sql.replace(/;$/, ''), from);
      if (k < 0) { res.push(null); return; }
      const a = src.slice(0, k).split('\n').length, b = a + o.sql.split('\n').length - 1;
      res.push([a, b]);
      from = k + o.sql.length - 1;
    });
    return res;
  }

  const PAGE = (() => { const el = document.getElementById('sqdata'); return el ? JSON.parse(el.textContent) : { runs: {}, labs: [] }; })();
  const DBNAME = { shop: 'Bytes Bazaar shop', school: 'Sunrise School', company: 'Orbit Tech company', '': 'empty' };

  /* ---------- runnable blocks ---------- */
  function mountRun(el) {
    const R = PAGE.runs[el.dataset.q];
    if (!R || el.dataset.on) return;
    el.dataset.on = '1';
    const notes = R.notes || {};
    el.innerHTML = `<div class="sq-box"><div class="sq-bar"><span class="sq-tag">SQL</span><b>${esc(R.title || 'Try this query')}</b>${R.db ? `<span class="sq-db" title="Sample database">${esc(DBNAME[R.db] || R.db)}</span>` : ''}<span class="grow"></span>
      <button type="button" class="sq-b sq-go" title="Ctrl + Enter">Run</button><button type="button" class="sq-b sq-step">Step</button><button type="button" class="sq-b sq-rs">Reset</button><button type="button" class="sq-b sq-cp">Copy</button></div>
      <div class="sq-edh"></div>
      ${Object.keys(notes).length ? `<details class="sq-notes"><summary>What each marked line does</summary><ol>${Object.entries(notes).sort((a, b) => a[0] - b[0]).map(([n, t]) => `<li><b>Line ${n}</b><span>${t}</span></li>`).join('')}</ol></details>` : ''}
      <div class="sq-outh"><div class="sq-cap">Output <small>(recorded when this page was built, press Run to run it yourself)</small></div><div class="sq-out" aria-live="polite"></div></div></div>`;
    const marks = {};
    Object.keys(notes).forEach(n => { marks[n] = 1; });
    let stepDb = null, stepAt = 0, stepOut = [];
    const ed = editor($('.sq-edh', el), R.src, () => runAll());
    ed.mark(marks);
    const out = $('.sq-out', el), cap = $('.sq-cap', el);
    out.innerHTML = records(R.out || []);
    function busy(t) { cap.innerHTML = t; }
    function runAll() {
      stepDb = null; ed.now(null);
      busy('Output <small>running...</small>');
      ready().then(SQL => {
        const db = open(SQL, R.db, R.setup);
        const o = SQRUN.run(db, ed.value);
        db.close();
        busy(`Output <small>(${o.length} ${o.length === 1 ? 'statement' : 'statements'} run just now)</small>`);
        out.innerHTML = records(o);
      }).catch(e => { busy('Output'); out.innerHTML = errBox('SQLite could not load: ' + e.message); });
    }
    function step() {
      ready().then(SQL => {
        if (!stepDb) {
          const probe = open(SQL, R.db, R.setup);
          const all = SQRUN.run(probe, ed.value);
          probe.close();
          stepDb = { db: open(SQL, R.db, R.setup), stms: all.map(o => o.sql), ranges: lineRanges(ed.value, all) };
          stepAt = 0; stepOut = [];
        }
        if (stepAt >= stepDb.stms.length) { stepDb.db.close(); stepDb = null; ed.now(null); busy('Output <small>(all statements done, press Step to start again)</small>'); return; }
        const o = SQRUN.run(stepDb.db, stepDb.stms[stepAt]);
        stepOut.push(o[0] || { sql: stepDb.stms[stepAt], cols: [], rows: [] });
        ed.now(stepDb.ranges[stepAt]);
        stepAt++;
        busy(`Output <small>(statement ${stepAt} of ${stepDb.stms.length}, press Step for the next one)</small>`);
        out.innerHTML = records(stepOut, true);
        if (o[0] && o[0].error) { stepDb.db.close(); stepDb = null; }
      });
    }
    $('.sq-go', el).addEventListener('click', runAll);
    $('.sq-step', el).addEventListener('click', step);
    $('.sq-rs', el).addEventListener('click', () => { stepDb = null; ed.value = R.src; ed.mark(marks); ed.now(null); out.innerHTML = records(R.out || []); busy('Output <small>(recorded when this page was built, press Run to run it yourself)</small>'); });
    $('.sq-cp', el).addEventListener('click', e => { try { navigator.clipboard.writeText(ed.value); e.target.textContent = 'Copied'; setTimeout(() => { e.target.textContent = 'Copy'; }, 1200); } catch (x) { /* no clipboard */ } });
  }

  /* ---------- labs ---------- */
  const LV = { e: 'Easy', m: 'Medium', h: 'Hard', x: 'Expert' };
  function sameRows(want, got, ordered) {
    if (!got || got.cols.length !== want.cols.length) return false;
    const key = r => JSON.stringify(r.map(v => typeof v === 'number' ? Math.round(v * 1e6) / 1e6 : v));
    const a = want.rows.map(key), b = got.rows.map(key);
    if (a.length !== b.length) return false;
    if (ordered) return a.every((x, i) => x === b[i]);
    a.sort(); b.sort();
    return a.every((x, i) => x === b[i]);
  }
  function schemaHtml(SQL, name, setup) {
    const db = open(SQL, name, setup);
    const t = db.exec("SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid");
    const html = t.length ? t[0].values.map(([n]) => {
      const c = db.exec(`SELECT name, type, pk FROM pragma_table_info('${n.replace(/'/g, "''")}')`)[0];
      return `<span class="sq-sch"><b>${esc(n)}</b> ${c ? c.values.map(([cn, ty, pk]) => `<i${pk ? ' class="pk"' : ''}>${esc(cn)}</i>`).join(' ') : ''}</span>`;
    }).join('') : '';
    db.close();
    return html;
  }
  function mountLab(el) {
    const L = PAGE.labs.find(l => l.id === el.dataset.lab);
    if (!L || el.dataset.on) return;
    el.dataset.on = '1';
    const key = 'sq-lab:' + location.pathname + ':' + L.id;
    const saved = store.get(key, null);
    el.innerHTML = `<div class="sq-labc${saved && saved.ok ? ' won' : ''}"><div class="sq-lh"><span class="sq-lv lv-${L.lv}">${LV[L.lv] || L.lv}</span><b>Lab: ${esc(L.title)}</b><span class="sq-won">Solved</span></div>
      <div class="sq-task">${L.task}</div><div class="sq-schema"><small>Tables you can use</small><div class="sq-schl">loading...</div></div>
      <div class="sq-edh"></div>
      <div class="sq-lbar"><button type="button" class="sq-b sq-go">Run and check</button><button type="button" class="sq-b sq-hint">Hint</button><button type="button" class="sq-b sq-sol">Show answer</button><button type="button" class="sq-b sq-rs">Reset</button></div>
      <div class="sq-verdict" aria-live="polite"></div><div class="sq-out"></div>
      <div class="sq-hintb" hidden>${L.hint}</div><div class="sq-solb" hidden><div class="sq-cap">A model answer</div><pre class="sq-code">${hl(L.solution)}</pre><div class="sq-why">${L.why}</div></div></div>`;
    const start = L.starter || '-- Write your SQL here, then press Run and check\n';
    const ed = editor($('.sq-edh', el), saved && saved.sql ? saved.sql : start, () => check());
    const out = $('.sq-out', el), ver = $('.sq-verdict', el), card = $('.sq-labc', el);
    ready().then(SQL => { $('.sq-schl', el).innerHTML = schemaHtml(SQL, L.db, L.setup); });
    ed.ta.addEventListener('input', () => { ver.innerHTML = ''; store.set(key, { sql: ed.value, ok: card.classList.contains('won') }); });
    function check() {
      ready().then(SQL => {
        const db = open(SQL, L.db, L.setup);
        const o = SQRUN.run(db, ed.value);
        db.close();
        out.innerHTML = records(o);
        const last = o[o.length - 1];
        if (!last || last.error) { ver.innerHTML = '<div class="sq-no">Not yet. Fix the error first, the message below says where it is.</div>'; return; }
        const ok = sameRows(L.want, last, L.ordered);
        if (ok) {
          card.classList.add('won');
          ver.innerHTML = '<div class="sq-yes">Correct. Your rows match the expected answer exactly.</div>';
          if (window.FUN && FUN.confetti) try { FUN.confetti(); } catch (e) { /* optional */ }
        } else {
          const why = last.cols.length !== L.want.cols.length ? `The answer needs ${L.want.cols.length} ${L.want.cols.length === 1 ? 'column' : 'columns'}, yours has ${last.cols.length}.`
            : last.rows.length !== L.want.rows.length ? `The answer has ${L.want.rows.length} rows, yours has ${last.rows.length}.`
              : L.ordered ? 'The right count of rows, but the values or their order differ.' : 'The right count of rows, but some values differ.';
          ver.innerHTML = `<div class="sq-no">Not yet. ${why}</div>`;
        }
        store.set(key, { sql: ed.value, ok: card.classList.contains('won') });
      });
    }
    $('.sq-go', el).addEventListener('click', check);
    $('.sq-hint', el).addEventListener('click', () => { const h = $('.sq-hintb', el); h.hidden = !h.hidden; });
    $('.sq-sol', el).addEventListener('click', () => { const h = $('.sq-solb', el); h.hidden = !h.hidden; });
    $('.sq-rs', el).addEventListener('click', () => { ed.value = start; out.innerHTML = ''; ver.innerHTML = ''; card.classList.remove('won'); store.set(key, null); });
  }

  /* ---------- the playground ---------- */
  function playground() {
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'sq-pgbtn'; btn.innerHTML = '<span>SQL</span> playground';
    btn.setAttribute('aria-label', 'Open the SQL playground');
    document.body.appendChild(btn);
    const pane = document.createElement('aside');
    pane.className = 'sq-pg'; pane.hidden = true; pane.setAttribute('aria-label', 'SQL playground');
    const names = Object.keys(DATA);
    pane.innerHTML = `<div class="sq-pgh"><b>SQL playground</b><select aria-label="Database">${names.map(n => `<option value="${n}">${esc(DBNAME[n] || n)}</option>`).join('')}<option value="">Empty database</option></select><span class="grow"></span><button type="button" class="sq-b sq-x" aria-label="Close">Close</button></div>
      <div class="sq-pgb"><div class="sq-tables"></div><div class="sq-edh"></div>
      <div class="sq-lbar"><button type="button" class="sq-b sq-go">Run (Ctrl + Enter)</button><button type="button" class="sq-b sq-new">Fresh database</button><button type="button" class="sq-b sq-ex">Example</button></div>
      <div class="sq-pgnote">Changes stay in this database until you press Fresh database or pick another one. Nothing leaves your browser.</div>
      <div class="sq-out" aria-live="polite"></div></div>`;
    document.body.appendChild(pane);
    const sel = $('select', pane), out = $('.sq-out', pane), tables = $('.sq-tables', pane);
    const st = store.get('sq-pg', { db: 'shop', sql: "SELECT name, city\nFROM customers\nWHERE city = 'Pune';" });
    sel.value = names.includes(st.db) || st.db === '' ? st.db : names[0];
    let db = null;
    const ed = editor($('.sq-edh', pane), st.sql, () => go());
    ed.ta.addEventListener('input', () => store.set('sq-pg', { db: sel.value, sql: ed.value }));
    function fresh() {
      return ready().then(SQL => {
        if (db) db.close();
        db = open(SQL, sel.value);
        listTables(SQL);
        return db;
      });
    }
    function listTables() {
      const t = db.exec("SELECT name, type FROM sqlite_schema WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY type, rowid");
      tables.innerHTML = t.length ? t[0].values.map(([n, ty]) => {
        const c = db.exec(`SELECT name, type, pk FROM pragma_table_info('${n.replace(/'/g, "''")}')`)[0];
        const cnt = db.exec(`SELECT count(*) FROM "${n.replace(/"/g, '""')}"`)[0].values[0][0];
        return `<details class="sq-tb"><summary><b>${esc(n)}</b> <small>${ty === 'view' ? 'view' : cnt + ' rows'}</small><button type="button" class="sq-peek" data-t="${esc(n)}">Show rows</button></summary><ul>${c ? c.values.map(([cn, cty, pk]) => `<li${pk ? ' class="pk"' : ''}><code>${esc(cn)}</code> <small>${esc(cty || 'any type')}${pk ? ', primary key' : ''}</small></li>`).join('') : ''}</ul></details>`;
      }).join('') : '<div class="sq-cnt">No tables yet. Try CREATE TABLE.</div>';
    }
    function go() {
      (db ? Promise.resolve(db) : fresh()).then(d => {
        out.innerHTML = records(SQRUN.run(d, ed.value), true);
        listTables();
      });
    }
    tables.addEventListener('click', e => {
      const b = e.target.closest('.sq-peek');
      if (!b) return;
      e.preventDefault();
      ed.value = `SELECT *\nFROM "${b.dataset.t}"\nLIMIT 20;`;
      store.set('sq-pg', { db: sel.value, sql: ed.value });
      go();
    });
    const EX = { shop: "SELECT c.name, COUNT(o.id) AS orders\nFROM customers AS c\nLEFT JOIN orders AS o ON o.customer_id = c.id\nGROUP BY c.id\nORDER BY orders DESC;", school: "SELECT s.name, AVG(m.score) AS average\nFROM students AS s\nJOIN marks AS m ON m.student_id = s.id\nGROUP BY s.id\nORDER BY average DESC;", company: "SELECT e.name, m.name AS manager\nFROM employees AS e\nLEFT JOIN employees AS m ON m.id = e.manager_id;", '': "CREATE TABLE pets (name TEXT, kind TEXT);\nINSERT INTO pets VALUES ('Tommy', 'dog'), ('Kitty', 'cat');\nSELECT * FROM pets;" };
    $('.sq-ex', pane).addEventListener('click', () => { ed.value = EX[sel.value] || EX.shop; go(); });
    $('.sq-go', pane).addEventListener('click', go);
    $('.sq-new', pane).addEventListener('click', () => { fresh(); out.innerHTML = '<div class="sq-ok">A fresh copy of the database is ready.</div>'; });
    sel.addEventListener('change', () => { store.set('sq-pg', { db: sel.value, sql: ed.value }); fresh(); out.innerHTML = ''; });
    const toggle = on => { pane.hidden = !on; btn.classList.toggle('on', on); document.body.classList.toggle('sq-pg-open', on); if (on) { if (!db) fresh(); ed.focus(); } };
    btn.addEventListener('click', () => toggle(pane.hidden));
    $('.sq-x', pane).addEventListener('click', () => toggle(false));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !pane.hidden) toggle(false); });
  }

  function mountAll(root) {
    root.querySelectorAll('.sq-run[data-q]').forEach(mountRun);
    root.querySelectorAll('.sq-lab[data-lab]').forEach(mountLab);
  }
  window.SQ = { ready, open: (name, extra) => ready().then(SQL => open(SQL, name, extra)), openSync: open, run: (db, s) => SQRUN.run(db, s), hl, grid, records, esc, data: DATA };
  function boot() {
    mountAll(document);
    if (document.body.classList.contains('sqlp')) playground();
    if (typeof VIZ !== 'undefined') VIZ.mountAll(document);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
