/* Run one Java, C, C++ or C# file with the playground runner from the command line, the same way the page does.
   node tools/playground-build/run.js file.java java [stdin text]     (set TRACE=1 to record steps) */
const path = require('path');
const P = path.join(__dirname, '..', '..', 'assets', 'playground');
for (const f of ['cf-parse.js', 'cf-run.js', 'cf-expr.js', 'cf-lib.js', 'cf-check.js']) require(path.join(P, f));
const fs = require('fs');
if (process.env.CHECK_DEBUG) globalThis.CF_CHECK_DEBUG = true;
const [file, lang, stdin] = process.argv.slice(2);
const r = CF.run(fs.readFileSync(file, 'utf8'), lang, { stdin: stdin || '', trace: !!process.env.TRACE });
process.stdout.write(r.out.map(o => o.s).join(''));
if (r.compile) console.log('[COMPILE] line ' + r.compile.line + ': ' + r.compile.msg);
if (r.notes && r.notes.length) console.error('[NOTES] ' + r.notes.join('\n'));
