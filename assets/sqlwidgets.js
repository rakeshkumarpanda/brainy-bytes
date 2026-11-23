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

  /* ---------- 2.1 CASE gives each row a label ---------- */
  SQW('sqcase', (SQL, cfg) => ({
    title: 'CASE labels every row',
    sub: 'Set two price limits. CASE checks the WHEN tests from top to bottom and stops at the first one that is true.',
    inputs: [{ k: 'lo', label: 'Cheap below', type: 'num', val: cfg.lo || 200, w: 90 }, { k: 'hi', label: 'Premium from', type: 'num', val: cfg.hi || 1000, w: 90 }],
    check: v => v.lo >= v.hi ? 'The cheap limit must be smaller than the premium limit.' : '',
    frames: v => {
      const d = db(SQL, 'shop');
      const text = `SELECT name, price,\n  CASE\n    WHEN price < ${v.lo} THEN 'cheap'\n    WHEN price >= ${v.hi} THEN 'premium'\n    ELSE 'regular'\n  END AS band\nFROM products;`;
      const r = q(d, `SELECT name, price, CASE WHEN price < ${+v.lo} THEN 'cheap' WHEN price >= ${+v.hi} THEN 'premium' ELSE 'regular' END FROM products ORDER BY id`);
      const rows = r.rows.map(x => [x[0], x[1], '']);
      const out = [{ msg: 'CASE is SQL’s if, else if, else. Each row gets one label.', mood: 'think', layers: [{ t: 'sql', text }, { t: 'tab', cols: ['name', 'price', 'band'], rows }] }];
      const cls = {};
      r.rows.forEach((x, i) => {
        rows[i] = [x[0], x[1], x[2]];
        const why = x[2] === 'cheap' ? `${x[1]} &lt; ${v.lo}, the first WHEN is true` : x[2] === 'premium' ? `${x[1]} is not below ${v.lo}, but ${x[1]} &gt;= ${v.hi}` : `neither WHEN is true, so ELSE`;
        cls[i + ',2'] = x[2] === 'cheap' ? 'yes' : x[2] === 'premium' ? 'piv' : 'cur';
        out.push({ msg: `<b>${esc(x[0])}</b>: ${why}. Label <b>${x[2]}</b>.`, mood: 'look', layers: [{ t: 'sql', text }, { t: 'tab', cols: ['name', 'price', 'band'], rows: rows.map(z => z.slice()), cls: Object.assign({}, cls), rcls: { [i]: 'look' } }] });
      });
      const n = k => r.rows.filter(x => x[2] === k).length;
      out.push({ msg: `Every row has a label: ${n('cheap')} cheap, ${n('regular')} regular, ${n('premium')} premium.`, mood: 'happy', fx: 'burst', layers: [{ t: 'sql', text }, { t: 'tab', cols: ['name', 'price', 'band'], rows, cls }] });
      return out;
    }
  }));

  /* ---------- 2.2 three valued logic ---------- */
  SQW('sqnull', (SQL, cfg) => ({
    title: 'TRUE, FALSE and the third value: NULL',
    sub: 'Pick A and B. SQLite works out every operator, and Pip finds your pair in the truth tables.',
    inputs: [{ k: 'a', label: 'A', type: 'seg', val: cfg.a || 'NULL', opts: [['TRUE', 'TRUE'], ['FALSE', 'FALSE'], ['NULL', 'NULL']] },
      { k: 'b', label: 'B', type: 'seg', val: cfg.b || 'FALSE', opts: [['TRUE', 'TRUE'], ['FALSE', 'FALSE'], ['NULL', 'NULL']] }],
    frames: v => {
      const d = db(SQL, '');
      const V = ['TRUE', 'FALSE', 'NULL'];
      const word = x => x === null ? 'NULL' : x ? 'TRUE' : 'FALSE';
      const tableFor = op => V.map(a => V.map(b => word(q(d, `SELECT ${a} ${op} ${b}`).rows[0][0])));
      const ai = V.indexOf(v.a), bi = V.indexOf(v.b);
      const and = tableFor('AND'), or = tableFor('OR'), eqt = V.map(a => V.map(b => word(q(d, `SELECT ${a} = ${b}`).rows[0][0])));
      const not = word(q(d, `SELECT NOT ${v.a}`).rows[0][0]);
      const mark = t => ({ t: 'grid', label: t.label, rows: t.rows, rlab: V, clab: V, cls: { [ai + ',' + bi]: t.rows[ai][bi] === 'NULL' ? 'no' : t.rows[ai][bi] === 'TRUE' ? 'yes' : 'cur' } });
      return [
        { msg: 'SQL logic has three values. NULL means <b>unknown</b>: maybe true, maybe false, we cannot tell.', mood: 'think', layers: [{ t: 'grid', label: 'A AND B', rows: and, rlab: V, clab: V }] },
        { msg: `<b>${v.a} AND ${v.b}</b> is <b>${and[ai][bi]}</b>. AND is FALSE as soon as one side is FALSE, because then the unknown side cannot help.`, mood: 'look', layers: [mark({ label: 'A AND B (rows are A, columns are B)', rows: and })] },
        { msg: `<b>${v.a} OR ${v.b}</b> is <b>${or[ai][bi]}</b>. OR is TRUE as soon as one side is TRUE.`, mood: 'look', layers: [mark({ label: 'A OR B', rows: or })] },
        { msg: `<b>NOT ${v.a}</b> is <b>${not}</b>. The opposite of unknown is still unknown.`, mood: 'think', layers: [{ t: 'grid', label: 'NOT A', rows: [V.map(a => word(q(d, `SELECT NOT ${a}`).rows[0][0]))], clab: V, cls: { ['0,' + ai]: not === 'NULL' ? 'no' : 'yes' } }] },
        { msg: `<b>${v.a} = ${v.b}</b> is <b>${eqt[ai][bi]}</b>. Anything compared with NULL, even NULL itself, gives NULL. That is why we write IS NULL.`, mood: eqt[ai][bi] === 'NULL' ? 'wow' : 'happy', fx: 'burst', layers: [mark({ label: 'A = B', rows: eqt })] }
      ];
    }
  }));

  /* ---------- 2.3 GROUP BY puts rows into buckets ---------- */
  SQW('sqgroup', (SQL, cfg) => ({
    title: 'GROUP BY drops rows into buckets',
    sub: 'Choose how to group products and what to work out. Each row falls into the bucket of its value, then one answer comes out per bucket. HAVING can then remove buckets.',
    inputs: [{ k: 'g', label: 'Group by', type: 'seg', val: cfg.g || 'category', opts: [['category', 'category'], ['stock = 0', 'out of stock?']] },
      { k: 'f', label: 'Work out', type: 'seg', val: cfg.f || 'COUNT(*)', opts: [['COUNT(*)', 'COUNT(*)'], ['SUM(stock)', 'SUM(stock)'], ['AVG(price)', 'AVG(price)'], ['MAX(price)', 'MAX(price)']] },
      { k: 'h', label: 'HAVING (optional)', type: 'text', val: cfg.h || '', w: 170 }],
    check: v => v.h && tryq(db(SQL, 'shop'), `SELECT 1 FROM products GROUP BY ${v.g} HAVING ${v.h}`).error ? `SQLite says: ${esc(tryq(db(SQL, 'shop'), `SELECT 1 FROM products GROUP BY ${v.g} HAVING ${v.h}`).error)}` : '',
    frames: v => {
      const d = db(SQL, 'shop');
      const rows = q(d, `SELECT name, ${v.g} FROM products ORDER BY id`).rows;
      const keys = q(d, `SELECT DISTINCT ${v.g} FROM products ORDER BY 1`).rows.map(r => r[0]);
      const lab = keys.map(k => String(k === null ? 'NULL' : v.g === 'stock = 0' ? (k ? 'yes, stock = 0' : 'no') : k));
      const res = q(d, `SELECT ${v.g} AS grp, ${v.f} AS answer${v.h ? `, (${v.h}) AS keep` : ''} FROM products GROUP BY ${v.g} ORDER BY 1`).rows;
      const text = `SELECT ${v.g}, ${v.f}\nFROM products\nGROUP BY ${v.g}${v.h ? `\nHAVING ${v.h}` : ''};`;
      const bk = keys.map(() => []);
      const out = [{ msg: `One empty bucket for each different value of <b>${esc(v.g)}</b>: ${keys.length} buckets.`, mood: 'think', layers: [{ t: 'sql', text }, { t: 'buckets', buckets: bk.map(x => x.slice()), blab: lab }] }];
      rows.forEach((r, i) => {
        const b = keys.findIndex(k => k === r[1]);
        bk[b].push(r[0]);
        out.push({ msg: `<b>${esc(r[0])}</b> goes into the <b>${esc(lab[b])}</b> bucket.`, mood: 'work', layers: [{ t: 'sql', text }, { t: 'buckets', buckets: bk.map(x => x.slice()), blab: lab, cls: { [b + ',' + (bk[b].length - 1)]: 'yes' } }] });
      });
      const ans = keys.map(k => { const row = res.find(r => r[0] === k); const a = row[1]; return typeof a === 'number' && !Number.isInteger(a) ? a.toFixed(2) : a; });
      out.push({ msg: `Now <b>${esc(v.f)}</b> runs once per bucket. One bucket becomes one result row.`, mood: 'wow', fx: 'burst', layers: [{ t: 'sql', text }, { t: 'buckets', buckets: bk, blab: lab.map((l, i) => `${l}: ${ans[i]}`) }] });
      if (v.h) {
        const bcls = {};
        keys.forEach((k, i) => { bcls[i] = res.find(r => r[0] === k)[2] ? 'yes' : 'no'; });
        out.push({ msg: `HAVING <b>${esc(v.h)}</b> tests each bucket, not each row. Red buckets are removed.`, mood: 'look', layers: [{ t: 'sql', text }, { t: 'buckets', buckets: bk, blab: lab.map((l, i) => `${l}: ${ans[i]}`), bcls }] });
      }
      const fin = res.filter(r => !v.h || r[2]).map(r => [r[0] === null ? null : v.g === 'stock = 0' ? r[0] : r[0], typeof r[1] === 'number' && !Number.isInteger(r[1]) ? +r[1].toFixed(2) : r[1]]);
      out.push({ msg: `The result: ${fin.length} ${fin.length === 1 ? 'row' : 'rows'}, one per bucket that survived.`, mood: 'happy', layers: [{ t: 'sql', text }, { t: 'tab', label: 'Result', cols: [v.g, v.f], rows: fin }] });
      return out;
    }
  }));

  /* ---------- 2.3 the logical order of a query ---------- */
  SQW('sqpipe', (SQL, cfg) => ({
    title: 'The order SQL really works in',
    sub: 'You write SELECT first, but the engine starts at FROM. Change the parts and watch the table shrink and change at each stage.',
    inputs: [{ k: 'w', label: 'WHERE', type: 'text', val: cfg.w || "status <> 'cancelled'", w: 200 },
      { k: 'g', label: 'GROUP BY', type: 'seg', val: cfg.g || 'customer_id', opts: [['customer_id', 'customer_id'], ['status', 'status']] },
      { k: 'h', label: 'HAVING', type: 'text', val: cfg.h || 'COUNT(*) >= 2', w: 150 },
      { k: 'n', label: 'LIMIT', type: 'num', val: cfg.n || 2, w: 70 }],
    check: v => { const e = tryq(db(SQL, 'shop'), `SELECT ${v.g}, COUNT(*) FROM orders WHERE ${v.w || '1'} GROUP BY ${v.g} HAVING ${v.h || '1'} LIMIT ${+v.n || 1}`).error; return e ? `SQLite says: ${esc(e)}` : ''; },
    frames: v => {
      const d = db(SQL, 'shop'), W = v.w || '1', H = v.h || '1', N = Math.max(0, +v.n || 0);
      const ST = ['FROM', 'WHERE', 'GROUP BY', 'HAVING', 'SELECT', 'ORDER BY', 'LIMIT'];
      const text = `SELECT ${v.g}, COUNT(*) AS orders\nFROM orders\nWHERE ${W}\nGROUP BY ${v.g}\nHAVING ${H}\nORDER BY orders DESC, ${v.g}\nLIMIT ${N};`;
      const F = (i, msg, t, mood, fx) => ({ msg, mood, fx, layers: [{ t: 'sql', text }, { t: 'flow', items: ST, on: i, done: i - 1 }, t] });
      const all = q(d, 'SELECT * FROM orders'), wh = q(d, `SELECT * FROM orders WHERE ${W}`);
      const gr = q(d, `SELECT ${v.g}, group_concat(id, ' ') AS order_ids FROM orders WHERE ${W} GROUP BY ${v.g}`);
      const hv = q(d, `SELECT ${v.g}, group_concat(id, ' ') AS order_ids FROM orders WHERE ${W} GROUP BY ${v.g} HAVING ${H}`);
      const se = q(d, `SELECT ${v.g}, COUNT(*) AS orders FROM orders WHERE ${W} GROUP BY ${v.g} HAVING ${H}`);
      const ob = q(d, `SELECT ${v.g}, COUNT(*) AS orders FROM orders WHERE ${W} GROUP BY ${v.g} HAVING ${H} ORDER BY orders DESC, ${v.g}`);
      const li = q(d, `SELECT ${v.g}, COUNT(*) AS orders FROM orders WHERE ${W} GROUP BY ${v.g} HAVING ${H} ORDER BY orders DESC, ${v.g} LIMIT ${N}`);
      return [
        F(0, `1. <b>FROM</b> picks the table: all ${all.rows.length} orders.`, { t: 'tab', cols: all.cols, rows: all.rows }, 'look'),
        F(1, `2. <b>WHERE</b> keeps rows where ${esc(W)} is true: ${wh.rows.length} left.`, { t: 'tab', cols: wh.cols, rows: wh.rows }, 'look'),
        F(2, `3. <b>GROUP BY</b> ${v.g} folds the rows into ${gr.rows.length} groups.`, { t: 'tab', cols: gr.cols, rows: gr.rows }, 'work'),
        F(3, `4. <b>HAVING</b> keeps groups where ${esc(H)}: ${hv.rows.length} left.`, { t: 'tab', cols: hv.cols, rows: hv.rows }, 'look'),
        F(4, '5. <b>SELECT</b> finally works out the columns, including COUNT(*) and the alias orders.', { t: 'tab', cols: se.cols, rows: se.rows }, 'wow'),
        F(5, '6. <b>ORDER BY</b> sorts. It runs after SELECT, so it may use the alias orders.', { t: 'tab', cols: ob.cols, rows: ob.rows }, 'look'),
        F(6, `7. <b>LIMIT</b> ${N} keeps the first ${N}. Done.`, { t: 'tab', cols: li.cols, rows: li.rows }, 'happy', 'burst')
      ];
    }
  }));
})();
