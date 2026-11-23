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

  /* ---------- 3.1 a foreign key points at a parent row ---------- */
  SQW('sqlink', (SQL, cfg) => ({
    title: 'Follow the foreign key',
    sub: 'Pick an order. Its customer_id points at exactly one row of customers, the way a roll number points at one student.',
    inputs: [{ k: 'o', label: 'Order id', type: 'seg', val: String(cfg.o || 103), opts: ['101', '103', '105', '107', '110'].map(x => [x, x]) }],
    frames: v => {
      const d = db(SQL, 'shop');
      const o = q(d, 'SELECT id, customer_id, order_date, status FROM orders ORDER BY id'), c = q(d, 'SELECT id, name, city FROM customers ORDER BY id');
      const oi = o.rows.findIndex(r => String(r[0]) === v.o), cid = o.rows[oi][1], ci = c.rows.findIndex(r => r[0] === cid);
      const two = (ol, cl) => [{ t: 'tab', label: 'orders (child)', cols: o.cols, rows: o.rows, ...ol }, { t: 'tab', label: 'customers (parent)', cols: c.cols, rows: c.rows, ...cl }];
      const kids = o.rows.map((r, i) => r[1] === cid ? i : -1).filter(i => i >= 0);
      return [
        { msg: `Order <b>${v.o}</b> does not store the customer’s name. It stores only <b>customer_id = ${cid}</b>.`, mood: 'look', layers: two({ rcls: { [oi]: 'look' }, cls: { [oi + ',1']: 'piv' } }, {}) },
        { msg: `Follow the number to customers.id = ${cid}. That row is <b>${esc(c.rows[ci][1])}</b> from ${esc(c.rows[ci][2] || 'an unknown city')}.`, mood: 'happy', fx: 'burst', layers: two({ rcls: { [oi]: 'look' }, cls: { [oi + ',1']: 'piv' } }, { rcls: { [ci]: 'yes' }, cls: { [ci + ',0']: 'piv' } }) },
        { msg: `The link works backwards too: ${esc(c.rows[ci][1])} has <b>${kids.length}</b> ${kids.length === 1 ? 'order' : 'orders'}. One customer, many orders: a <b>one to many</b> relationship.`, mood: 'wow', layers: two({ rcls: Object.fromEntries(kids.map(i => [i, 'yes'])) }, { rcls: { [ci]: 'yes' } }) },
        { msg: 'The name lives in one place only. If the customer changes their name, one row changes, and every order shows the new name. That is why we link instead of copying.', mood: 'happy', layers: two({}, { rcls: { [ci]: 'cur' } }) }
      ];
    }
  }));

  /* ---------- 3.2 joins pair rows ---------- */
  SQW('sqjoin', (SQL, cfg) => ({
    title: 'How a JOIN pairs rows',
    sub: 'Pick a join type. Pip takes each customer, looks for matching orders, and builds the result row by row. Unmatched rows show NULLs.',
    inputs: [{ k: 'j', label: 'Join', type: 'seg', val: cfg.j || 'INNER', opts: [['INNER', 'INNER'], ['LEFT', 'LEFT'], ['RIGHT', 'RIGHT'], ['FULL', 'FULL']] }],
    frames: v => {
      const d = db(SQL, 'shop');
      const L = q(d, 'SELECT id, name FROM customers WHERE id IN (1, 4, 5, 7) ORDER BY id').rows;
      const R = q(d, "SELECT id, customer_id FROM orders WHERE id IN (101, 103, 105, 106, 107) ORDER BY id").rows.concat([[120, 9]]);
      const text = `SELECT c.name, o.id AS order_id\nFROM customers AS c\n${v.j} JOIN orders AS o ON o.customer_id = c.id;`;
      const res = [], rused = new Set();
      const lay = (lc, rc, msg, mood, fx) => ({ msg, mood, fx, layers: [{ t: 'sql', text }, { t: 'note', html: 'Small sample: 4 customers and 6 orders (order 120 points at customer 9, who does not exist, to show RIGHT and FULL joins).' },
        { t: 'tab', label: 'customers c', cols: ['id', 'name'], rows: L, rcls: lc }, { t: 'tab', label: 'orders o', cols: ['id', 'customer_id'], rows: R, rcls: rc }, { t: 'tab', label: 'Result', cols: ['name', 'order_id'], rows: res.slice() }] });
      const out = [lay({}, {}, `A <b>${v.j} JOIN</b> compares every customer with every order using the ON test: o.customer_id = c.id.`, 'think')];
      L.forEach((l, i) => {
        const m = R.map((r, k) => r[1] === l[0] ? k : -1).filter(k => k >= 0);
        m.forEach(k => { res.push([l[1], R[k][0]]); rused.add(k); });
        if (m.length) out.push(lay({ [i]: 'yes' }, Object.fromEntries(m.map(k => [k, 'yes'])), `<b>${esc(l[1])}</b> (id ${l[0]}) matches ${m.length} ${m.length === 1 ? 'order' : 'orders'}: ${m.map(k => R[k][0]).join(', ')}. Each match makes one result row.`, 'happy'));
        else {
          if (v.j === 'LEFT' || v.j === 'FULL') res.push([l[1], null]);
          out.push(lay({ [i]: 'no' }, {}, `<b>${esc(l[1])}</b> has no order. ${v.j === 'LEFT' || v.j === 'FULL' ? 'A ' + v.j + ' JOIN keeps every left row, so we add it with NULL for the order.' : 'An ' + v.j + ' JOIN drops a left row with no match.'}`, v.j === 'LEFT' || v.j === 'FULL' ? 'wow' : 'sad'));
        }
      });
      const lone = R.map((r, k) => rused.has(k) ? -1 : k).filter(k => k >= 0);
      if (lone.length) {
        if (v.j === 'RIGHT' || v.j === 'FULL') lone.forEach(k => res.push([null, R[k][0]]));
        out.push(lay({}, Object.fromEntries(lone.map(k => [k, 'no'])), `Orders with no matching customer: ${lone.map(k => R[k][0]).join(', ')}. ${v.j === 'RIGHT' || v.j === 'FULL' ? 'A ' + v.j + ' JOIN keeps them, with NULL for the name.' : 'This join leaves them out.'}`, v.j === 'RIGHT' || v.j === 'FULL' ? 'wow' : 'sad'));
      }
      out.push(lay({}, {}, `Done: ${res.length} result rows for ${v.j} JOIN.`, 'happy', 'burst'));
      return out;
    }
  }));

  /* ---------- 3.3 a correlated subquery runs once per outer row ---------- */
  SQW('sqexists', (SQL, cfg) => ({
    title: 'EXISTS asks a question for every row',
    sub: 'For each customer the inner query runs again with that customer’s id. EXISTS is true as soon as one row comes back.',
    inputs: [{ k: 'neg', label: 'Test', type: 'seg', val: cfg.neg || 'EXISTS', opts: [['EXISTS', 'EXISTS'], ['NOT EXISTS', 'NOT EXISTS']] }],
    frames: v => {
      const d = db(SQL, 'shop');
      const C = q(d, 'SELECT id, name FROM customers ORDER BY id').rows;
      const text = `SELECT c.name\nFROM customers AS c\nWHERE ${v.neg} (\n  SELECT 1 FROM orders AS o\n  WHERE o.customer_id = c.id\n);`;
      const rc = {}, keep = [];
      const out = [{ msg: 'The inner query mentions <b>c.id</b> from the outer query. That makes it a <b>correlated</b> subquery: it depends on the current outer row.', mood: 'think', layers: [{ t: 'sql', text }, { t: 'tab', label: 'customers', cols: ['id', 'name'], rows: C }] }];
      C.forEach((c, i) => {
        const n = q(d, `SELECT count(*) FROM orders WHERE customer_id = ${c[0]}`).rows[0][0];
        const pass = v.neg === 'EXISTS' ? n > 0 : n === 0;
        rc[i] = pass ? 'yes' : 'no';
        if (pass) keep.push([c[1]]);
        out.push({ msg: `For <b>${esc(c[1])}</b> the inner query looks for orders with customer_id = ${c[0]} and finds ${n ? 'at least one' : 'none'}. ${v.neg} is <b>${pass ? 'true' : 'false'}</b>.`, mood: pass ? 'happy' : 'sad',
          layers: [{ t: 'sql', text: text.replace(/c\.id/, String(c[0])) }, { t: 'tab', label: 'customers', cols: ['id', 'name'], rows: C, rcls: Object.assign({}, rc) }] });
      });
      out.push({ msg: `${keep.length} customers pass. EXISTS stops at the first match, so it never needs to count all the orders.`, mood: 'wow', fx: 'burst', layers: [{ t: 'sql', text }, { t: 'tab', label: 'Result', cols: ['name'], rows: keep }] });
      return out;
    }
  }));

  /* ---------- 3.4 set operations ---------- */
  SQW('sqset', (SQL, cfg) => ({
    title: 'UNION, INTERSECT and EXCEPT',
    sub: 'Two lists of cities: where customers live, and where we have a warehouse. Pick an operator and see which cities survive.',
    inputs: [{ k: 'op', label: 'Operator', type: 'seg', val: cfg.op || 'UNION', opts: [['UNION', 'UNION'], ['UNION ALL', 'UNION ALL'], ['INTERSECT', 'INTERSECT'], ['EXCEPT', 'EXCEPT']] }],
    frames: v => {
      const d = db(SQL, 'shop');
      const A = q(d, 'SELECT city FROM customers WHERE city IS NOT NULL ORDER BY id').rows.map(r => r[0]);
      const B = q(d, 'SELECT city FROM warehouses ORDER BY rowid').rows.map(r => r[0]);
      const res = q(d, `SELECT city FROM customers WHERE city IS NOT NULL ${v.op} SELECT city FROM warehouses`).rows.map(r => r[0]);
      const sa = new Set(res), inB = new Set(B), inA = new Set(A);
      const text = `SELECT city FROM customers WHERE city IS NOT NULL\n${v.op}\nSELECT city FROM warehouses;`;
      const why = { 'UNION': 'every city from either list, each only once', 'UNION ALL': 'everything from both lists, repeats kept', 'INTERSECT': 'only cities in both lists', 'EXCEPT': 'cities in the first list that are not in the second' }[v.op];
      return [
        { msg: 'Two queries with the same number of columns can be stacked with a set operator.', mood: 'think', layers: [{ t: 'sql', text }, { t: 'row', label: 'Customer cities (first query)', cells: A, idx: false }, { t: 'row', label: 'Warehouse cities (second query)', cells: B, idx: false }] },
        { msg: `${v.op} keeps ${why}.`, mood: 'look', layers: [{ t: 'sql', text }, { t: 'row', label: 'Customer cities', cells: A, idx: false, cls: Object.fromEntries(A.map((c, i) => [i, sa.has(c) ? 'yes' : 'no'])) }, { t: 'row', label: 'Warehouse cities', cells: B, idx: false, cls: Object.fromEntries(B.map((c, i) => [i, sa.has(c) ? 'yes' : 'no'])) }] },
        { msg: `Result: ${res.length} ${res.length === 1 ? 'row' : 'rows'}${v.op === 'UNION ALL' ? ', repeats and all' : v.op === 'UNION' ? ', duplicates removed' : ''}.`, mood: 'happy', fx: 'burst', layers: [{ t: 'sql', text }, { t: 'row', label: 'Result', cells: res, idx: false, cls: Object.fromEntries(res.map((c, i) => [i, inA.has(c) && inB.has(c) ? 'piv' : 'yes'])) }] }
      ];
    }
  }));

  /* a fresh writable copy for widgets that change data, thrown away after each run */
  function scratch(SQL, name, extra) { return SQ.openSync(SQL, name, extra); }
  function err(d, sql) { try { d.exec(sql); return ''; } catch (e) { return String(e.message || e); } }

  /* ---------- 4.1 constraints guard the door ---------- */
  SQW('sqcheck', (SQL, cfg) => ({
    title: 'Constraints check every new row',
    sub: 'The members table has rules. Type a new member and watch each rule test the row before SQLite lets it in. Try a missing name, a repeated email or an age under 18.',
    inputs: [{ k: 'name', label: 'name', type: 'text', val: cfg.name !== undefined ? cfg.name : 'Kiran', w: 110 },
      { k: 'email', label: 'email', type: 'text', val: cfg.email || 'kiran@mail.in', w: 150 },
      { k: 'age', label: 'age', type: 'text', val: cfg.age || '21', w: 70 }],
    frames: v => {
      const DDL = `CREATE TABLE members (\n  id    INTEGER PRIMARY KEY,\n  name  TEXT NOT NULL,\n  email TEXT UNIQUE,\n  age   INTEGER CHECK (age >= 18)\n) STRICT;`;
      const seed = "INSERT INTO members (name, email, age) VALUES ('Asha', 'asha@mail.in', 30), ('Ravi', 'ravi@mail.in', 24);";
      const d = scratch(SQL, '', DDL + seed);
      const lit = x => x.trim() === '' ? 'NULL' : /^-?\d+$/.test(x.trim()) ? x.trim() : `'${x.replace(/'/g, "''")}'`;
      const ins = `INSERT INTO members (name, email, age)\nVALUES (${lit(v.name)}, ${lit(v.email)}, ${lit(v.age)});`;
      const before = q(d, 'SELECT * FROM members');
      const nm = v.name.trim(), em = v.email.trim(), ag = v.age.trim();
      const dup = em && before.rows.some(r => r[2] === em);
      const isInt = ag === '' || /^-?\d+$/.test(ag);
      const tests = [
        ['STRICT type check', isInt, isInt ? 'age is a whole number (or empty), so it fits INTEGER.' : `"${esc(ag)}" is not a whole number, and a STRICT table refuses it.`],
        ['name NOT NULL', nm !== '', nm ? `name is "${esc(nm)}", so it is not NULL.` : 'name is empty, which we send as NULL. NOT NULL says no.'],
        ['email UNIQUE', !dup, dup ? `${esc(em)} already belongs to another member.` : 'No other member has this email.'],
        ['CHECK (age >= 18)', !isInt || ag === '' || +ag >= 18, ag === '' ? 'age is NULL. A CHECK that is unknown counts as passed.' : isInt ? `${ag} >= 18 is ${+ag >= 18 ? 'true' : 'false'}.` : 'skipped, the type check already failed.']
      ];
      const e = err(d, ins);
      const after = q(d, 'SELECT * FROM members');
      const out = [{ msg: 'These rules live in the table definition, so every program that writes to the table must obey them.', mood: 'think', layers: [{ t: 'sql', text: DDL }, { t: 'tab', label: 'members now', cols: before.cols, rows: before.rows }] },
        { msg: 'Your new row asks to come in.', mood: 'look', layers: [{ t: 'sql', text: ins }, { t: 'tab', label: 'members now', cols: before.cols, rows: before.rows }] }];
      tests.forEach((t, i) => out.push({ msg: `<b>${t[0]}</b>: ${t[2]}`, mood: t[1] ? 'happy' : 'sad', layers: [{ t: 'sql', text: ins }, { t: 'flow', items: tests.map(x => x[0]), on: i, done: i - 1 }] }));
      out.push(e ? { msg: `SQLite refuses the row and says: <b>${esc(e)}</b>. The table is unchanged.`, mood: 'sad', layers: [{ t: 'sql', text: ins }, { t: 'tab', label: 'members', cols: after.cols, rows: after.rows }] }
        : { msg: 'Every rule passed, so the row is stored. SQLite also gave it the next id by itself.', mood: 'happy', fx: 'burst', layers: [{ t: 'sql', text: ins }, { t: 'tab', label: 'members', cols: after.cols, rows: after.rows, rcls: { [after.rows.length - 1]: 'yes' } }] });
      return out;
    }
  }));

  /* ---------- 4.2 UPDATE and DELETE touch the rows WHERE picks ---------- */
  SQW('sqdml', (SQL, cfg) => ({
    title: 'WHERE decides which rows change',
    sub: 'Pick a change and a WHERE test. Pip marks the rows the test picks, then runs the statement on a throwaway copy of products. Clear the WHERE box to see why people fear a missing WHERE.',
    inputs: [{ k: 'a', label: 'Change', type: 'seg', val: cfg.a || 'UPDATE', opts: [['UPDATE', 'UPDATE price + 10%'], ['DELETE', 'DELETE']] },
      { k: 'w', label: 'WHERE', type: 'text', val: cfg.w !== undefined ? cfg.w : "category = 'Kitchen'", w: 200 }],
    check: v => { const e = tryq(db(SQL, 'shop'), `SELECT 1 FROM products${v.w.trim() ? ' WHERE ' + v.w : ''}`).error; return e ? `SQLite says: ${esc(e)}` : ''; },
    frames: v => {
      const W = v.w.trim();
      const d = scratch(SQL, 'shop', 'DELETE FROM order_items;');
      const stmt = v.a === 'UPDATE' ? `UPDATE products\nSET price = price * 11 / 10${W ? '\nWHERE ' + W : ''};` : `DELETE FROM products${W ? '\nWHERE ' + W : ''};`;
      const cols = 'id, name, category, price';
      const before = q(d, `SELECT ${cols} FROM products ORDER BY id`);
      const hit = new Set(q(d, `SELECT id FROM products${W ? ' WHERE ' + W : ''}`).rows.map(r => r[0]));
      const rc = Object.fromEntries(before.rows.map((r, i) => [i, hit.has(r[0]) ? 'look' : '']));
      const e = err(d, stmt.replace(/\n/g, ' '));
      const n = d.getRowsModified();
      const after = q(d, `SELECT ${cols} FROM products ORDER BY id`);
      const out = [
        { msg: 'The table before the change.', mood: 'think', layers: [{ t: 'sql', text: stmt }, { t: 'tab', label: 'products', cols: before.cols, rows: before.rows }] },
        { msg: W ? `First the engine finds the rows where <b>${esc(W)}</b> is true: ${hit.size} of ${before.rows.length}.` : `There is no WHERE, so <b>every row</b> is picked: all ${before.rows.length}.`, mood: W ? 'look' : 'wow', layers: [{ t: 'sql', text: stmt }, { t: 'tab', label: 'products', cols: before.cols, rows: before.rows, rcls: rc }] }];
      if (e) out.push({ msg: `SQLite says: ${esc(e)}`, mood: 'sad', layers: [{ t: 'sql', text: stmt }] });
      else if (v.a === 'UPDATE') out.push({ msg: `${n} ${n === 1 ? 'row was' : 'rows were'} changed. Prices went up by 10 percent, using integer division, only in the marked rows.`, mood: n === before.rows.length && !W ? 'sad' : 'happy', fx: 'burst', layers: [{ t: 'sql', text: stmt }, { t: 'tab', label: 'products after', cols: after.cols, rows: after.rows, rcls: rc, ccls: { 3: 'piv' } }] });
      else out.push({ msg: `${n} ${n === 1 ? 'row is' : 'rows are'} gone. ${!W ? 'The table is empty. Without a backup or an open transaction there is no undo.' : 'The other rows are untouched.'}`, mood: W ? 'happy' : 'sad', fx: W ? 'burst' : undefined, layers: [{ t: 'sql', text: stmt }, { t: 'tab', label: 'products after', cols: after.cols, rows: after.rows }] });
      out.push({ msg: 'Habit worth keeping: run the same WHERE in a SELECT first, check the rows, and only then change them.', mood: 'happy', layers: [{ t: 'sql', text: `SELECT * FROM products${W ? '\nWHERE ' + W : ''};` }] });
      return out;
    }
  }));

  /* ---------- 4.3 a CTE builds a query in named steps ---------- */
  SQW('sqcte', (SQL, cfg) => ({
    title: 'A CTE is a query in named steps',
    sub: 'Each WITH step is a small named result that the next step can read. Change the spending limit and watch every step recompute.',
    inputs: [{ k: 'n', label: 'Big spender means total at least', type: 'num', val: cfg.n || 2000, w: 90 }],
    frames: v => {
      const d = db(SQL, 'shop'), N = Math.max(0, +v.n || 0);
      const s1 = 'SELECT o.customer_id, SUM(oi.qty * p.price) AS total\n  FROM orders o\n  JOIN order_items oi ON oi.order_id = o.id\n  JOIN products p ON p.id = oi.product_id\n  WHERE o.status <> \'cancelled\'\n  GROUP BY o.customer_id';
      const s2 = `SELECT customer_id, total FROM spend WHERE total >= ${N}`;
      const s3 = 'SELECT c.name, b.total FROM big b JOIN customers c ON c.id = b.customer_id ORDER BY b.total DESC';
      const full = `WITH spend AS (\n  ${s1}\n),\nbig AS (\n  ${s2}\n)\n${s3};`;
      const r1 = q(d, `WITH spend AS (${s1}) SELECT * FROM spend ORDER BY customer_id`);
      const r2 = q(d, `WITH spend AS (${s1}), big AS (${s2}) SELECT * FROM big ORDER BY customer_id`);
      const r3 = q(d, `WITH spend AS (${s1}), big AS (${s2}) ${s3}`);
      const ST = ['spend', 'big', 'final SELECT'];
      return [
        { msg: 'The whole statement. Read it top to bottom like a recipe: each step has a name.', mood: 'think', layers: [{ t: 'sql', text: full }, { t: 'flow', items: ST, on: -1 }] },
        { msg: `Step <b>spend</b>: total money per customer, cancelled orders left out. ${r1.rows.length} customers.`, mood: 'work', layers: [{ t: 'flow', items: ST, on: 0 }, { t: 'sql', text: 'spend AS (\n  ' + s1 + '\n)' }, { t: 'tab', label: 'spend', cols: r1.cols, rows: r1.rows }] },
        { msg: `Step <b>big</b> reads spend as if it were a table and keeps totals of at least ${N}: ${r2.rows.length} left.`, mood: 'look', layers: [{ t: 'flow', items: ST, on: 1, done: 0 }, { t: 'sql', text: 'big AS (\n  ' + s2 + '\n)' }, { t: 'tab', label: 'spend', cols: r1.cols, rows: r1.rows, rcls: Object.fromEntries(r1.rows.map((r, i) => [i, r[1] >= N ? 'yes' : 'no'])) }] },
        { msg: 'The final SELECT joins big to customers to show names. The named steps vanish when the statement ends.', mood: 'happy', fx: 'burst', layers: [{ t: 'flow', items: ST, on: 2, done: 1 }, { t: 'sql', text: s3 + ';' }, { t: 'tab', label: 'Result', cols: r3.cols, rows: r3.rows }] }
      ];
    }
  }));
})();
