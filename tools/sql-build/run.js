// Runs SQL jobs at build time with the same sql.js the pages load. Reads JSON from stdin:
//   { datasets: {name: sql}, jobs: [{key, db, setup, src}] }
// and prints { key: [records from SQRUN.run] }. A job may also have plan: true, which adds EXPLAIN QUERY PLAN rows.
const path = require('path');
const ROOT = path.join(__dirname, '..', '..');
const init = require(path.join(ROOT, 'assets/vendor/sqljs/sql-wasm.js'));
const SQRUN = require(path.join(ROOT, 'assets/sqlrun.js'));

let input = '';
process.stdin.on('data', d => { input += d; });
process.stdin.on('end', async () => {
  const { datasets, jobs } = JSON.parse(input);
  const SQL = await init({ useOldExtensionFunctions: false });
  const out = {};
  for (const j of jobs) {
    const db = SQRUN.open(SQL, (j.db ? datasets[j.db] : '') + '\n' + (j.setup || ''));
    out[j.key] = SQRUN.run(db, j.src, j.max || 200);
    db.close();
  }
  process.stdout.write(JSON.stringify(out));
});
