# Chapter 24: TypeScript classes and real projects: access modifiers, abstract classes and interfaces, decorators, declaration files and module augmentation, JSDoc with checkJs, and moving a JavaScript project to TypeScript.
import json
from kit import part, run, dom, test, show, say, quiz, calc, ex, panel, pkg, ts

MODULE = ('🔷', 'TypeScript', 'ts', 'TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.')

EMIT_CONFIG = json.dumps({'compilerOptions': {'target': 'es2022', 'module': 'nodenext', 'strict': True, 'rootDir': 'src', 'outDir': 'dist', 'types': ['node']}, 'include': ['src']}, indent=2)

CODES = {
    'classes': ts('''
abstract class BasePage {
  protected readonly baseURL: string;
  #visits = 0;                                     // JavaScript private: hidden at run time too
  constructor(baseURL: string, private readonly path: string) {
    this.baseURL = baseURL;
  }
  get url(): string { return this.baseURL + this.path; }
  open(): string { this.#visits++; return `open ${this.url} (visit ${this.#visits})`; }
  abstract isLoaded(): boolean;                   // every page must say how to know it is ready
}

interface Searchable { search(term: string): string[] }

class ProductsPage extends BasePage implements Searchable {
  constructor(baseURL: string) { super(baseURL, "/products"); }
  override isLoaded() { return true; }
  search(term: string) { return [`${term} pen`, `${term} ink`]; }
}

const page = new ProductsPage("http://localhost:3000");
console.log(page.open(), page.open(), page.isLoaded(), page.search("blue"));

page.baseURL;                                      // protected: only inside the class family
page.path;                                         // private: only inside BasePage
new BasePage("x", "/");                            // abstract classes cannot be created
class Broken extends BasePage {}                   // forgot isLoaded
''', 'Access modifiers, abstract classes and interfaces', errors=4, run=False),
    'private': ts('''
class Session {
  private token = "secret-123";                   // TypeScript private: a compile time check only
  #pin = "4321";                                  // JavaScript private: truly hidden

  check(pin: string) { return pin === this.#pin; }
}
const s = new Session();
console.log(Object.keys(s), JSON.stringify(s));
console.log((s as any).token, (s as any)["#pin"], s.check("4321"));
''', 'TypeScript private against JavaScript #private'),
    'decorators': test({
        'package.json': pkg('decorators', 'module'),
        'tsconfig.json': EMIT_CONFIG,
        'src/steps.ts': '''
// Standard decorators (TypeScript 5 and later): a method decorator receives the method and a context
export function step(title: string) {
  return function <This, Args extends unknown[], R>(
    method: (this: This, ...args: Args) => Promise<R>,
    context: ClassMethodDecoratorContext<This>,
  ) {
    return async function (this: This, ...args: Args): Promise<R> {
      const started = Date.now();
      try {
        const result = await method.apply(this, args);
        console.log(`✔ ${title}`);
        return result;
      } catch (e) {
        console.log(`✖ ${title} (${String(context.name)}): ${(e as Error).message}`);
        throw e;
      } finally {
        void (Date.now() - started);
      }
    };
  };
}

export function retry(times: number) {
  return function <This, Args extends unknown[], R>(method: (this: This, ...args: Args) => Promise<R>, _ctx: ClassMethodDecoratorContext<This>) {
    return async function (this: This, ...args: Args): Promise<R> {
      for (let i = 1; ; i++) {
        try { return await method.apply(this, args); }
        catch (e) { if (i >= times) throw e; }
      }
    };
  };
}
''',
        'src/main.ts': '''
import { step, retry } from "./steps.js";

class CheckoutPage {
  attempts = 0;

  @step("Fill the address")
  async fillAddress(city: string) { return `address in ${city}`; }

  @step("Pay with card")
  @retry(3)
  async pay() {
    if (++this.attempts < 3) throw new Error("payment frame not ready");
    return "paid";
  }

  @step("Apply coupon")
  async applyCoupon(code: string) { if (code !== "SAVE10") throw new Error(`coupon ${code} rejected`); }
}

const page = new CheckoutPage();
await page.fillAddress("Pune");
console.log(await page.pay(), "after", page.attempts, "attempts");
await page.applyCoupon("FREE").catch(() => {});
''',
    }, 'npx tsc && node dist/main.js', 'Decorators for steps and retries', show=['src/steps.ts', 'src/main.ts'], badge='🔷 Compiled with tsc, then run'),
    'dts': test({
        'package.json': pkg('typed-lib', 'module'),
        'tsconfig.json': json.dumps({'compilerOptions': {'target': 'esnext', 'module': 'nodenext', 'strict': True, 'noEmit': True, 'allowJs': True, 'allowImportingTsExtensions': True, 'types': ['node']}, 'include': ['src', 'types']}, indent=2),
        'vendor/legacy-report.js': '''
// An old plain JavaScript helper with no types
export function summarise(results) {
  const failed = results.filter(r => !r.ok).map(r => r.name);
  return { total: results.length, failed };
}
''',
        'types/legacy-report.d.ts': '''
// A declaration file describes JavaScript that has no types of its own
declare module "legacy-report" {
  export interface Result { name: string; ok: boolean }
  export function summarise(results: Result[]): { total: number; failed: string[] };
}
''',
        'types/globals.d.ts': '''
// Module augmentation: add a field to a global type.
// The empty export makes this file a module, which declare global needs.
declare global {
  interface Window { __TEST_USER__?: { id: number; role: "admin" | "customer" } }
}
export {};
''',
        'src/main.ts': '''
import { summarise } from "legacy-report";

const report = summarise([{ name: "login", ok: true }, { name: "cart", ok: false }]);
console.log(report.failed.join(", "));

summarise([{ name: "x", passed: true }]);          // wrong field name, caught by the .d.ts

// In browser test code: typed access to a value the app puts on window
function testUser(win: Window) { return win.__TEST_USER__?.role ?? "anonymous"; }
void testUser;
''',
    }, 'npx tsc -p . --pretty false', 'Declaration files and module augmentation', show=['vendor/legacy-report.js', 'types/legacy-report.d.ts', 'types/globals.d.ts', 'src/main.ts'],
        expect='fail', badge='🔷 tsc finds 1 error', ts_errors=1),
    'jsdoc': test({
        'package.json': pkg('jsdoc-check', 'module'),
        'tsconfig.json': json.dumps({'compilerOptions': {'allowJs': True, 'checkJs': True, 'noEmit': True, 'strict': True, 'target': 'esnext', 'module': 'nodenext', 'types': ['node']}, 'include': ['src']}, indent=2),
        'src/cart.js': '''
// Plain JavaScript, checked by TypeScript through JSDoc comments

/**
 * @typedef {{ sku: string, price: number, qty: number }} Line
 */

/**
 * @param {Line[]} lines
 * @param {{ coupon?: "SAVE10" | "SAVE20" }} [options]
 * @returns {number}
 */
export function cartTotal(lines, options = {}) {
  const sum = lines.reduce((s, l) => s + l.price * l.qty, 0);
  const off = { SAVE10: 0.1, SAVE20: 0.2 }[options.coupon ?? "SAVE10"] ?? 0;
  return options.coupon ? sum * (1 - off) : sum;
}

cartTotal([{ sku: "PEN", price: "40", qty: 1 }]);
cartTotal([], { coupon: "FREE" });
''',
    }, 'npx tsc -p . --pretty false', 'Type checking plain JavaScript with JSDoc', show=['src/cart.js'], expect='fail', badge='🔷 tsc finds 2 errors', ts_errors=2),
    'migrate': show('''
# Step 1: check JavaScript without changing it
#   tsconfig.json: "allowJs": true, "checkJs": false, "strict": false
# Step 2: turn on checkJs for one folder at a time with // @ts-check at the top of files
# Step 3: rename files to .ts, starting with leaf modules (utils, test data builders)
# Step 4: add types to public functions, page objects and API clients
# Step 5: turn on "strict": true, fix errors folder by folder
# Step 6: add tsc --noEmit to CI so new code cannot add type errors

npx tsc --noEmit                      # fails the CI job on any type error
npx tsc --noEmit --watch              # keep checking while you edit
''', 'A safe path from JavaScript to TypeScript', lang='bash', note='A plan, not a single command'),
    'tools': show('''
# Type check only (the source of truth)
npx tsc --noEmit

# Run TypeScript directly
node src/main.ts                      # Node.js 23.6+, strips erasable types, no checking
npx tsx src/main.ts                   # also handles enums, decorators and path aliases

# Build for publishing a library
npx tsc                               # emits .js and .d.ts files into outDir

# Bundle for the browser
npx esbuild src/app.ts --bundle --outfile=dist/app.js
npx vite build
''', 'Running and building TypeScript', lang='bash', note='Tool choices'),
    'scenario': ts('''
// A typed page object base with a generic "wait for" helper and typed test data
type Role = "admin" | "customer";
interface TestUser { email: string; password: string; role: Role }

interface Locator { textContent(): Promise<string>; click(): Promise<void>; fill(v: string): Promise<void> }
interface PageLike { locator(selector: string): Locator; goto(url: string): Promise<void> }

abstract class Page<TReady extends string = string> {
  constructor(protected readonly page: PageLike) {}
  abstract readonly path: string;
  async open(): Promise<this> { await this.page.goto(this.path); return this; }
  protected el(selector: string) { return this.page.locator(selector); }
}

class LoginPage extends Page {
  readonly path = "/login";
  async loginAs(user: TestUser): Promise<DashboardPage> {
    await this.el("#email").fill(user.email);
    await this.el("#password").fill(user.password);
    await this.el("button[type=submit]").click();
    return new DashboardPage(this.page);
  }
}
class DashboardPage extends Page {
  readonly path = "/dashboard";
  greeting() { return this.el("h1").textContent(); }
}

// A fake page so the example runs without a browser
const log: string[] = [];
const fake: PageLike = {
  async goto(url) { log.push(`goto ${url}`); },
  locator: sel => ({ async fill(v) { log.push(`fill ${sel}`); }, async click() { log.push(`click ${sel}`); }, async textContent() { return "Welcome, Asha"; } }),
};

const admin: TestUser = { email: "asha@shop.test", password: "s3cret!", role: "admin" };
const dash = await (await new LoginPage(fake).open()).loginAs(admin);
console.log(await dash.greeting(), log);
''', 'A typed page object hierarchy', options={'erasableSyntaxOnly': False}, run=False),
}

PARTS = [
    part('classes', '🏛️', 'Classes in TypeScript', '''
<p>TypeScript adds <b>access modifiers</b> to classes. <code>public</code> is the default, <code>protected</code> allows subclasses, and <code>private</code> allows only the class itself. <code>readonly</code> blocks changes after the constructor, <code>abstract</code> marks a class or method that subclasses must complete, <code>implements</code> checks a class against an interface, and <code>override</code> confirms that a method replaces one from the parent.</p>
[[classes]]
<p>TypeScript's <code>private</code> is a compile time check only. The value is still on the object at run time. JavaScript's <code>#private</code> is enforced by the engine, so prefer it for real secrets.</p>
[[private]]
<div class="note"><code>constructor(private readonly path: string)</code> is a <b>parameter property</b>: it declares and assigns the field in one go. Like enum, it creates run time code, so <code>erasableSyntaxOnly</code> and Node.js type stripping do not allow it. Write the field and the assignment out if you run .ts files directly.</div>
''', qa=['Playwright', 'Selenium'], qa_why='Typed base pages with abstract methods and protected helpers are the backbone of large page object frameworks.',
        kw=['class', 'public', 'private', 'protected', 'readonly', 'abstract class', 'abstract method', 'implements', 'override', 'parameter properties', '#private', 'access modifiers']),
    part('decorators', '🎀', 'Decorators', '''
<p>TypeScript 5 supports the standard decorators proposal. A method decorator is a function that receives the original method and a context object, and returns a replacement. Decorators stack: the one closest to the method wraps first.</p>
[[decorators]]
<div class="tip">This is how some frameworks add steps to reports. In Playwright the built in way is <code>await test.step("Pay with card", async () => …)</code>, and a decorator like <code>@step</code> can call it for you so every page object method shows up as a step in the HTML report and the trace viewer.</div>
''', qa=['Playwright'], qa_why='Step decorators put every page object action into the test report without extra code in each method.',
        kw=['decorators', 'method decorator', 'ClassMethodDecoratorContext', 'stage 3 decorators', 'experimentalDecorators', 'test.step', 'retry decorator']),
    part('dts', '📜', 'Declaration files and augmentation', '''
<p>A <b>declaration file</b> (<code>.d.ts</code>) contains only types. It describes JavaScript code that has no types of its own. Most npm packages ship one, and others have one in <code>@types/…</code>. <b>Module augmentation</b> adds to existing types, such as a field on <code>Window</code> or a custom matcher on <code>expect</code>.</p>
[[dts]]
<div class="tip">Custom Playwright matchers are typed by augmenting <code>PlaywrightTest.Matchers</code>, and custom Cypress commands by augmenting <code>Cypress.Chainable</code> in a <code>.d.ts</code> file.</div>
''', qa=['Playwright', 'Cypress'], qa_why='Custom commands, custom matchers and app globals in tests all need declaration files or augmentation.',
        kw=['declaration file', '.d.ts', 'declare module', 'declare global', 'module augmentation', '@types', 'DefinitelyTyped', 'custom matchers', 'Cypress.Chainable']),
    part('jsdoc', '📝', 'Checking JavaScript with JSDoc', '''
<p>You can get most of the safety of TypeScript without renaming a single file. With <code>checkJs</code>, or <code>// @ts-check</code> at the top of a file, TypeScript reads types from <b>JSDoc</b> comments and reports the same errors.</p>
[[jsdoc]]
''', qa=True, qa_why='Many existing JavaScript test suites can get type checking today with JSDoc and checkJs.',
        kw=['JSDoc', 'checkJs', '@ts-check', 'allowJs', '@param', '@returns', '@typedef', 'type checking JavaScript']),
    part('migrate', '🚚', 'Moving a project to TypeScript, and the tools around it', '''
<p>Move in small, safe steps. Every step keeps the project working, and CI keeps you from going backwards.</p>
[[migrate]]
[[tools]]
<div class="warn">Path aliases such as <code>@pages/login</code> in <code>paths</code> are only understood by tsc and by tools that read tsconfig. Plain Node.js does not resolve them. Use <code>package.json</code> <code>"imports"</code> with <code>#pages/*</code> instead, which works everywhere.</div>
''', qa=True, qa_why='Moving a test suite to TypeScript step by step is a common project for senior testers.',
        kw=['migration', 'JavaScript to TypeScript', 'allowJs', 'tsc --noEmit', 'tsx', 'esbuild', 'vite', 'path aliases', 'package imports', 'CI type check']),
    part('scenario', '🎬', 'Real world scenario: a typed page object hierarchy', '''
<div class="scenario"><b>The situation</b>The UI suite has 60 page objects. New pages often forget the path, and helpers return untyped values.</div>
[[scenario]]
<p>An abstract <code>path</code> forces every page to declare its URL, <code>protected el()</code> keeps raw locators inside page objects, and returning <code>DashboardPage</code> from <code>loginAs</code> makes the next step in a test auto complete. In a real project, <code>PageLike</code> is Playwright's <code>Page</code> type.</p>
''', qa=['Playwright'], kw=['page object model', 'abstract class', 'typed page object', 'fluent page objects', 'protected', 'test data types']),
]

INFO = {'title': 'TypeScript at project scale', 'panels': [
    panel([['e', '🏛️'], ['t', 'abstract isLoaded()', {'b': 1}]], 'Classes', 'Modifiers, abstract, implements.', '#private for real secrets.'),
    panel([['e', '🎀'], ['t', '@step("Pay")', {'b': 1}]], 'Decorators', 'Wrap methods once.', 'Steps and retries everywhere.'),
    panel([['e', '📜'], ['t', 'declare module "x"', {'b': 1}]], 'Declarations', 'Types for untyped code.', 'Augment globals and matchers.'),
    panel([['e', '🚚'], ['t', 'tsc --noEmit in CI', {'b': 1}]], 'Migrate safely', 'JSDoc first, then .ts.', 'Strict at the end.')],
    'remember': 'Use abstract bases and protected helpers for page objects, #private for secrets, declaration files for untyped code, and move to TypeScript in small checked steps.'}

REAL = [
    ['🧱', 'A UI test framework', 'Made its BasePage abstract with an abstract path. Thirteen pages that had silently opened the home page were fixed on the first compile.'],
    ['📜', 'An old in house library', 'Got a hand written .d.ts file. The test team used it for months before the library itself was rewritten.'],
    ['🚚', 'A 900 file test suite', 'Moved to TypeScript over six weeks with checkJs first, then one folder per week, without a single red build.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter covers TypeScript at project scale: classes with access modifiers, decorators, declaration files, JSDoc checking and moving a project to TypeScript.',
        'यह अध्याय project स्तर पर TypeScript सिखाता है: access modifiers वाली classes, decorators, declaration files, JSDoc checking और migration।',
        'ಈ ಅಧ್ಯಾಯ project ಮಟ್ಟದ TypeScript: classes, decorators, declaration files, JSDoc ಮತ್ತು migration.',
        'ଏହି ଅଧ୍ୟାୟ project ସ୍ତର TypeScript: classes, decorators, declaration files, JSDoc ଓ migration।',
        'يتناول هذا الفصل TypeScript على مستوى المشروع: الأصناف ومعدلات الوصول والمزخرفات وملفات التصريح وفحص JSDoc والانتقال إلى TypeScript.',
        'Dieses Kapitel behandelt TypeScript im Projekt: Klassen mit Modifikatoren, Dekoratoren, Deklarationsdateien, JSDoc und Migration.'),
    say('classes', 'Classes', 'public, protected and private control access. abstract forces subclasses to complete a method, and JavaScript hash private hides a field at run time.',
        'public, protected और private access तय करते हैं। abstract subclasses से method पूरा करवाता है, और hash private run time पर छिपाता है।',
        'public, protected, private access ನಿಯಂತ್ರಿಸುತ್ತವೆ. abstract subclass ನಿಂದ method ಪೂರ್ಣಗೊಳಿಸುತ್ತದೆ.',
        'public, protected, private access ନିୟନ୍ତ୍ରଣ କରେ। abstract subclass ରୁ method ପୂରଣ କରାଏ।',
        'تتحكم public وprotected وprivate في الوصول، وتجبر abstract الأصناف الفرعية على إكمال الدالة، ويخفي private بعلامة # الحقل وقت التشغيل.',
        'public, protected und private steuern den Zugriff. abstract erzwingt Methoden in Unterklassen, #private versteckt Felder wirklich.'),
    say('decorators', 'Decorators', 'A method decorator receives the method and a context and returns a replacement, which can log a step or retry.',
        'Method decorator method और context पाता है और बदला हुआ method लौटाता है, जो step log या retry कर सकता है।',
        'Method decorator method ಮತ್ತು context ಪಡೆದು ಬದಲಿ method ಕೊಡುತ್ತದೆ.',
        'Method decorator method ଓ context ପାଇ ବଦଳ method ଦିଏ।',
        'يستقبل مزخرف الدالة الدالة وسياقها ويعيد بديلًا يمكنه تسجيل خطوة أو إعادة المحاولة.',
        'Ein Methodendekorator erhält Methode und Kontext und liefert einen Ersatz, der loggt oder wiederholt.'),
    say('dts', 'Declaration files', 'A d ts file holds only types for JavaScript that has none. Module augmentation adds to existing types, such as Window or expect.',
        'd ts file में केवल types होते हैं। Module augmentation मौजूद types में जोड़ता है, जैसे Window या expect।',
        'd ts file ನಲ್ಲಿ types ಮಾತ್ರ. Augmentation ಇರುವ types ಗೆ ಸೇರಿಸುತ್ತದೆ.',
        'd ts file ରେ କେବଳ types। Augmentation ଥିବା types ରେ ଯୋଡ଼େ।',
        'يحوي ملف d.ts أنواعًا فقط لشيفرة JavaScript بلا أنواع، ويضيف تعزيز الوحدات إلى الأنواع الموجودة مثل Window أو expect.',
        'Eine d.ts-Datei enthält nur Typen. Augmentation erweitert bestehende Typen wie Window oder expect.'),
    say('jsdoc', 'JSDoc', 'With checkJs, TypeScript reads types from JSDoc comments and checks plain JavaScript files without renaming them.',
        'checkJs के साथ TypeScript JSDoc comments से types पढ़ता है और JavaScript files बिना नाम बदले जांचता है।',
        'checkJs ಜೊತೆ TypeScript JSDoc ನಿಂದ types ಓದಿ JavaScript ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'checkJs ସହ TypeScript JSDoc ରୁ types ପଢ଼ି JavaScript ଯାଞ୍ଚ କରେ।',
        'مع checkJs تقرأ TypeScript الأنواع من تعليقات JSDoc وتفحص ملفات JavaScript دون إعادة تسميتها.',
        'Mit checkJs liest TypeScript Typen aus JSDoc und prüft JavaScript ohne Umbenennen.'),
    say('migrate', 'Migration', 'Move in small steps: allow JavaScript, check it, rename leaf files, add types, turn on strict, and run tsc in CI.',
        'छोटे कदमों में बढ़ें: JavaScript allow करें, जांचें, leaf files rename करें, types जोड़ें, strict चालू करें और CI में tsc चलाएं।',
        'ಸಣ್ಣ ಹೆಜ್ಜೆಗಳಲ್ಲಿ: allowJs, checkJs, rename, types, strict, CI ನಲ್ಲಿ tsc.',
        'ଛୋଟ ପଦକ୍ଷେପ: allowJs, checkJs, rename, types, strict, CI ରେ tsc।',
        'انتقل بخطوات صغيرة: اسمح بـ JavaScript وافحصها وأعد تسمية الملفات الطرفية وأضف الأنواع وشغل strict وشغل tsc في CI.',
        'Gehe in kleinen Schritten: JavaScript erlauben, prüfen, umbenennen, typisieren, strict, tsc in CI.'),
    say('scenario', 'Scenario', 'An abstract path forces every page to declare its URL, and returning the next page type makes test steps auto complete.',
        'Abstract path हर page से URL बताने को कहता है, और अगला page type लौटाने से test steps auto complete होते हैं।',
        'Abstract path ಪ್ರತಿ page URL ಘೋಷಿಸುವಂತೆ ಮಾಡುತ್ತದೆ.',
        'Abstract path ପ୍ରତି page URL ଘୋଷଣା କରାଏ।',
        'يجبر المسار المجرد كل صفحة على تعريف عنوانها، وإرجاع نوع الصفحة التالية يجعل خطوات الاختبار تكمل تلقائيًا.',
        'Ein abstrakter Pfad zwingt jede Seite zur URL, und der nächste Seitentyp macht Testschritte vervollständigbar.'),
    say('practice', 'Hands-on', 'Practise a class with a private field, an abstract style check, a method wrapper like a decorator, and a step log.',
        'Private field वाली class, abstract जैसा check, decorator जैसा method wrapper और step log का अभ्यास करें।',
        'Private field class, abstract check, decorator wrapper ಮತ್ತು step log ಅಭ್ಯಾಸ ಮಾಡಿ.',
        'Private field class, abstract check, decorator wrapper ଓ step log ଅଭ୍ୟାସ କରନ୍ତୁ।',
        'تدرب على صنف بحقل خاص وفحص يشبه abstract وغلاف دالة يشبه المزخرف وسجل خطوات.',
        'Übe eine Klasse mit privatem Feld, eine abstrakte Prüfung, einen Methoden-Wrapper und ein Schrittprotokoll.'),
]

QUIZ = [
    quiz('e', 'Which modifier lets subclasses use a member but hides it from outside code?', ['protected', 'private', 'public', 'readonly'], 0, 'Family only.', 'private allows only the class itself.'),
    quiz('e', 'What does abstract on a method mean?', ['Subclasses must implement it', 'It runs first', 'It is private', 'It is static'], 0, 'To be completed.', 'A class with abstract members cannot be created directly.'),
    quiz('e', 'What is a .d.ts file?', ['A file with only type declarations', 'A compiled JavaScript file', 'A test file', 'A config file'], 0, 'Declarations.', 'It describes code that lives elsewhere.'),
    quiz('m', 'Is a TypeScript private field visible at run time?', ['Yes, private is a compile time check only', 'No, it is removed', 'It throws when read', 'Only in strict mode'], 0, 'Erased checks.', 'Use #private for real run time privacy.'),
    quiz('m', 'What does implements Searchable check?', ['That the class has every member of the interface', 'That it extends a class', 'It adds the methods', 'It runs the methods'], 0, 'A contract.', 'It adds no code.'),
    quiz('m', 'Why do parameter properties fail with erasableSyntaxOnly?', ['They create assignment code in the constructor', 'They are deprecated', 'They are slow', 'They need decorators'], 0, 'Not erasable.', 'Stripping the types would remove the assignment.'),
    quiz('m', 'Which tsconfig option lets TypeScript check plain .js files?', ['checkJs', 'strict', 'noEmit', 'isolatedModules'], 0, 'Check JavaScript.', 'allowJs includes them, checkJs reports errors in them.'),
    quiz('h', 'Two decorators @step and @retry are stacked above a method, step on top. Which wraps the original method first?', ['@retry, the one closest to the method', '@step', 'Both at once', 'Neither'], 0, 'Bottom up.', 'Decorators are applied from the closest one outwards.'),
    quiz('h', 'How do you add a custom matcher type to Playwright expect?', ['Augment the Matchers interface in a declaration', 'Edit node_modules', 'Use any', 'It is not possible'], 0, 'Module augmentation.', 'declare global or declare module merges into the existing interface.'),
    quiz('h', 'Why might @pages/login imports fail when running node src/main.ts?', ['Node.js does not read tsconfig paths', 'The file is missing', 'TypeScript forbids it', 'Imports must be relative'], 0, 'tsc only.', 'Use package.json imports with #pages/* instead.'),
    quiz('x', 'What does returning Promise<this> from open() give subclasses?', ['open() returns the subclass type, so chained calls stay typed', 'A copy of the page', 'A base page type', 'Nothing special'], 0, 'Polymorphic this.', 'new LoginPage(page).open() is typed as LoginPage.'),
    quiz('x', 'What does tsc --noEmit do in CI?', ['Type checks the project and fails on errors without writing files', 'Builds the project', 'Runs the tests', 'Formats the code'], 0, 'Check only.', 'It is the gate that keeps type errors out of main.'),
]

CALC = [
    calc('e', 'The classes example has four mistakes after the console.log. How many errors does tsc report?', '4', 'One per line.', ['protected, private, abstract creation and a missing abstract method.']),
    calc('e', 'ProductsPage.open() is called twice. What visit number does the second call print?', '2', 'The #visits counter.', ['It starts at 0 and goes up once per call.']),
    calc('m', 'The pay method fails until attempt 3, and @retry(3) allows 3 tries. On which attempt does it succeed?', '3', 'Count tries.', ['Attempts 1 and 2 throw, attempt 3 returns "paid".']),
    calc('m', 'A suite of 900 files moves 150 files a week to TypeScript. How many weeks?', '6', 'Divide.', ['<span class="eq">900 ÷ 150 = 6</span>']),
    calc('m', 'The JSDoc example has a wrong price type and a wrong coupon. How many errors?', '2', 'One each.', ['"40" is not a number, and "FREE" is not one of the coupons.']),
    calc('h', 'A base page has 3 abstract members. A subclass implements 2. How many errors on that class?', '1', 'One error listing the missing member.', ['tsc reports the class once for the missing member.'], alt=['1']),
    calc('h', 'Decorators wrap from the closest one out. With @a @b @c above a method, which runs first when the method is called?', 'a', 'The outermost wrapper runs first.', ['c wraps the method, b wraps c, a wraps b.', 'Calling enters a first.']),
    calc('x', 'In the scenario, how many log lines does loginAs add, not counting open()?', '3', 'Two fills and a click.', ['fill #email, fill #password, click the button.']),
]

EX = [
    ex('account', 'e', 'A class with a private field', '<p>Write a class <code>Account</code> with a JavaScript private <code>#balance</code> that starts at 0, a <code>deposit(n)</code> that rejects amounts that are not positive by throwing a <code>RangeError</code>, and a <code>balance</code> getter.</p>',
       'class Account {\n  \n}\n',
       [('(() => { const a = new Account(); a.deposit(50); a.deposit(25); return [a.balance, Object.keys(a).length, JSON.stringify(a)]; })()', [75, 0, '{}']),
        ('(() => { try { new Account().deposit(-5); } catch (e) { return e.name; } })()', 'RangeError')],
       'class Account {\n  #balance = 0;\n  deposit(n) {\n    if (!(n > 0)) throw new RangeError("amount must be positive");\n    this.#balance += n;\n  }\n  get balance() {\n    return this.#balance;\n  }\n}', hint='<code>#balance = 0;</code> as a class field, and <code>get balance()</code> to read it.', why='#private fields never appear in Object.keys or JSON, unlike TypeScript private.'),
    ex('abstract', 'm', 'Enforce an abstract method at run time', '<p>JavaScript has no <code>abstract</code>. Write a class <code>BasePage</code> whose constructor throws a <code>TypeError</code> when called with <code>new BasePage()</code> directly, and whose <code>isLoaded()</code> throws <code>"isLoaded is not implemented"</code> unless a subclass overrides it.</p>',
       'class BasePage {\n  \n}\n',
       [('(() => { try { new BasePage(); } catch (e) { return e.name; } })()', 'TypeError'),
        ('(() => { class A extends BasePage {} try { new A().isLoaded(); } catch (e) { return e.message; } })()', 'isLoaded is not implemented'),
        ('(() => { class B extends BasePage { isLoaded() { return true; } } return new B().isLoaded(); })()', True)],
       'class BasePage {\n  constructor() {\n    if (new.target === BasePage) throw new TypeError("BasePage is abstract");\n  }\n  isLoaded() {\n    throw new Error("isLoaded is not implemented");\n  }\n}', hint='<code>new.target</code> tells you which class was used with new.', why='TypeScript catches both mistakes at compile time, and this pattern catches them in plain JavaScript.'),
    ex('wrap', 'h', 'A decorator by hand', '<p>Write <code>withStep(obj, name, title, log)</code> that replaces the method <code>obj[name]</code> with a wrapper. The wrapper calls the original with the same <code>this</code> and arguments, then pushes <code>"✔ " + title</code> to the <code>log</code> array, or <code>"✖ " + title</code> if it threw, and rethrows.</p>',
       'function withStep(obj, name, title, log) {\n  \n}\n',
       [('(async () => { const log = []; const page = { n: 2, async double() { return this.n * 2; }, async boom() { throw new Error("x"); } }; withStep(page, "double", "Double", log); withStep(page, "boom", "Boom", log); const r = await page.double(); await page.boom().catch(() => {}); return [r, log]; })()', [4, ['✔ Double', '✖ Boom']])],
       'function withStep(obj, name, title, log) {\n  const original = obj[name];\n  obj[name] = async function (...args) {\n    try {\n      const result = await original.apply(this, args);\n      log.push("✔ " + title);\n      return result;\n    } catch (e) {\n      log.push("✖ " + title);\n      throw e;\n    }\n  };\n}', hint='Keep the original, then assign a regular <code>async function</code> so <code>this</code> still works.', why='A method decorator does exactly this, at class definition time.'),
    ex('steplog', 'x', 'A typed step log', '<p>Write <code>createSteps()</code> that returns <code>{ step, report }</code>. <code>await step(title, fn)</code> runs <code>fn</code>, records <code>{ title, ok, ms }</code> where ms is a whole number of milliseconds, and returns or rethrows. <code>report()</code> returns titles with a tick or a cross, such as <code>"✔ Login"</code>.</p>',
       'function createSteps() {\n  \n}\n',
       [('(async () => { const { step, report } = createSteps(); await step("Login", async () => 1); await step("Pay", async () => { throw new Error("no"); }).catch(() => {}); return report(); })()', ['✔ Login', '✖ Pay']),
        ('(async () => { const { step } = createSteps(); return await step("x", async () => 42); })()', 42)],
       'function createSteps() {\n  const steps = [];\n  async function step(title, fn) {\n    const start = Date.now();\n    try {\n      const value = await fn();\n      steps.push({ title, ok: true, ms: Math.round(Date.now() - start) });\n      return value;\n    } catch (e) {\n      steps.push({ title, ok: false, ms: Math.round(Date.now() - start) });\n      throw e;\n    }\n  }\n  return { step, report: () => steps.map(s => (s.ok ? "✔ " : "✖ ") + s.title) };\n}',
       hint='Record the result in both the try and the catch branch, then rethrow.', why='This is a small copy of Playwright test.step, which records the same data for its HTML report.'),
]

T = {
    'slug': 'ts-projects', 'title': 'TypeScript classes and real projects', 'short': 'TypeScript projects', 'emoji': '🏛️', 'module': MODULE, 'minutes': 18,
    'lead': 'TypeScript at the scale of a real project: access modifiers, abstract classes and interfaces, TypeScript private against #private, standard decorators for steps and retries, declaration files and module augmentation, checking JavaScript with JSDoc, moving a project to TypeScript, and a typed page object hierarchy.',
    'desc': 'TypeScript classes and projects: public, private, protected, readonly, abstract, implements, override, parameter properties, decorators, .d.ts, declare module, augmentation, JSDoc checkJs, migration, tsc --noEmit, tsx and typed page objects.',
    'summary': 'Classes with access modifiers, abstract members and interfaces, TypeScript private compared with #private, standard decorators that log steps and retry, declaration files and module augmentation, type checking JavaScript with JSDoc, a safe migration plan and the tools to run TypeScript, and a typed page object hierarchy.',
    'keywords': ['TypeScript classes', 'abstract class', 'access modifiers', 'private', '#private', 'decorators', '.d.ts', 'declaration files', 'module augmentation', 'JSDoc', 'checkJs', 'migration', 'tsc --noEmit', 'page object', 'interview'],
    'qa_intro': 'Large automation frameworks are TypeScript projects. Abstract base pages, step decorators, typed custom commands and a safe migration plan are what keep them maintainable.',
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'ex': EX,
}
