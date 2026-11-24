/* Checks the practice shell labs of the Unix and Linux chapters (called by build.py).
   Reads [[slug, lab], ...] as JSON on stdin. For each lab it makes a fresh pretend computer, runs every mission's
   hint in order, and fails when a hint does not complete its own mission, or when a mission is already complete
   before its hint runs (then the mission teaches nothing). */
const path = require('path');
const LXSH = require(path.join(__dirname, '..', '..', 'assets', 'lxshell.js'));
let src = '';
process.stdin.on('data', d => { src += d; });
process.stdin.on('end', () => {
  const bad = [];
  JSON.parse(src).forEach(([slug, lab]) => {
    const w = new LXSH.World(lab);
    let last = { cmd: '', out: '', code: 0 };
    lab.missions.forEach((m, i) => {
      if (m.check.length && !m.check.some(c => c.cmd || c.out || c.code !== undefined) && LXSH.check(w, m.check, last)) bad.push(`${slug}: "${lab.title}" mission ${i + 1} is already done before its hint runs`);
      if (!m.hint) { bad.push(`${slug}: "${lab.title}" mission ${i + 1} has no hint`); return; }
      const r = w.run(m.hint);
      last = { cmd: m.hint, out: r.out, code: r.code };
      if (!LXSH.check(w, m.check, last)) bad.push(`${slug}: "${lab.title}" mission ${i + 1} (${m.t.replace(/<[^>]+>/g, '')}) is not completed by its hint "${m.hint}". Output was:\n${r.out}`);
    });
  });
  if (bad.length) { console.log(bad.join('\n')); process.exit(1); }
});
