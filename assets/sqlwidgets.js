/* ===== Playful step animations for the SQL chapters (tools/sql-build/build.py) =====
   Each widget is a PK.widget (assets/playkit.js) on the shared VIZ player, so Play, Step, Reset, speed and
   voice teaching work like every other animation. The difference: the pictures are worked out by the real SQLite
   (sql.js, through window.SQ), so whatever the reader types is answered by the same engine as the SQL blocks.

   SQW(name, (SQL, cfg) => options)   registers PK.defs[name]. cfg comes from the data-cfg of the placeholder.
   Extra layer:  {t: 'tab', label, cols, rows, ccls: {col: cls}, rcls: {row: cls}, cls: {'r,c': cls}, tag: {row: text}, keys}
   Extra layer:  {t: 'flow', items: [text...], on: index, done: index}   a row of stages
   Extra layer:  {t: 'sql', text}                                       the statement being explained
*/
(() => {
  if (typeof PK === 'undefined' || typeof SQ === 'undefined') return;
  const esc = SQ.esc;
  const D = PK.draw;

  D.tab = L => {
    const ccls = L.ccls || {}, rcls = L.rcls || {}, cls = L.cls || {}, tag = L.tag || {};
    const head = `<tr>${L.cols.map((c, ci) => `<th class="${ccls[ci] || ''}">${esc(c)}</th>`).join('')}${L.tag ? '<th class="sqw-tg"></th>' : ''}</tr>`;
    const body = L.rows.map((r, ri) => `<tr class="${rcls[ri] || ''}"${L.keys ? ` data-fk="${esc((L.id || 't') + ':' + L.keys[ri])}"` : ''}>${r.map((v, ci) => `<td class="${[ccls[ci], cls[ri + ',' + ci], v === null ? 'nul' : ''].filter(Boolean).join(' ')}">${v === null ? 'NULL' : esc(v)}</td>`).join('')}${L.tag ? `<td class="sqw-tg">${tag[ri] !== undefined ? esc(tag[ri]) : ''}</td>` : ''}</tr>`).join('');
    const none = L.rows.length ? '' : `<tr><td colspan="${L.cols.length || 1}" class="sq-none">no rows yet</td></tr>`;
    return `${L.label ? `<div class="pk-lab">${L.label}</div>` : ''}<div class="pk-gw"><table class="pk-grid sqw-t">${head}${body}${none}</table></div>`;
  };
  D.flow = L => `<div class="sqw-flow">${L.items.map((t, i) => `${i ? '<i>›</i>' : ''}<span class="${i === L.on ? 'on' : i <= (L.done === undefined ? -1 : L.done) ? 'done' : ''}">${esc(t)}</span>`).join('')}</div>`;
  D.sql = L => `<pre class="sqw-sql">${SQ.hl(L.text)}</pre>`;

  const DBS = {};
  function db(SQL, name) {            /* one read only copy of each sample database for the animations */
    if (!DBS[name]) DBS[name] = SQ.openSync(SQL, name);
    return DBS[name];
  }
  /* one statement only (prepare ignores anything after the first), so typed input cannot change the shared copy */
  function q(d, sql) {
    if (/^\s*(insert|update|delete|drop|create|alter|replace|pragma|attach|vacuum)\b/i.test(sql)) throw new Error('only queries can run in this animation');
    const st = d.prepare(sql);
    const cols = st.getColumnNames(), rows = [];
    try { while (st.step()) rows.push(st.get()); } finally { st.free(); }
    return { cols, rows };
  }
  function tryq(d, sql) {
    try { return q(d, sql); } catch (e) { return { error: String(e.message || e) }; }
  }
  const tableOpts = names => names.map(n => [n, n]);
  window.SQW = function SQW(name, make) {
    PK.defs[name] = el => {
      el.innerHTML = '<div class="sq-cnt">Loading SQLite for this animation...</div>';
      SQ.ready().then(SQL => {
        let cfg = {};
        try { cfg = el.dataset.cfg ? JSON.parse(el.dataset.cfg) : {}; } catch (e) { cfg = {}; }
        PK.widget(el, make(SQL, cfg));
      }).catch(e => { el.textContent = 'This animation needs SQLite, which could not load: ' + e.message; });
    };
  };
  const SQWX = { db, q, tryq };
  window.SQWX = SQWX;

  /* ---------- 1.1 a table, piece by piece ---------- */
  SQW('sqanatomy', (SQL, cfg) => ({
    title: 'Meet a table, one piece at a time',
    sub: 'Pick a table from the Bytes Bazaar shop. Pip points at each part and names it.',
    inputs: [{ k: 't', label: 'Table', type: 'seg', val: cfg.t || 'customers', opts: tableOpts(['customers', 'products', 'orders']) }],
    frames: v => {
      const d = db(SQL, 'shop');
      const { cols, rows } = q(d, `SELECT * FROM ${v.t}`);
      const T = (extra, msg, mood, say) => ({ msg, mood, say, layers: [Object.assign({ t: 'tab', label: `The <b>${v.t}</b> table`, cols, rows }, extra)] });
      let nr = -1, nc = -1;
      rows.forEach((r, ri) => r.forEach((x, ci) => { if (x === null && nr < 0) { nr = ri; nc = ci; } }));
      const out = [
        { msg: `Here is a whole table. It has a name, <b>${v.t}</b>, and it looks like a page in a school register.`, mood: 'idle', layers: [{ t: 'tab', label: `The <b>${v.t}</b> table`, cols, rows }] },
        T({ ccls: Object.fromEntries(cols.map((_, i) => [i, 'look'])), rcls: Object.fromEntries(rows.map((_, i) => [i, 'hd'])) }, `The top line holds the <b>column names</b>: ${cols.join(', ')}. Every column keeps one kind of fact.`, 'look'),
        T({ ccls: { 1: 'look' } }, `One column, <b>${cols[1]}</b>, runs top to bottom. Every value in it is the same kind of thing.`, 'look'),
        T({ rcls: { 2: 'cur' } }, `One <b>row</b> runs left to right. It is one record: everything we know about one ${v.t === 'customers' ? 'customer' : v.t === 'products' ? 'product' : 'order'}.`, 'look'),
        T({ cls: { '2,1': 'yes' } }, `Where a row meets a column you get one <b>cell</b>, holding one value: <b>${rows[2][1]}</b>.`, 'happy', undefined),
        T({ ccls: { 0: 'piv' } }, `The <b>${cols[0]}</b> column is the <b>primary key</b>. No two rows share an ${cols[0]}, so it names each row exactly.`, 'wow')
      ];
      if (nr >= 0) out.push(T({ cls: { [nr + ',' + nc]: 'no' } }, `This cell shows <b>NULL</b>. NULL means the value is missing or unknown. It is not zero and not an empty word.`, 'think'));
      out.push(T({}, `Count them: <b>${rows.length} rows</b> and <b>${cols.length} columns</b>. A real shop has millions of rows, but the shape stays the same.`, 'happy'));
      out[out.length - 1].fx = 'burst';
      return out;
    }
  }));

  /* ---------- 1.4 the journey of one query ---------- */
  SQW('sqtrip', (SQL, cfg) => ({
    title: 'The journey of one query',
    sub: 'Type any query on the shop database. Watch it pass through the parser, the planner and the executor of the real SQLite.',
    inputs: [{ k: 'sql', label: 'Your query', type: 'text', val: cfg.sql || "SELECT name, price FROM products WHERE price < 200", w: 460 }],
    frames: v => {
      const d = db(SQL, 'shop');
      const STG = ['You', 'Parser', 'Planner', 'Executor', 'Result'];
      const F = (on, msg, mood, more, fx) => ({ msg, mood, fx, layers: [{ t: 'sql', text: v.sql }, { t: 'flow', items: STG, on, done: on - 1 }].concat(more || []) });
      const out = [F(0, 'You write what you want, not how to get it. SQL is a <b>declarative</b> language.', 'idle')];
      const plan = tryq(d, 'EXPLAIN QUERY PLAN ' + v.sql);
      if (plan.error) {
        out.push(F(1, `The <b>parser</b> reads your words like a teacher checking grammar, and stops here: <b>${esc(plan.error)}</b>. Fix it and press Show me again.`, 'sad', [], 'shake'));
        return out;
      }
      out.push(F(1, 'The <b>parser</b> checks the grammar and the names. Every table and column you used exists, so it turns your text into a tree the engine understands.', 'look'));
      out.push(F(2, 'The <b>planner</b> (also called the optimizer) chooses how to find the rows. Here is its real plan:', 'think',
        [{ t: 'note', html: '<b>EXPLAIN QUERY PLAN</b><br>' + (plan.rows.map(r => esc(r[3])).join('<br>') || 'a constant, no table to read') }]));
      const res = tryq(d, v.sql);
      if (res.error) { out.push(F(3, `The <b>executor</b> started but stopped: <b>${esc(res.error)}</b>`, 'sad', [], 'shake')); return out; }
      out.push(F(3, `The <b>executor</b> follows the plan step by step, reading rows and keeping the ones that fit.`, 'work'));
      out.push(F(4, `Done. <b>${res.rows.length}</b> ${res.rows.length === 1 ? 'row comes' : 'rows come'} back to you as a new little table.`, 'happy',
        [{ t: 'tab', label: 'Result', cols: res.cols, rows: res.rows.slice(0, 12) }], 'burst'));
      return out;
    }
  }));

  /* ---------- 1.2 SELECT picks columns ---------- */
  SQW('sqselect', (SQL, cfg) => ({
    title: 'SELECT picks the columns you ask for',
    sub: 'Type a list of columns, or *. Pip lights up each column you named, then copies them into the result.',
    inputs: [{ k: 't', label: 'Table', type: 'seg', val: cfg.t || 'products', opts: tableOpts(['products', 'customers']) },
      { k: 'c', label: 'Columns', type: 'text', val: cfg.c || 'name, price', w: 240 }],
    check: v => {
      const r = tryq(db(SQL, 'shop'), `SELECT ${v.c} FROM ${v.t} LIMIT 0`);
      return r.error ? `SQLite says: ${esc(r.error)}. Use column names from the table, separated by commas.` : '';
    },
    frames: v => {
      const d = db(SQL, 'shop');
      const all = q(d, `SELECT * FROM ${v.t}`), res = q(d, `SELECT ${v.c} FROM ${v.t}`);
      const low = all.cols.map(c => c.toLowerCase());
      const out = [{ msg: `The query is <b>SELECT ${esc(v.c)} FROM ${v.t}</b>. First SQLite finds the table named after FROM.`, mood: 'look', layers: [{ t: 'sql', text: `SELECT ${v.c}\nFROM ${v.t};` }, { t: 'tab', label: v.t, cols: all.cols, rows: all.rows }] }];
      const picked = [];
      res.cols.forEach((c, k) => {
        const i = low.indexOf(c.toLowerCase());
        if (i >= 0) picked.push(i);
        out.push({ msg: i >= 0 ? `Column ${k + 1} of the result is <b>${esc(c)}</b>. Found it in the table.` : `<b>${esc(c)}</b> is not a stored column. SQLite works it out for every row: a calculated column.`, mood: i >= 0 ? 'happy' : 'wow',
          layers: [{ t: 'sql', text: `SELECT ${v.c}\nFROM ${v.t};` }, { t: 'tab', label: v.t, cols: all.cols, rows: all.rows, ccls: Object.fromEntries(all.cols.map((_, j) => [j, j === i ? 'look' : picked.includes(j) ? 'yes' : ''])) }] });
      });
      out.push({ msg: `The result keeps every row but only the columns you asked for, in your order. ${res.cols.length} ${res.cols.length === 1 ? 'column' : 'columns'}, ${res.rows.length} rows.`, mood: 'happy', fx: 'burst',
        layers: [{ t: 'sql', text: `SELECT ${v.c}\nFROM ${v.t};` }, { t: 'tab', label: 'Result', cols: res.cols, rows: res.rows }] });
      return out;
    }
  }));

  /* ---------- 1.3 WHERE checks every row ---------- */
  SQW('sqwhere', (SQL, cfg) => ({
    title: 'WHERE checks every row, one by one',
    sub: 'Type a condition. Pip tests each row: green rows pass, red rows are thrown out, and a NULL answer counts as not passing.',
    inputs: [{ k: 't', label: 'Table', type: 'seg', val: cfg.t || 'products', opts: tableOpts(['products', 'customers']) },
      { k: 'w', label: 'WHERE', type: 'text', val: cfg.w || 'price < 300', w: 280 }],
    random: () => ({ w: ['price < 300', "category = 'Sports'", 'stock = 0', "price BETWEEN 100 AND 700", "name LIKE '%box%'"][Math.floor(Math.random() * 5)] }),
    check: v => {
      const r = tryq(db(SQL, 'shop'), `SELECT 1 FROM ${v.t} WHERE ${v.w} LIMIT 0`);
      return r.error ? `SQLite says: ${esc(r.error)}. Try something like price &lt; 300 or city = 'Pune'.` : '';
    },
    frames: v => {
      const d = db(SQL, 'shop');
      const all = q(d, `SELECT * FROM ${v.t}`);
      const test = q(d, `SELECT (${v.w}) FROM ${v.t}`).rows.map(r => r[0]);
      const text = `SELECT *\nFROM ${v.t}\nWHERE ${v.w};`;
      const rc = {}, tag = {};
      const out = [{ msg: `Every row will be tested with <b>${esc(v.w)}</b>. Only rows where it is true stay.`, mood: 'think', layers: [{ t: 'sql', text }, { t: 'tab', label: v.t, cols: all.cols, rows: all.rows, tag: {} }] }];
      all.rows.forEach((r, i) => {
        const t = test[i];
        const word = t === null ? 'NULL, so it is thrown out' : t ? 'true, keep it' : 'false, throw it out';
        out.push({ msg: `Row ${i + 1} (${esc(r[1])}): the test gives <b>${word}</b>.`, mood: 'look', layers: [{ t: 'sql', text }, { t: 'tab', label: v.t, cols: all.cols, rows: all.rows, rcls: Object.assign({}, rc, { [i]: 'look' }), tag: Object.assign({}, tag) }] });
        rc[i] = t ? 'yes' : 'no';
        tag[i] = t === null ? 'NULL' : t ? 'keep' : 'drop';
        out.push({ msg: t ? `<b>${esc(r[1])}</b> passes.` : t === null ? `<b>${esc(r[1])}</b> has a missing value, the test is unknown, so the row does not pass.` : `<b>${esc(r[1])}</b> does not pass.`, mood: t ? 'happy' : 'sad',
          layers: [{ t: 'sql', text }, { t: 'tab', label: v.t, cols: all.cols, rows: all.rows, rcls: Object.assign({}, rc), tag: Object.assign({}, tag) }] });
      });
      const keep = all.rows.filter((_, i) => test[i]);
      out.push({ msg: keep.length ? `Finished. ${keep.length} of ${all.rows.length} rows passed the test.` : 'Finished. No row passed, so the result is empty. That is a normal answer, not an error.', mood: keep.length ? 'wow' : 'sad', fx: keep.length ? 'burst' : 'shake',
        layers: [{ t: 'sql', text }, { t: 'tab', label: 'Result', cols: all.cols, rows: keep }] });
      return out;
    }
  }));

  /* ---------- 1.3 ORDER BY sorts the rows ---------- */
  SQW('sqorder', (SQL, cfg) => ({
    title: 'ORDER BY lines the rows up',
    sub: 'Pick a column and a direction. Rows slide into their new places. Ties keep no promised order unless you add a second column.',
    inputs: [{ k: 'c', label: 'Sort by', type: 'seg', val: cfg.c || 'price', opts: [['price', 'price'], ['name', 'name'], ['category', 'category'], ['stock', 'stock']] },
      { k: 'dir', label: 'Direction', type: 'seg', val: cfg.dir || 'ASC', opts: [['ASC', 'ASC (small first)'], ['DESC', 'DESC (big first)']] }],
    frames: v => {
      const d = db(SQL, 'shop');
      const a = q(d, 'SELECT id, name, category, price, stock FROM products ORDER BY id');
      const b = q(d, `SELECT id, name, category, price, stock FROM products ORDER BY ${v.c} ${v.dir}, id`);
      const ci = a.cols.indexOf(v.c);
      const text = `SELECT id, name, category, price, stock\nFROM products\nORDER BY ${v.c} ${v.dir};`;
      return [
        { msg: 'Without ORDER BY, SQL promises no order at all. Here the rows happen to come out by id.', mood: 'idle', layers: [{ t: 'sql', text }, { t: 'tab', label: 'Before', cols: a.cols, rows: a.rows, keys: a.rows.map(r => r[0]), id: 'o' }] },
        { msg: `SQLite compares the <b>${v.c}</b> values.`, mood: 'look', layers: [{ t: 'sql', text }, { t: 'tab', label: 'Before', cols: a.cols, rows: a.rows, keys: a.rows.map(r => r[0]), id: 'o', ccls: { [ci]: 'look' } }] },
        { msg: `Sorted ${v.dir === 'ASC' ? 'from smallest to biggest' : 'from biggest to smallest'}${v.c === 'name' || v.c === 'category' ? ' (for words that means A to Z order' + (v.dir === 'DESC' ? ', backwards' : '') + ')' : ''}.`, mood: 'happy', fx: 'burst',
          layers: [{ t: 'sql', text }, { t: 'tab', label: 'After', cols: b.cols, rows: b.rows, keys: b.rows.map(r => r[0]), id: 'o', ccls: { [ci]: 'yes' } }] }
      ];
    }
  }));

  /* ---------- 1.3 LIKE patterns ---------- */
  SQW('sqlike', (SQL, cfg) => ({
    title: 'LIKE matches patterns',
    sub: '% stands for any run of characters (even none). _ stands for exactly one character. Try your own pattern.',
    inputs: [{ k: 'p', label: 'Pattern', type: 'text', val: cfg.p || '%box%', w: 160 }],
    random: () => ({ p: ['%box%', 'P%', '%l', '_o%', '%e_', '____ %'][Math.floor(Math.random() * 6)] }),
    frames: v => {
      const d = db(SQL, 'shop');
      const pat = v.p.replace(/'/g, "''");
      const r = q(d, `SELECT name, name LIKE '${pat}' FROM products ORDER BY id`);
      const names = r.rows.map(x => x[0]);
      const cls = {};
      const text = `SELECT name\nFROM products\nWHERE name LIKE '${v.p}';`;
      const out = [{ msg: `The pattern is <b>${esc(v.p)}</b>. LIKE ignores upper and lower case for plain English letters.`, mood: 'think', layers: [{ t: 'sql', text }, { t: 'row', label: 'Product names', cells: names, idx: false }] }];
      r.rows.forEach((x, i) => {
        out.push({ msg: `<b>${esc(x[0])}</b> ${x[1] ? 'fits the pattern' : 'does not fit'}.`, mood: x[1] ? 'happy' : 'sad', layers: [{ t: 'sql', text }, { t: 'row', label: 'Product names', cells: names, idx: false, cls: Object.assign({}, cls, { [i]: 'look' }) }] });
        cls[i] = x[1] ? 'yes' : 'no';
      });
      const n = r.rows.filter(x => x[1]).length;
      out.push({ msg: `${n} ${n === 1 ? 'name matches' : 'names match'} <b>${esc(v.p)}</b>.`, mood: n ? 'wow' : 'sad', fx: n ? 'burst' : 'shake', layers: [{ t: 'sql', text }, { t: 'row', label: 'Product names', cells: names, idx: false, cls }] });
      return out;
    }
  }));
})();
