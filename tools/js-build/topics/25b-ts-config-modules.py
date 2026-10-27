# Chapter 25b: setting up TypeScript projects: tsconfig in depth, ES modules and module resolution, type only imports and
# verbatimModuleSyntax, subpath imports with #/, erasable syntax for Node type stripping, declaration merging and namespaces,
# isolatedDeclarations and project references.
import json
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

PRICE = '''
export interface Item { sku: string; price: number }

export function total(items: Item[]): number {
  return items.reduce((sum, i) => sum + i.price, 0);
}
'''

CORE_CFG = json.dumps({'compilerOptions': {'composite': True, 'target': 'esnext', 'module': 'nodenext', 'strict': True, 'outDir': 'dist', 'rootDir': 'src'}, 'include': ['src']}, indent=2)
APP_CFG = json.dumps({'compilerOptions': {'target': 'esnext', 'module': 'nodenext', 'strict': True, 'outDir': 'dist', 'rootDir': 'src'},
                      'references': [{'path': '../core'}], 'include': ['src']}, indent=2)

CODES = {
    'esm': ts('''
import { total, type Item } from "./price.ts";        // type is erased, total stays
import { total as sum } from "./price";               // no extension: Node cannot find this file
import { Item as Row } from "./price.ts";             // a type imported like a value

const cart: Item[] = [{ sku: "PEN-1", price: 49 }, { sku: "BAG-2", price: 899 }];
console.log("total", total(cart));
''', 'ES module imports under module nodenext', errors=2, run=False, more={'src/price.ts': PRICE}, options={'verbatimModuleSyntax': True}),
    'subpath': test({'package.json': json.dumps({'name': 'shop-tests', 'type': 'module', 'imports': {'#/*': './src/*'}}, indent=2),
                     'tsconfig.json': json.dumps({'compilerOptions': {'target': 'esnext', 'module': 'nodenext', 'strict': True, 'noEmit': True, 'allowImportingTsExtensions': True, 'types': ['node']}, 'include': ['src']}, indent=2),
                     'src/lib/price.ts': PRICE,
                     'src/tests/cart.test.ts': '''
// #/ points at the src folder, so deep files never need ../../..
import { total, type Item } from "#/lib/price.ts";

const items: Item[] = [{ sku: "PEN-1", price: 49 }, { sku: "PEN-2", price: 51 }];
console.log(total(items) === 100 ? "PASS total of two pens" : "FAIL");
'''}, 'npx tsc -p . --pretty false && echo "tsc: no type errors" && node src/tests/cart.test.ts', 'Subpath imports that start with #/ (TypeScript 6.0)',
        show=['package.json', 'src/tests/cart.test.ts'], shown_cmd='npx tsc && node src/tests/cart.test.ts'),
    'erasable': ts('''
// Node.js runs .ts files by deleting the types. Code that needs real JavaScript output cannot be deleted.
enum Status { Pass, Fail }                         // generates an object at run time

class Client {
  constructor(private baseURL: string) {}          // parameter property: generates this.baseURL = baseURL
}

namespace Legacy { export const v = 1; }           // generates an object too

// The erasable alternatives
const Status2 = { Pass: 0, Fail: 1 } as const;
type Status2 = (typeof Status2)[keyof typeof Status2];
class Client2 {
  baseURL: string;
  constructor(baseURL: string) { this.baseURL = baseURL; }
}
const s: Status2 = Status2.Fail;
console.log(s, new Client2("http://localhost:3000").baseURL, Status, Client, Legacy);
''', 'erasableSyntaxOnly marks code that Node cannot strip', errors=3, run=False, options={'erasableSyntaxOnly': True}),
    'merging': ts('''
// Two declarations of the same interface merge into one
interface TestInfo { title: string }
interface TestInfo { retries: number }
const info: TestInfo = { title: "checkout works", retries: 2 };

// Adding a field to a global type, as test libraries do
declare global {
  interface Window { __TEST_USER__?: string }
}

// A function and a namespace with the same name merge: callable, with extra members
function money(cents: number): string { return (cents / 100).toFixed(2); }
namespace money {
  export const currency = "INR";
}

console.log(info.title, info.retries, money(4950), money.currency);
const wrong: TestInfo = { title: "only a title" };
export {};
''', 'Declaration merging and namespaces', errors=1, run=False),
    'isolated': ts('''
export interface Item { sku: string; price: number }

export function total(items: Item[]): number {        // explicit return type: fine
  return items.reduce((sum, i) => sum + i.price, 0);
}

export function withTax(amount: number) {             // return type must be inferred: not allowed
  return amount * 1.18;
}

export const VAT = 0.18;                              // a literal is easy to read: fine
export const defaults = { currency: "INR", vat: VAT };  // an object made of other values: not allowed

const local = (n: number) => n * 2;                   // not exported, so nothing to declare
console.log(total([{ sku: "A", price: 10 }]), withTax(100), local(2), defaults.currency);
''', 'isolatedDeclarations: every export states its type', errors=2, options={'declaration': True, 'isolatedDeclarations': True}),
    'refs': test({'package.json': pkg('monorepo', 'module'),
                  'packages/core/tsconfig.json': CORE_CFG,
                  'packages/core/src/index.ts': '''
export function slug(text: string): string {
  return text.trim().toLowerCase().replace(/\\s+/g, "-");
}
''',
                  'packages/app/tsconfig.json': APP_CFG,
                  'packages/app/src/main.ts': '''
import { slug } from "../../core/dist/index.js";
console.log(slug("  Add To Cart "));
'''}, 'echo "--- first build ---" && npx tsc -b packages/app --verbose | grep -E "Building|up to date|out of date" ; node packages/app/dist/main.js && echo "--- second build, nothing changed ---" && npx tsc -b packages/app --verbose | grep -E "Building|up to date|out of date"',
        'Project references: build only what changed', show=['packages/core/tsconfig.json', 'packages/app/tsconfig.json', 'packages/app/src/main.ts'],
        shown_cmd='npx tsc -b packages/app --verbose\nnode packages/app/dist/main.js\nnpx tsc -b packages/app --verbose',
        replace=[(r'\d\d:\d\d:\d\d [AP]M - ', ''), (r"is older than output '[^']*'", 'is older than its output')]),
    'removed': ts('''
const ok = 1;
console.log(ok);
''', 'An old option that TypeScript 7.0 no longer accepts', errors=1, run=False, options={'baseUrl': '.'}),
}

LANES = {
    'resolve': {'t': 'How tsc and Node find an import under nodenext',
                'code': 'import { total } from "./price.ts";\nimport { total } from "./price";\nimport { total } from "#/lib/price.ts";\nimport { z } from "zod";',
                'lanes': ['Import', 'Where it looks', 'Found', 'Result'], 'tone': [1, 2, 3, 4],
                'steps': [{'l': 1, 'v': [['./price.ts'], ['src/price.ts'], ['yes'], ['OK in tsc and Node']], 'm': 'A relative path with the real file extension. Both tsc and Node find exactly that file.'},
                          {'l': 2, 'v': [['./price'], ['src/price (no extension)'], ['no'], ['tsc error, Node crash']], 'm': 'ES modules in Node never guess extensions. tsc knows this under nodenext and reports the import before Node crashes on it.'},
                          {'l': 3, 'v': [['#/lib/price.ts'], ['package.json "imports"', 'src/lib/price.ts'], ['yes'], ['OK']], 'm': 'A name starting with # is looked up in the imports field of the nearest package.json. TypeScript 6.0 also accepts the short #/ prefix.'},
                          {'l': 4, 'v': [['zod'], ['node_modules/zod/package.json', '"exports" field'], ['yes'], ['OK']], 'm': 'A bare name is a package. Node reads its exports field to choose the right file, and tsc finds the matching .d.ts types the same way.'}]},
}

DG = {
    'refs': {'t': 'A monorepo with project references', 'w': 900, 'h': 300, 'mw': 640,
        'n': [['core', 40, 50, 230, 60, 'packages/core', {'c': 2, 'sub': 'composite: true'}], ['coreout', 40, 190, 230, 60, 'core/dist', {'c': 4, 'sub': '.js, .d.ts, .tsbuildinfo'}],
              ['app', 360, 50, 230, 60, 'packages/app', {'c': 1, 'sub': 'references ../core'}], ['tests', 660, 50, 210, 60, 'packages/tests', {'c': 3, 'sub': 'references app and core'}],
              ['build', 360, 190, 230, 60, 'tsc -b', {'c': 5, 'sub': 'builds in order, skips unchanged'}]],
        'e': [['core', 'coreout', {'t': 'emits', 'id': 'r1'}], ['app', 'core', {'t': 'depends on', 'id': 'r2'}], ['tests', 'app', {'id': 'r3'}],
              ['build', 'coreout', {'t': 'reads', 'id': 'r4', 'd': 1}]],
        'st': [[['core'], 'A shared package marked composite: true, so others can reference it.'],
               [['core', 'coreout', 'r1'], 'Building it writes JavaScript, declaration files and a .tsbuildinfo file that remembers what was checked.'],
               [['app', 'r2'], 'The app lists core under references. It uses core through its .d.ts files instead of re-checking core\'s source.'],
               [['tests', 'r3'], 'A test package can reference both. Each package keeps its own tsconfig with its own options.'],
               [['build', 'r4'], 'tsc -b builds packages in dependency order and skips any whose inputs have not changed. TypeScript 7 can build several projects in parallel with --builders.']]},
}

PARTS = [
    part('tsconfig', '⚙️', 'tsconfig.json in depth', '''
<p>Every TypeScript project is driven by <code>tsconfig.json</code>. It answers four questions: which files to check (<code>include</code>, <code>exclude</code>, <code>files</code>), how strict to be, what JavaScript to produce, and how imports are found. Since TypeScript 6.0 a fresh project already defaults to <code>strict: true</code>, <code>module: "esnext"</code>, <code>target: "es2025"</code> and <code>types: []</code>.</p>
<div class="tw"><table class="jt"><tr><th>Group</th><th>Options you will meet</th></tr>
<tr><td>Files</td><td><code>include</code>, <code>exclude</code>, <code>rootDir</code>, <code>outDir</code></td></tr>
<tr><td>Checking</td><td><code>strict</code>, <code>noUncheckedIndexedAccess</code>, <code>exactOptionalPropertyTypes</code>, <code>noImplicitOverride</code></td></tr>
<tr><td>Output</td><td><code>target</code>, <code>declaration</code>, <code>sourceMap</code>, <code>noEmit</code></td></tr>
<tr><td>Modules</td><td><code>module</code>, <code>moduleResolution</code>, <code>verbatimModuleSyntax</code>, <code>paths</code></td></tr>
<tr><td>Environment</td><td><code>lib</code>, <code>types</code>, <code>skipLibCheck</code></td></tr>
<tr><td>Sharing</td><td><code>extends</code> (a base config, or several since 5.0), <code>references</code></td></tr></table></div>
<p>Old options do not live forever. TypeScript 6.0 deprecated a long list and TypeScript 7.0 removed them, so an old config stops the build:</p>
[[removed]]
''', qa=True, qa_why='Test projects often copy an old tsconfig. Knowing which options matter avoids hours of strange import errors.',
        kw=['tsconfig.json', 'compilerOptions', 'include', 'strict', 'target', 'lib', 'types', 'extends', 'baseUrl removed', 'TypeScript 6.0 defaults', 'paths']),
    part('esm', '📥', 'ES modules and module resolution', '''
<p>The <code>module</code> and <code>moduleResolution</code> options tell tsc which rules the real runtime will use to find files. With <code>nodenext</code> it copies Node exactly: ES module imports need the file extension, and packages are found through their <code>exports</code> field. With <code>bundler</code> it copies Vite, webpack and esbuild, which allow imports without extensions.</p>
<div class="viz" data-viz="lanes" data-k="resolve"></div>
<p><code>verbatimModuleSyntax</code> keeps imports exactly as written, so anything that is only a type must say so with <code>import type</code> or an inline <code>type</code> marker. Tools that strip types one file at a time then know which imports to delete.</p>
[[esm]]
<div class="tw"><table class="jt"><tr><th>Runs in</th><th>module</th><th>moduleResolution</th></tr>
<tr><td>Node.js</td><td><code>nodenext</code> (or <code>node20</code> since 5.9)</td><td>follows module</td></tr>
<tr><td>Vite, webpack, esbuild</td><td><code>esnext</code> or <code>preserve</code></td><td><code>bundler</code></td></tr></table></div>
''', qa=True, qa_why='Playwright and Vitest projects break most often on imports: missing extensions, CommonJS against ES modules, and types imported as values.',
        kw=['ES modules', 'module resolution', 'nodenext', 'bundler', 'file extensions', 'exports field', 'import type', 'verbatimModuleSyntax', 'CommonJS', 'ERR_MODULE_NOT_FOUND']),
    part('subpath', '#️⃣', 'Subpath imports instead of ../../..', '''
<p>Deep test folders end up with imports like <code>../../../lib/price</code>. Node's <b>subpath imports</b> fix that with an <code>imports</code> field in package.json, and both Node and tsc understand it without extra tools. TypeScript 6.0 added support for the short <code>#/</code> prefix that Node recently allowed.</p>
[[subpath]]
<div class="note">The older <code>paths</code> option in tsconfig only teaches tsc where files are. Node itself does not read it, so a separate plugin was needed at run time. Subpath imports work in both places with one setting.</div>
''', qa=True, kw=['subpath imports', '#/', 'package.json imports', 'paths', 'path aliases', 'TypeScript 6.0', 'relative imports']),
    part('erasable', '✂️', 'Erasable syntax and running .ts files directly', '''
<p>Node.js 23.6 and later run <code>.ts</code> files directly by replacing types with spaces, without checking them. That only works for TypeScript features that leave no JavaScript behind. Enums, namespaces with values and constructor parameter properties produce real code, so Node refuses them. <code>erasableSyntaxOnly</code> (TypeScript 5.8) makes tsc flag them early.</p>
[[erasable]]
<div class="tip">This is also why the earlier chapters prefer <code>as const</code> objects over enums. They behave the same, work in Node, Deno and Bun without a build step, and the JavaScript output is exactly what you wrote.</div>
''', qa=True, qa_why='Running test files with plain node, without ts-node or a bundler, is now common, and these three features are what breaks it.',
        kw=['erasableSyntaxOnly', 'type stripping', 'node main.ts', 'enum', 'namespace', 'parameter properties', 'TypeScript 5.8', 'Node.js 23.6']),
    part('merging', '🧷', 'Declaration merging and namespaces', '''
<p>TypeScript merges some declarations that share a name. Two <code>interface</code> blocks become one, which is how libraries let you add fields to their types. A function and a <code>namespace</code> can merge too, giving a function with extra properties. Namespaces come from before ES modules. In new code, use modules instead, and keep namespaces for reading older code and type declarations.</p>
[[merging]]
<p>This file is only checked here, not run. The namespace produces real JavaScript, so Node's type stripping refuses it, exactly as the erasable syntax part above explained.</p>
''', kw=['declaration merging', 'interface merging', 'namespace', 'declare global', 'module augmentation', 'Window', 'legacy code']),
    part('isolated', '🏝️', 'isolatedDeclarations and fast declaration files', '''
<p>A library publishes <code>.d.ts</code> files that describe its exports. Normally only tsc can write them, because it must infer return types. With <code>isolatedDeclarations</code> (TypeScript 5.5) every export states its type, so faster tools such as esbuild, oxc or swc can write the declarations one file at a time, in parallel.</p>
[[isolated]]
''', kw=['isolatedDeclarations', 'declaration files', '.d.ts', 'explicit return types', 'TypeScript 5.5', 'library publishing', 'oxc', 'swc']),
    part('refs', '🏗️', 'Project references for big repositories', '''
<p>In a large repository with many packages, checking everything every time is slow. <b>Project references</b> split the code into projects that build separately and in order. <code>tsc -b</code> (build mode) checks only what changed since the last build.</p>
<div class="viz" data-viz="flow" data-k="refs"></div>
[[refs]]
<div class="note">The second build checked nothing, because no input changed. TypeScript 7.0, the native rewrite, also adds <code>--builders</code> to build independent projects at the same time, and <code>--checkers</code> to split checking across CPU cores.</div>
''', kw=['project references', 'composite', 'tsc -b', 'build mode', 'tsbuildinfo', 'monorepo', 'incremental', '--builders', '--checkers', 'TypeScript 7']),
]

INFO = {'title': 'Setting up so everything finds everything', 'panels': [
    panel([['e', '⚙️'], ['t', 'tsconfig.json', {'b': 1}]], 'Config', 'One file decides the rules.', 'Old options break TypeScript 7.'),
    panel([['e', '📥'], ['t', 'import "./price.ts"', {'b': 1, 'size': 11}]], 'nodenext', 'Copy Node exactly.', 'Extensions are required.'),
    panel([['e', '#️⃣'], ['t', '"#/*": "./src/*"', {'b': 1, 'size': 11}]], 'Subpath imports', 'No more ../../..', 'Works in Node and tsc.'),
    panel([['e', '✂️'], ['t', 'erasableSyntaxOnly', {'b': 1, 'size': 11}]], 'Erasable', 'Types only, no enums.', 'node file.ts just works.')],
    'remember': 'Match module settings to the real runtime, mark type only imports, prefer subpath imports to deep relative paths, write erasable TypeScript so Node can run it, and split big repositories with project references.'}

REAL = [
    ['🎭', 'A Playwright suite', 'Moved from ts-node to running specs with plain node and erasableSyntaxOnly, and replaced its enums with as const objects.'],
    ['🧭', 'A test utilities folder', 'Replaced ../../../helpers imports in 300 files with #/helpers imports, so moving a test no longer breaks its imports.'],
    ['🏗️', 'A monorepo with 40 packages', 'Uses project references and tsc -b in CI, so a change in one package re-checks only the packages that depend on it.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter sets up TypeScript projects: tsconfig, ES modules and resolution, subpath imports, erasable syntax, merging, isolated declarations and project references.',
        'यह अध्याय TypeScript projects सेट करता है: tsconfig, ES modules और resolution, subpath imports, erasable syntax, merging, isolated declarations और project references।',
        'ಈ ಅಧ್ಯಾಯ TypeScript projects ಹೊಂದಿಸುತ್ತದೆ: tsconfig, modules, subpath imports, project references.',
        'ଏହି ଅଧ୍ୟାୟ TypeScript projects ସେଟ୍ କରେ: tsconfig, modules, subpath imports, project references।',
        'يجهّز هذا الفصل مشاريع TypeScript: ملف tsconfig ووحدات ES والاستيراد الفرعي والصياغة القابلة للمسح والدمج ومراجع المشاريع.',
        'Dieses Kapitel richtet TypeScript-Projekte ein: tsconfig, ES-Module, Subpath-Importe, löschbare Syntax, Merging und Projektreferenzen.'),
    say('tsconfig', 'tsconfig', 'tsconfig decides which files are checked, how strict, what output is made and how imports are found. TypeScript 7 rejects options removed after 6.0.',
        'tsconfig तय करता है कौन सी files जांची जाएं, कितना strict, क्या output बने और imports कैसे मिलें। TypeScript 7 हटाए गए options को अस्वीकार करता है।',
        'tsconfig files, strictness, output, imports ನಿರ್ಧರಿಸುತ್ತದೆ.',
        'tsconfig files, strictness, output, imports ନିର୍ଦ୍ଧାରଣ କରେ।',
        'يحدد tsconfig الملفات المفحوصة ومدى الصرامة والمخرجات وطريقة إيجاد الاستيرادات، وترفض TypeScript 7 الخيارات المحذوفة.',
        'tsconfig bestimmt geprüfte Dateien, Strenge, Ausgabe und Importauflösung. TypeScript 7 lehnt entfernte Optionen ab.'),
    say('esm', 'Modules', 'Under nodenext, imports need the real file extension and packages are found through exports. Types must be imported with import type.',
        'nodenext में imports को असली file extension चाहिए और packages exports से मिलते हैं। Types को import type से लाना होता है।',
        'nodenext ನಲ್ಲಿ extension ಬೇಕು, types ಗೆ import type.',
        'nodenext ରେ extension ଦରକାର, types ପାଇଁ import type।',
        'في nodenext تحتاج الاستيرادات إلى امتداد الملف الحقيقي وتُعثر الحزم عبر exports، ويجب استيراد الأنواع بـ import type.',
        'Unter nodenext brauchen Importe die echte Dateiendung, Pakete werden über exports gefunden, und Typen kommen per import type.'),
    say('subpath', 'Subpath imports', 'An imports field in package.json maps hash slash to the src folder, so deep files import without dot dot slash chains.',
        'package.json का imports field hash slash को src folder से जोड़ता है, ताकि गहरी files बिना लंबे relative paths के import करें।',
        'package.json imports field # ಅನ್ನು src ಗೆ ಜೋಡಿಸುತ್ತದೆ.',
        'package.json imports field # କୁ src ସହ ଯୋଡ଼େ।',
        'يربط حقل imports في package.json البادئة #/ بمجلد src فتستورد الملفات العميقة دون سلاسل ../.',
        'Ein imports-Feld in package.json bildet #/ auf src ab, sodass tiefe Dateien ohne ../-Ketten importieren.'),
    say('erasable', 'Erasable syntax', 'Node runs ts files by deleting types. Enums, namespaces and parameter properties make real code, so erasableSyntaxOnly flags them.',
        'Node types हटाकर ts files चलाता है। Enums, namespaces और parameter properties असली code बनाते हैं, इसलिए erasableSyntaxOnly उन्हें चिह्नित करता है।',
        'Node types ಅಳಿಸಿ ಓಡಿಸುತ್ತದೆ. Enums ಬೇಡ.',
        'Node types ମିଟାଇ ଚଲାଏ। Enums ନୁହେଁ।',
        'يشغّل Node ملفات ts بحذف الأنواع، والتعدادات ومساحات الأسماء وخصائص المعاملات تنتج شيفرة حقيقية فيشير إليها erasableSyntaxOnly.',
        'Node führt ts-Dateien durch Löschen der Typen aus. Enums, Namespaces und Parameter-Properties erzeugen echten Code, daher markiert erasableSyntaxOnly sie.'),
    say('merging', 'Merging', 'Interfaces with the same name merge into one, and a function can merge with a namespace. Use modules for new code.',
        'एक नाम वाले interfaces एक हो जाते हैं, और function namespace के साथ जुड़ सकता है। नए code के लिए modules इस्तेमाल करें।',
        'ಒಂದೇ ಹೆಸರಿನ interfaces ವಿಲೀನವಾಗುತ್ತವೆ.',
        'ସମାନ ନାମର interfaces ମିଶିଯାଆନ୍ତି।',
        'تندمج الواجهات ذات الاسم الواحد، ويمكن دمج دالة مع مساحة أسماء، واستخدم الوحدات في الشيفرة الجديدة.',
        'Gleichnamige Interfaces verschmelzen, und eine Funktion kann mit einem Namespace verschmelzen. Für neuen Code nutze Module.'),
    say('isolated', 'Isolated declarations', 'With isolatedDeclarations every export states its type, so fast tools can write declaration files one file at a time.',
        'isolatedDeclarations में हर export अपना type बताता है, ताकि तेज़ tools एक एक file की declaration बना सकें।',
        'isolatedDeclarations ನಲ್ಲಿ ಪ್ರತಿ export type ಹೇಳುತ್ತದೆ.',
        'isolatedDeclarations ରେ ପ୍ରତି export type କହେ।',
        'مع isolatedDeclarations يذكر كل تصدير نوعه، فتكتب الأدوات السريعة ملفات التصريح ملفًا ملفًا.',
        'Mit isolatedDeclarations nennt jeder Export seinen Typ, sodass schnelle Tools Deklarationsdateien einzeln schreiben können.'),
    say('refs', 'Project references', 'Project references split a big repository into projects. tsc dash b builds them in order and skips what did not change.',
        'Project references बड़े repository को projects में बांटते हैं। tsc dash b उन्हें क्रम से बनाता है और बिना बदले को छोड़ देता है।',
        'Project references repository ವಿಭಜಿಸುತ್ತವೆ, tsc -b ಬದಲಾದದ್ದನ್ನು ಮಾತ್ರ.',
        'Project references repository ବିଭାଜନ କରେ, tsc -b ବଦଳିଥିବା କେବଳ।',
        'تقسم مراجع المشاريع المستودع الكبير إلى مشاريع، ويبنيها tsc -b بالترتيب ويتخطى ما لم يتغير.',
        'Projektreferenzen teilen ein großes Repository in Projekte. tsc -b baut sie der Reihe nach und überspringt Unverändertes.'),
    say('practice', 'Hands-on', 'Practise resolving a subpath import, adding a missing extension, merging configs and ordering project builds.',
        'Subpath import resolve करना, extension जोड़ना, configs merge करना और project builds का क्रम तय करना अभ्यास करें।',
        'Subpath import, extension, configs merge ಅಭ್ಯಾಸ.',
        'Subpath import, extension, configs merge ଅଭ୍ୟାସ।',
        'تدرّب على حل استيراد فرعي وإضافة امتداد ودمج الإعدادات وترتيب بناء المشاريع.',
        'Übe das Auflösen von Subpath-Importen, fehlende Endungen, Config-Merging und die Build-Reihenfolge.'),
]

QUIZ = [
    quiz('e', 'Which file configures a TypeScript project?', ['tsconfig.json', 'package-lock.json', '.eslintrc', 'babel.config.js'], 0, 'ts plus config.', 'tsc -p . reads it.'),
    quiz('e', 'Under module nodenext, which import works for src/price.ts from src/main.ts?', ['./price.ts', './price', 'price', '../price'], 0, 'Node does not guess.', 'allowImportingTsExtensions lets tsc accept the .ts extension.'),
    quiz('e', 'What does <code>import type</code> tell the tools?', ['The import is only for types and can be deleted', 'The import is lazy', 'The import is from a CDN', 'The import must be a class'], 0, 'Erased.', 'Nothing remains of it in the JavaScript.'),
    quiz('m', 'Why does Node refuse an enum in a .ts file it runs directly?', ['An enum generates JavaScript, and Node only deletes types', 'Enums are deprecated', 'Node has no numbers', 'Enums must be exported'], 0, 'Erasable syntax.', 'erasableSyntaxOnly reports enums, value namespaces and parameter properties.'),
    quiz('m', 'What does the package.json field <code>"imports": { "#/*": "./src/*" }</code> do?', ['Lets #/lib/x.ts mean ./src/lib/x.ts for Node and tsc', 'Installs packages', 'Publishes the src folder', 'Turns on strict mode'], 0, 'Subpath imports.', 'Unlike tsconfig paths, Node reads it too.'),
    quiz('m', 'Two interfaces named TestInfo declare title and retries. What is TestInfo?', ['One interface with both title and retries', 'A compile error', 'Only the second one', 'A union of the two'], 0, 'Declaration merging.', 'An object must then have both fields.'),
    quiz('m', 'Which moduleResolution copies Vite and esbuild?', ['bundler', 'nodenext', 'classic', 'node10'], 0, 'Bundlers allow imports without extensions.', 'classic and node10 were deprecated in 6.0 and removed in 7.0.'),
    quiz('h', 'What does isolatedDeclarations require?', ['Explicit types on exports that tsc would otherwise infer', 'No exports at all', 'One file per project', 'CommonJS'], 0, 'Declarations per file.', 'Then tools other than tsc can write .d.ts files fast.'),
    quiz('h', 'What happens in TypeScript 7.0 with <code>"baseUrl": "."</code> in tsconfig?', ['An error says the option was removed', 'It still works silently', 'It is renamed automatically', 'It turns on paths'], 0, 'Deprecated in 6.0.', 'The error suggests using paths instead.'),
    quiz('h', 'What does <code>tsc -b</code> skip?', ['Projects whose inputs did not change since the last build', 'Type checking entirely', 'Projects without tests', 'Declaration files'], 0, 'Build mode.', 'It compares inputs with the .tsbuildinfo file.'),
    quiz('x', 'A project needs <code>"composite": true</code> when?', ['When other projects reference it', 'Always', 'Only for browser code', 'When it uses decorators'], 0, 'References need it.', 'composite makes sure declarations and build info are produced.'),
    quiz('x', 'Why can a value namespace not be stripped by Node?', ['It compiles to an object with properties at run time', 'Namespaces are only types', 'Node does not support objects', 'It needs a bundler plugin'], 0, 'Real JavaScript.', 'A namespace with only types would be erasable.'),
]

CALC = [
    calc('e', 'An import statement has 3 imported names and 2 of them are types. With import type markers, how many names remain in the JavaScript?', '1', 'Types are erased.', ['<span class="eq">3 − 2 = 1</span>']),
    calc('e', 'A test file is 4 folders below src. How many "../" parts does a relative import to src/lib need?', '4', 'One per folder level.', ['A #/lib import needs none.']),
    calc('m', 'erasableSyntaxOnly found an enum, a parameter property and a namespace. How many errors?', '3', 'One per construct.', ['Each produces real JavaScript.']),
    calc('m', 'A monorepo has 10 packages and one changed with 2 packages depending on it. How many does tsc -b rebuild?', '3', 'The changed one plus dependents.', ['<span class="eq">1 + 2 = 3</span>']),
    calc('h', 'The VS Code build took 125.7 s with TypeScript 6 and 10.6 s with TypeScript 7. About how many times faster is that, to one decimal place?', '11.9', 'Divide old by new.', ['<span class="eq"><span class="fr"><i>125.7</i><i>10.6</i></span> ≈ 11.9</span>']),
    calc('h', 'With --checkers 4 on a 4 core machine, if checking took 20 s on one thread and splits perfectly, how many seconds does it take?', '5', 'Divide by four.', ['<span class="eq"><span class="fr"><i>20</i><i>4</i></span> = 5 s</span>', 'Real projects get somewhat less than perfect splitting.']),
    calc('x', 'A tsconfig extends two bases. The first sets strict true, the second sets strict false. Later entries win. What is strict?', 'false', 'The last one wins.', ['Options from later configs in the extends array override earlier ones.'], alt=['False']),
]

EX = [
    ex('resolve', 'e', 'Resolve a #/ import', '<p>Write <code>resolveSubpath(spec, map)</code>. If <code>spec</code> starts with a key of <code>map</code> that ends in <code>*</code> (such as <code>"#/*"</code>), replace that prefix with the value without its <code>*</code>. Otherwise return <code>null</code>.</p>',
       'function resolveSubpath(spec, map) {\n  \n}\n',
       [('resolveSubpath("#/lib/price.ts", { "#/*": "./src/*" })', './src/lib/price.ts'), ('resolveSubpath("zod", { "#/*": "./src/*" })', None), ('resolveSubpath("#utils/a.ts", { "#utils/*": "./tools/*" })', './tools/a.ts')],
       'function resolveSubpath(spec, map) {\n  for (const [key, target] of Object.entries(map)) {\n    const prefix = key.slice(0, -1);\n    if (key.endsWith("*") && spec.startsWith(prefix)) return target.slice(0, -1) + spec.slice(prefix.length);\n  }\n  return null;\n}', hint='Strip the * from both sides and swap the prefix.', why='This is the core of how Node and tsc read the imports field.'),
    ex('ext', 'm', 'Add the missing extension', '<p>Write <code>fixImport(spec)</code> for imports under nodenext. Relative specs (starting with <code>./</code> or <code>../</code>) that have no extension get <code>.ts</code> added. Package names and specs that already end in <code>.ts</code>, <code>.js</code> or <code>.json</code> stay the same.</p>',
       'function fixImport(spec) {\n  \n}\n',
       [('fixImport("./price")', './price.ts'), ('fixImport("../lib/cart.ts")', '../lib/cart.ts'), ('fixImport("zod")', 'zod'), ('fixImport("./data.json")', './data.json')],
       'function fixImport(spec) {\n  const relative = spec.startsWith("./") || spec.startsWith("../");\n  if (!relative || /\\.(ts|js|json)$/.test(spec)) return spec;\n  return spec + ".ts";\n}', hint='Check relative first, then test the ending with a regex.', why='This is the change most projects need when they move to nodenext.'),
    ex('extends', 'h', 'Merge extended configs', '<p>Write <code>mergeConfigs(list)</code> that merges an array of tsconfig objects. <code>compilerOptions</code> are merged key by key, with later configs winning. Other top level keys are replaced by later values.</p>',
       'function mergeConfigs(list) {\n  \n}\n',
       [('mergeConfigs([{ compilerOptions: { strict: true, target: "es2022" } }, { compilerOptions: { target: "esnext" }, include: ["src"] }])', {'compilerOptions': {'strict': True, 'target': 'esnext'}, 'include': ['src']}),
        ('mergeConfigs([])', {'compilerOptions': {}})],
       'function mergeConfigs(list) {\n  const out = { compilerOptions: {} };\n  for (const cfg of list) {\n    for (const [k, v] of Object.entries(cfg)) {\n      if (k === "compilerOptions") Object.assign(out.compilerOptions, v);\n      else out[k] = v;\n    }\n  }\n  return out;\n}', hint='Start with empty compilerOptions and use Object.assign for that key only.', why='This is how extends with an array of bases behaves since TypeScript 5.0.'),
    ex('order', 'x', 'Order project builds', '<p>Write <code>buildOrder(refs)</code> where <code>refs</code> maps each project to the projects it references. Return the projects in an order where every project comes after the ones it references. Visit projects and references in the order given.</p>',
       'function buildOrder(refs) {\n  \n}\n',
       [('buildOrder({ app: ["core"], core: [], tests: ["app", "core"] })', ['core', 'app', 'tests']), ('buildOrder({ a: [] })', ['a']), ('buildOrder({ ui: ["utils"], api: ["utils"], utils: [] })', ['utils', 'ui', 'api'])],
       'function buildOrder(refs) {\n  const done = new Set();\n  const out = [];\n  const visit = p => {\n    if (done.has(p)) return;\n    done.add(p);\n    for (const r of refs[p] || []) visit(r);\n    out.push(p);\n  };\n  Object.keys(refs).forEach(visit);\n  return out;\n}', hint='A depth first visit that adds a project after its references.', why='tsc -b sorts projects the same way before building them.'),
]

T = {
    'slug': 'ts-config-modules', 'title': 'TypeScript project setup: tsconfig, modules and builds', 'short': 'Config and modules', 'emoji': '⚙️', 'module': MODULE, 'minutes': 22,
    'lead': 'Most TypeScript problems at work are not about types but about setup: imports that cannot be found, enums that Node refuses, an old tsconfig that TypeScript 7 rejects. This chapter covers tsconfig in depth, ES modules and module resolution, type only imports, #/ subpath imports, erasable syntax for running .ts files directly, declaration merging, isolatedDeclarations and project references.',
    'desc': 'TypeScript project setup: tsconfig options, TypeScript 6.0 defaults and 7.0 removals, module and moduleResolution (nodenext, bundler), verbatimModuleSyntax and import type, subpath imports with #/, erasableSyntaxOnly and Node type stripping, declaration merging, namespaces, isolatedDeclarations and project references with tsc -b.',
    'summary': 'The groups of tsconfig options and an option TypeScript 7 removed, import rules under nodenext with an animated resolver, type only imports, #/ subpath imports, erasable alternatives to enums and parameter properties, interface and namespace merging, isolatedDeclarations, and a two package monorepo built with tsc -b.',
    'keywords': ['tsconfig', 'module resolution', 'nodenext', 'bundler', 'verbatimModuleSyntax', 'import type', 'subpath imports', 'erasableSyntaxOnly', 'type stripping', 'declaration merging', 'namespace', 'isolatedDeclarations', 'project references', 'tsc -b', 'TypeScript 7'],
    'qa_intro': 'Test projects are usually set up by copying a config from somewhere. This chapter explains what each setting does, so import errors and "works on my machine" problems can be fixed instead of worked around.',
    'parts': PARTS, 'codes': CODES, 'lanes': LANES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
