// Writes every lab answer in Java, Python, JavaScript and TypeScript with the playground's own translator
// (assets/pwplay.js), so build.py can run each version with real Playwright. Reads JSON from stdin:
// [{ "id": "...", "name": "...", "from": "ts", "src": "..." }] and prints { id: { java, py, js, ts } }.
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const PWPLAY = require('../../assets/pwplay.js');
let input = '';
for await (const chunk of process.stdin) input += chunk;
const out = {};
for (const lab of JSON.parse(input)) {
  out[lab.id] = {};
  for (const to of ['java', 'py', 'js', 'ts']) out[lab.id][to] = to === lab.from ? lab.src : PWPLAY.translate(lab.src, lab.from, to, lab.name);
}
console.log(JSON.stringify(out));
