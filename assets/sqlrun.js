/* ===== SQL runner shared by the browser pages (assets/sqlplay.js) and the build (tools/sql-build/run.js) =====
   Both sides use the same SQLite build, sql.js 1.16.0 (assets/vendor/sqljs), so the output written into a page
   at build time is exactly what the reader sees when they press Run.

   SQRUN.open(SQL, setupSql)  a fresh in-memory database with foreign keys switched on, then setupSql run on it
   SQRUN.run(db, src, max)    runs every statement of src in order and returns one record per statement:
                              {sql, cols, rows, more, changes, error}. It stops at the first error.
*/
(function (root) {
  function cellValue(v) {
    if (v instanceof Uint8Array) return "x'" + Array.from(v, b => b.toString(16).padStart(2, '0')).join('') + "'";
    return v;
  }
  function total(db) { return db.exec('SELECT total_changes()')[0].values[0][0]; }

  function open(SQL, setup) {
    const db = new SQL.Database();
    db.run('PRAGMA foreign_keys = ON');
    if (setup) db.exec(setup);
    return db;
  }

  function run(db, src, max) {
    max = max || 200;
    const out = [];
    let it, st = null;
    try {
      it = db.iterateStatements(src);
      for (;;) {
        const before = total(db);
        const nx = it.next();
        if (nx.done) break;
        st = nx.value;
        const sql = st.getSQL().trim();
        const cols = st.getColumnNames();
        const rows = [];
        let n = 0;
        while (st.step()) { if (n++ < max) rows.push(st.get().map(cellValue)); }
        const rec = { sql, cols, rows };
        if (n > rows.length) rec.more = n;
        const ch = total(db) - before;
        if (ch || /^\s*(insert|update|delete|replace|with[\s\S]*\b(insert|update|delete))\b/i.test(sql)) rec.changes = ch;
        out.push(rec);
        st = null;
      }
    } catch (e) {
      const sql = st ? st.getSQL().trim() : (it && it.getRemainingSQL ? it.getRemainingSQL().trim() : src.trim());
      out.push({ sql, cols: [], rows: [], error: String(e.message || e) });
    }
    return out;
  }

  const api = { open, run };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.SQRUN = api;
})(this);
