# Chapter 20: lambdas, functional interfaces, method references, composing functions, interface default methods and how lambdas run inside the JVM.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

CODES = {
    'anon': j('''
import java.util.*;

class Main {
    public static void main(String[] args) {
        List<String> tests = new ArrayList<>(List.of("checkout", "login", "search", "cart"));

        // Before Java 8: an anonymous class just to say "compare by length"
        Collections.sort(tests, new Comparator<String>() {
            @Override
            public int compare(String a, String b) {
                return Integer.compare(a.length(), b.length());
            }
        });
        System.out.println(tests);

        // Java 8: the same behaviour as a lambda
        tests.sort((a, b) -> b.length() - a.length());
        System.out.println(tests);
    }
}
''', 'An anonymous class and the lambda that replaces it'),
    'syntax': j('''
import java.util.function.*;

class Main {
    public static void main(String[] args) {
        Runnable hello = () -> System.out.println("no inputs");
        Function<String, Integer> len = s -> s.length();               // one input, no brackets needed
        BinaryOperator<Integer> add = (a, b) -> a + b;                  // two inputs
        BiFunction<Integer, Integer, Integer> max = (Integer a, Integer b) -> {
            if (a > b) return a;                                       // a block body needs return
            return b;
        };
        Predicate<String> empty = (var s) -> s.isBlank();               // var in lambda parameters, Java 11

        hello.run();
        System.out.println(len.apply("Brainy"));
        System.out.println(add.apply(40, 2));
        System.out.println(max.apply(7, 3));
        System.out.println(empty.test("   "));
    }
}
''', 'The five shapes a lambda can take'),
    'target': j('''
import java.util.concurrent.Callable;
import java.util.function.Supplier;

class Main {
    public static void main(String[] args) throws Exception {
        // The same lambda text becomes different types, decided by where it is used (the target type)
        Supplier<String> s = () -> "ready";
        Callable<String> c = () -> "ready";
        System.out.println(s.get() + " " + c.call());

        Object o = () -> "ready";        // Object is not a functional interface
    }
}
''', 'A lambda needs a target type', expect='compile'),
    'builtins': j('''
import java.util.*;
import java.util.function.*;

class Main {
    public static void main(String[] args) {
        Predicate<Integer> passed = code -> code >= 200 && code < 300;   // T -> boolean
        Function<String, String> slug = t -> t.toLowerCase().replace(' ', '-');  // T -> R
        Consumer<String> log = msg -> System.out.println("[LOG] " + msg); // T -> nothing
        Supplier<String> email = () -> "user" + new Random(7).nextInt(1000) + "@shop.test"; // nothing -> T
        UnaryOperator<String> trim = String::strip;                       // T -> T
        BiFunction<String, Integer, String> pad = (s, n) -> s + ".".repeat(n);
        IntPredicate even = n -> n % 2 == 0;                              // primitive version, no boxing

        System.out.println(passed.test(201) + " " + passed.test(404));
        System.out.println(slug.apply("Add To Cart"));
        log.accept("suite started");
        System.out.println(email.get());
        System.out.println("[" + trim.apply("  hi  ") + "]");
        System.out.println(pad.apply("Loading", 3));
        System.out.println(even.test(10));
    }
}
''', 'The everyday interfaces in java.util.function'),
    'custom': j('''
@FunctionalInterface
interface Discount {
    double apply(double price);                       // exactly one abstract method

    default Discount then(Discount next) {            // default methods are allowed
        return p -> next.apply(apply(p));
    }

    static Discount percent(double pct) {             // static factory methods too
        return p -> p - p * pct / 100;
    }
}

class Main {
    public static void main(String[] args) {
        Discount festive = Discount.percent(10);
        Discount coupon = p -> p - 50;
        Discount both = festive.then(coupon);
        System.out.println(festive.apply(1000));
        System.out.println(both.apply(1000));
    }
}
''', 'Your own functional interface with default and static methods'),
    'notfi': j('''
@FunctionalInterface
interface Broken {
    void first();
    void second();
}

class Main {
    public static void main(String[] args) { }
}
''', '@FunctionalInterface catches a second abstract method', expect='compile'),
    'refs': j('''
import java.util.*;
import java.util.function.*;

class Main {
    record User(String name) {}

    static boolean isAdmin(String n) { return n.startsWith("admin"); }

    public static void main(String[] args) {
        List<String> names = List.of("admin_asha", "ravi", "admin_meera");

        // 1. Static method: ClassName::staticMethod
        Predicate<String> admin = Main::isAdmin;
        // 2. Method of one particular object: object::method
        String prefix = "Hello, ";
        Function<String, String> greet = prefix::concat;
        // 3. Instance method of whatever object comes in: ClassName::instanceMethod
        Function<String, String> upper = String::toUpperCase;
        // 4. Constructor: ClassName::new
        Function<String, User> make = User::new;

        names.stream().filter(admin).map(upper).forEach(System.out::println);
        System.out.println(greet.apply("Ravi"));
        System.out.println(make.apply("Meera"));
    }
}
''', 'The four kinds of method reference'),
    'compose': j('''
import java.util.*;
import java.util.function.*;

class Main {
    record Result(String name, String status, int ms) {}

    public static void main(String[] args) {
        Predicate<Result> failed = r -> r.status().equals("FAIL");
        Predicate<Result> slow = r -> r.ms() > 1000;
        Function<String, String> trim = String::strip;
        Function<String, String> clean = trim.andThen(String::toLowerCase).andThen(s -> s.replace(' ', '_'));

        List<Result> results = new ArrayList<>(List.of(
            new Result("login", "PASS", 420), new Result("checkout", "FAIL", 2300),
            new Result("search", "PASS", 1800), new Result("cart", "FAIL", 300)));

        System.out.println(results.stream().filter(failed.or(slow)).map(Result::name).toList());
        System.out.println(results.stream().filter(failed.negate().and(slow)).map(Result::name).toList());
        System.out.println(clean.apply("  Add To Cart "));

        // Comparators compose too: by status, then slowest first
        results.sort(Comparator.comparing(Result::status).thenComparing(Result::ms, Comparator.reverseOrder()));
        results.forEach(r -> System.out.println(r.status() + " " + r.ms() + " " + r.name()));
    }
}
''', 'and, or, negate, andThen and Comparator chains'),
    'capture': j('''
import java.util.function.*;

class Main {
    public static void main(String[] args) {
        String env = "staging";                         // effectively final: never changed
        Supplier<String> url = () -> "https://" + env + ".shop.test";
        System.out.println(url.get());

        int count = 0;
        Runnable r = () -> count++;                     // a lambda may not change a local variable
    }
}
''', 'Lambdas capture effectively final variables only', expect='compile'),
    'counter': j('''
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.IntStream;

class Main {
    public static void main(String[] args) {
        // Need a counter inside a lambda? Use an object whose contents can change.
        AtomicInteger attempts = new AtomicInteger();
        IntStream.range(0, 3).forEach(i -> attempts.incrementAndGet());
        System.out.println("attempts = " + attempts.get());

        int[] box = {0};                                // the array reference is final, its slot is not
        IntStream.range(0, 5).forEach(i -> box[0] += i);
        System.out.println("sum = " + box[0]);
    }
}
''', 'Changing state from a lambda the safe way'),
    'thisref': j('''
class Main {
    String name = "outer object";

    void demo() {
        Runnable anon = new Runnable() {
            String name = "anonymous object";
            public void run() { System.out.println("anonymous class: this.name = " + this.name); }
        };
        Runnable lambda = () -> System.out.println("lambda:          this.name = " + this.name);
        anon.run();
        lambda.run();
    }

    public static void main(String[] args) {
        new Main().demo();
    }
}
''', 'this means different things in a lambda and an anonymous class'),
    'checked': j('''
import java.nio.file.*;
import java.util.*;
import java.util.function.*;

class Main {
    @FunctionalInterface
    interface ThrowingFunction<T, R> { R apply(T t) throws Exception; }

    // Wrap a function that may throw a checked exception into a plain Function
    static <T, R> Function<T, R> unchecked(ThrowingFunction<T, R> f) {
        return t -> {
            try { return f.apply(t); }
            catch (Exception e) { throw new RuntimeException(e.getMessage(), e); }
        };
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("data");
        Files.writeString(dir.resolve("a.txt"), "alpha");
        Files.writeString(dir.resolve("b.txt"), "beta");

        // Files.readString throws IOException, so it cannot be used directly in map(...)
        List<String> texts = List.of("a.txt", "b.txt").stream()
            .map(dir::resolve)
            .map(unchecked(Files::readString))
            .toList();
        System.out.println(texts);
    }
}
''', 'Checked exceptions and lambdas'),
    'javap': sh({'Main.java': '''
import java.util.function.Function;

class Main {
    public static void main(String[] args) {
        Function<String, Integer> len = s -> s.length();
        System.out.println(len.apply("lambda"));
    }
}
'''}, 'javac Main.java && java Main && echo "--- members of Main ---" && javap -p Main && echo "--- the lambda line in main ---" && javap -c -p Main | grep invokedynamic', 'What javac really produces for a lambda',
        shown='$ javac Main.java && java Main\n$ javap -p Main\n$ javap -c -p Main | grep invokedynamic', replace=[(r'#\d+(:#?\d+)?', '#n'), (r' +//', '  //')]),
    'retry': j('''
import java.util.function.*;

class Main {
    // A retry helper for flaky calls: the work and the success check are passed in as lambdas
    static <T> T retry(Supplier<T> call, Predicate<T> ok, int times) {
        T last = null;
        for (int attempt = 1; attempt <= times; attempt++) {
            last = call.get();
            System.out.println("attempt " + attempt + " -> " + last);
            if (ok.test(last)) return last;
        }
        throw new IllegalStateException("still failing after " + times + " attempts: " + last);
    }

    public static void main(String[] args) {
        int[] calls = {0};
        Supplier<Integer> flakyStatus = () -> ++calls[0] < 3 ? 503 : 200;   // fails twice, then works
        int status = retry(flakyStatus, code -> code == 200, 5);
        System.out.println("final status " + status);
    }
}
''', 'Real world: a retry helper for a flaky service'),
}

DG = {
    'lambda-inside': {'t': 'What happens when a lambda line runs', 'w': 900, 'h': 300, 'mw': 640,
        'n': [['src', 20, 30, 190, 70, 'Main.java', {'c': 0, 'sh': 'doc', 'sub': 's -> s.length()'}],
              ['javac', 250, 30, 160, 70, 'javac', {'c': 2, 'sub': 'body becomes a\nprivate method'}],
              ['cls', 450, 30, 190, 70, 'Main.class', {'c': 3, 'sh': 'doc', 'sub': 'lambda$main$0 +\ninvokedynamic'}],
              ['indy', 680, 30, 200, 70, 'First run of the line', {'c': 5, 'sub': 'bootstrap method called'}],
              ['meta', 680, 180, 200, 80, 'LambdaMetafactory', {'c': 1, 'sub': 'spins a small hidden class\nthat implements Function'}],
              ['obj', 400, 190, 230, 70, 'Function object', {'c': 4, 'sub': 'apply() calls lambda$main$0'}],
              ['next', 40, 190, 300, 70, 'Every later run', {'c': 7, 'sub': 'reuses the linked call site,\nno new class is made'}]],
        'e': [['src', 'javac'], ['javac', 'cls'], ['cls', 'indy'], ['indy', 'meta'], ['meta', 'obj'], ['obj', 'next', {'d': 1}]],
        'st': [[['src'], 'You write a lambda. It has no class of its own in the source.'],
               [['javac', 'src>javac'], 'javac moves the lambda body into a private method of Main, named something like lambda$main$0.'],
               [['cls', 'javac>cls'], 'Where the lambda was, javac writes one invokedynamic instruction. No extra .class file is created, unlike an anonymous class (Main$1.class).'],
               [['indy', 'cls>indy'], 'The first time that line runs, the JVM calls a bootstrap method to decide what the instruction should do.'],
               [['meta', 'indy>meta'], 'LambdaMetafactory creates a tiny hidden class at run time that implements Function and forwards apply() to lambda$main$0.'],
               [['obj', 'meta>obj'], 'An object of that class is returned. A lambda that captures nothing is created once and shared.'],
               [['next', 'obj>next'], 'The call site is now linked. Later runs skip all of this, which is why lambdas are cheap after the first call.']]},
}

PARTS = [
    part('why', '💡', 'Why lambdas exist', '''
<p>Before Java 8, passing a small piece of <b>behaviour</b> (how to compare, what to do on a click, which items to keep) meant writing a whole anonymous class. Most of those lines were ceremony. A <b>lambda</b> is the same behaviour written as just the inputs, an arrow and the result.</p>
[[anon]]
<p>Think of a lambda as a sticky note with instructions that you hand to someone else. <code>sort</code> does the sorting work, and your lambda only answers the one question it needs answered: "which of these two comes first?"</p>
<div class="fun">Java 8 (2014) added lambdas, method references, streams, Optional and java.time in one release. It is still the biggest change the language has ever had, and almost every modern Java API, from Selenium waits to Spring, expects you to pass lambdas.</div>
''', kw=['lambda', 'anonymous class', 'Java 8', 'behaviour parameterization', 'Comparator', 'sort']),
    part('syntax', '✍️', 'Lambda syntax', '''
<p>A lambda is <code>(parameters) -&gt; body</code>. The compiler works out the parameter types from the context, so you rarely write them.</p>
<div class="tw"><table class="jt"><tr><th>Form</th><th>Example</th><th>When</th></tr>
<tr><td>No input</td><td><code>() -&gt; System.out.println("hi")</code></td><td>Runnable, Supplier</td></tr>
<tr><td>One input</td><td><code>s -&gt; s.length()</code></td><td>brackets are optional</td></tr>
<tr><td>Several inputs</td><td><code>(a, b) -&gt; a + b</code></td><td>brackets are required</td></tr>
<tr><td>Block body</td><td><code>x -&gt; { int y = x * 2; return y; }</code></td><td>more than one statement, needs return</td></tr>
<tr><td>Typed or var</td><td><code>(var s) -&gt; s.isBlank()</code></td><td>to add annotations such as @NonNull</td></tr></table></div>
[[syntax]]
<p>A lambda has no type of its own. Its type comes from where you put it, called the <b>target type</b>. The same text can become a Supplier or a Callable, but never a plain Object.</p>
[[target]]
''', kw=['lambda syntax', 'arrow', '->', 'block body', 'expression body', 'target type', 'type inference', 'var in lambda']),
    part('functional', '🧰', 'Functional interfaces', '''
<p>A <b>functional interface</b> is an interface with exactly <b>one abstract method</b>. A lambda is simply a short way to create an object of such an interface: the lambda body becomes that method. Default and static methods do not count, so an interface can have many of those and still be functional.</p>
<div class="viz" data-viz="jlambda"></div>
<div class="tw"><table class="jt"><tr><th>Interface</th><th>Method</th><th>Shape</th><th>Typical use in tests</th></tr>
<tr><td><code>Predicate&lt;T&gt;</code></td><td><code>test</code></td><td>T to boolean</td><td>filter results, wait conditions</td></tr>
<tr><td><code>Function&lt;T,R&gt;</code></td><td><code>apply</code></td><td>T to R</td><td>map a response to a field</td></tr>
<tr><td><code>Consumer&lt;T&gt;</code></td><td><code>accept</code></td><td>T to nothing</td><td>log, click, fill each item</td></tr>
<tr><td><code>Supplier&lt;T&gt;</code></td><td><code>get</code></td><td>nothing to T</td><td>create test data lazily</td></tr>
<tr><td><code>UnaryOperator&lt;T&gt;</code> <code>BinaryOperator&lt;T&gt;</code></td><td><code>apply</code></td><td>T to T, (T,T) to T</td><td>clean up a value, add two totals</td></tr>
<tr><td><code>BiFunction</code> <code>BiConsumer</code> <code>BiPredicate</code></td><td>two inputs</td><td>(T,U) to ...</td><td>Map.forEach((k, v) -&gt; ...)</td></tr>
<tr><td><code>IntPredicate</code> <code>ToIntFunction</code> <code>IntSupplier</code> ...</td><td>primitive versions</td><td>no boxing</td><td>fast number work</td></tr></table></div>
[[builtins]]
<p>You can write your own. Add <code>@FunctionalInterface</code> so the compiler checks that it really has one abstract method.</p>
[[custom]]
[[notfi]]
<div class="tip">Selenium's <code>wait.until(driver -&gt; driver.findElement(By.id("total")).isDisplayed())</code> takes a <code>Function&lt;WebDriver, T&gt;</code>. Now you know why a lambda fits there.</div>
''', kw=['functional interface', '@FunctionalInterface', 'SAM', 'single abstract method', 'Predicate', 'Function', 'Consumer', 'Supplier', 'UnaryOperator', 'BinaryOperator', 'BiFunction', 'IntPredicate', 'java.util.function']),
    part('method-refs', '🔗', 'Method references', '''
<p>When a lambda only calls one existing method, a <b>method reference</b> says the same thing even shorter, with <code>::</code>. <code>s -&gt; s.toUpperCase()</code> becomes <code>String::toUpperCase</code>.</p>
<div class="tw"><table class="jt"><tr><th>Kind</th><th>Method reference</th><th>Same as the lambda</th></tr>
<tr><td>Static method</td><td><code>Integer::parseInt</code></td><td><code>s -&gt; Integer.parseInt(s)</code></td></tr>
<tr><td>Method of a given object</td><td><code>System.out::println</code></td><td><code>x -&gt; System.out.println(x)</code></td></tr>
<tr><td>Method of the incoming object</td><td><code>String::length</code></td><td><code>s -&gt; s.length()</code></td></tr>
<tr><td>Constructor</td><td><code>ArrayList::new</code></td><td><code>() -&gt; new ArrayList&lt;&gt;()</code></td></tr></table></div>
[[refs]]
<div class="note">Use a method reference when it reads better. <code>map(User::name)</code> is clearer than <code>map(u -&gt; u.name())</code>, but a lambda with a little logic should stay a lambda.</div>
''', kw=['method reference', '::', 'static method reference', 'bound method reference', 'unbound method reference', 'constructor reference', 'System.out::println', 'ArrayList::new']),
    part('compose', '🧩', 'Composing functions', '''
<p>Functional interfaces come with default methods that join small pieces into bigger ones, like Lego bricks. <code>Predicate</code> has <code>and</code>, <code>or</code> and <code>negate</code>. <code>Function</code> has <code>andThen</code> and <code>compose</code>. <code>Comparator</code> has <code>comparing</code>, <code>thenComparing</code> and <code>reversed</code>.</p>
[[compose]]
<p>Real reports sort by several keys at once: failures first, then the slowest. A comparator chain says exactly that, in the order a person would say it.</p>
''', kw=['Predicate.and', 'Predicate.or', 'negate', 'Function.andThen', 'compose', 'Comparator.comparing', 'thenComparing', 'reversed', 'reverseOrder', 'function composition']),
    part('capture', '📦', 'Capturing variables and this', '''
<p>A lambda can read local variables from the code around it, but only if they are <b>effectively final</b>: assigned once and never changed. The lambda may run later, maybe on another thread, so Java copies the value in and forbids changes that would make the copy wrong.</p>
[[capture]]
<p>If you truly need a changing counter, use an object such as <code>AtomicInteger</code>. The variable still points to the same object, only the object's contents change.</p>
[[counter]]
<p>One more difference from anonymous classes: inside a lambda, <code>this</code> means the surrounding object. A lambda does not create a new scope for <code>this</code>.</p>
[[thisref]]
''', kw=['effectively final', 'capture', 'closure', 'local variable', 'AtomicInteger', 'this in lambda', 'lambda vs anonymous class', 'variable shadowing']),
    part('exceptions', '⚠️', 'Lambdas and checked exceptions', '''
<p>The methods of <code>Function</code>, <code>Consumer</code> and friends do not declare <code>throws</code>, so a lambda passed to them cannot throw a checked exception such as <code>IOException</code>. The usual fix is a small wrapper that turns it into an unchecked exception, keeping the original as the cause.</p>
[[checked]]
<div class="warn">Do not hide exceptions with an empty catch inside a lambda. A test that swallows an IOException will pass with wrong data, which is worse than a clear failure.</div>
''', kw=['checked exception', 'IOException', 'lambda exception', 'throwing function', 'wrapper', 'RuntimeException', 'UncheckedIOException']),
    part('inside', '🔬', 'How a lambda runs inside the JVM', '''
<p>An anonymous class becomes its own <code>.class</code> file (<code>Main$1.class</code>). A lambda does not. javac turns its body into a private method and leaves a single <code>invokedynamic</code> instruction where the lambda was. The first time that line runs, the JVM builds the object.</p>
<div class="viz" data-viz="flow" data-k="lambda-inside"></div>
[[javap]]
<p>This design (Java 8, JSR 335) lets the JVM choose the best way to make lambdas without changing your class files, and it is why a lambda that captures nothing costs almost nothing after the first call.</p>
''', kw=['invokedynamic', 'LambdaMetafactory', 'bootstrap method', 'hidden class', 'lambda$main$0', 'javap', 'bytecode', 'call site']),
    part('scenario', '🎬', 'Real world scenario: a retry helper', '''
<div class="scenario"><b>The situation</b>A payment sandbox sometimes answers 503 for a second or two. Tests fail at random, and people add <code>Thread.sleep</code> everywhere.</div>
[[retry]]
<p>The helper does not know what it is retrying. The <b>work</b> arrives as a <code>Supplier</code>, and the meaning of "success" arrives as a <code>Predicate</code>. The same helper now retries API calls, database checks or UI conditions, and it reports every attempt. This is the idea behind Awaitility's <code>await().until(...)</code> and Selenium's <code>FluentWait</code>.</p>
''', kw=['retry', 'flaky test', 'Supplier', 'Predicate', 'FluentWait', 'Awaitility', 'generic helper', 'higher order function']),
]

INFO = {'title': 'Behaviour you can pass around', 'panels': [
    panel([['e', '📝'], ['t', 'new Comparator<>() { ... }', {'b': 1, 'size': 11}]], 'Before Java 8', 'Six lines to say one thing.', 'An anonymous class for every small piece of behaviour.'),
    panel([['e', '➡️'], ['t', '(a, b) -> a.length() - b.length()', {'b': 1, 'size': 10}]], 'A lambda', 'Inputs, arrow, result.', 'The compiler fills in the types from the target.'),
    panel([['e', '🔗'], ['t', 'String::length', {'b': 1}]], 'Method reference', 'Name the method, done.', 'Static, bound, unbound or constructor.'),
    panel([['e', '🧩'], ['t', 'failed.or(slow)', {'b': 1}]], 'Compose', 'Small pieces join up.', 'and, or, andThen, thenComparing.')],
    'remember': 'A lambda is an object of a functional interface, one abstract method, created with the lambda body as that method. It can read effectively final variables, and it runs through invokedynamic.'}

REAL = [
    ['🛵', 'A food delivery app', 'Sorts restaurants with Comparator.comparing(Restaurant::rating).reversed().thenComparing(Restaurant::distance). Changing the sort order is a one word change.'],
    ['🧪', 'A Selenium framework', 'Waits with wait.until(d -> cart.count() == 2). The wait loop is written once, and every test passes its own condition as a lambda.'],
    ['🏦', 'A bank batch job', 'Keeps validation rules as a List of Predicate objects loaded from configuration, so a new rule is added without touching the loop that applies them.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to lambdas. A lambda is a small piece of behaviour you can pass to another method, written as inputs, an arrow and a result.',
        'Lambdas में आपका स्वागत है। Lambda व्यवहार का एक छोटा टुकड़ा है जिसे आप किसी दूसरे method को दे सकते हैं, इसे inputs, एक तीर और result के रूप में लिखा जाता है।',
        'Lambdas ಗೆ ಸ್ವಾಗತ. Lambda ಎಂದರೆ ಇನ್ನೊಂದು method ಗೆ ಕೊಡಬಹುದಾದ ಸಣ್ಣ ನಡವಳಿಕೆ, inputs, ಬಾಣ ಮತ್ತು result ಆಗಿ ಬರೆಯಲಾಗುತ್ತದೆ.',
        'Lambdas କୁ ସ୍ୱାଗତ। Lambda ହେଉଛି ଏକ ଛୋଟ ବ୍ୟବହାର ଯାହା ଅନ୍ୟ method କୁ ଦିଆଯାଇପାରେ, inputs, ତୀର ଏବଂ result ଭାବେ ଲେଖାଯାଏ।',
        'مرحبًا بك في تعبيرات لامدا. لامدا جزء صغير من السلوك تمرره إلى دالة أخرى، ويُكتب كمدخلات ثم سهم ثم نتيجة.',
        'Willkommen bei Lambdas. Ein Lambda ist ein kleines Stück Verhalten, das du an eine andere Methode übergibst, geschrieben als Eingaben, Pfeil und Ergebnis.'),
    say('why', 'Why lambdas', 'Before Java 8 every small piece of behaviour needed an anonymous class. A lambda keeps only the part that matters.',
        'Java 8 से पहले हर छोटे व्यवहार के लिए anonymous class चाहिए थी। Lambda सिर्फ़ ज़रूरी हिस्सा रखता है।',
        'Java 8 ಮೊದಲು ಪ್ರತಿಯೊಂದು ಸಣ್ಣ ನಡವಳಿಕೆಗೆ anonymous class ಬೇಕಿತ್ತು. Lambda ಮುಖ್ಯ ಭಾಗವನ್ನು ಮಾತ್ರ ಇಡುತ್ತದೆ.',
        'Java 8 ପୂର୍ବରୁ ପ୍ରତ୍ୟେକ ଛୋଟ ବ୍ୟବହାର ପାଇଁ anonymous class ଦରକାର ହେଉଥିଲା। Lambda କେବଳ ଜରୁରୀ ଅଂଶ ରଖେ।',
        'قبل Java 8 كان كل سلوك صغير يحتاج صنفًا مجهولًا كاملًا. أما لامدا فتحتفظ بالجزء المهم فقط.',
        'Vor Java 8 brauchte jedes kleine Verhalten eine anonyme Klasse. Ein Lambda behält nur das Wesentliche.'),
    say('syntax', 'Syntax', 'A lambda is parameters, an arrow and a body. Its type comes from where it is used, called the target type.',
        'Lambda में parameters, एक तीर और body होती है। इसका type वहाँ से आता है जहाँ इसे इस्तेमाल किया जाता है, इसे target type कहते हैं।',
        'Lambda ಎಂದರೆ parameters, ಬಾಣ ಮತ್ತು body. ಅದರ type ಬಳಸುವ ಸ್ಥಳದಿಂದ ಬರುತ್ತದೆ, ಅದನ್ನು target type ಎನ್ನುತ್ತಾರೆ.',
        'Lambda ରେ parameters, ତୀର ଏବଂ body ଥାଏ। ଏହାର type ବ୍ୟବହାର ସ୍ଥାନରୁ ଆସେ, ଯାହାକୁ target type କୁହାଯାଏ।',
        'لامدا هي معاملات ثم سهم ثم جسم. ويأتي نوعها من مكان استخدامها، ويسمى النوع الهدف.',
        'Ein Lambda besteht aus Parametern, Pfeil und Rumpf. Sein Typ kommt vom Verwendungsort, dem Zieltyp.'),
    say('functional', 'Functional interfaces', 'A functional interface has exactly one abstract method. Predicate tests, Function maps, Consumer uses and Supplier creates.',
        'Functional interface में ठीक एक abstract method होता है। Predicate जाँचता है, Function बदलता है, Consumer इस्तेमाल करता है और Supplier बनाता है।',
        'Functional interface ನಲ್ಲಿ ಒಂದೇ abstract method ಇರುತ್ತದೆ. Predicate ಪರೀಕ್ಷಿಸುತ್ತದೆ, Function ಬದಲಿಸುತ್ತದೆ, Consumer ಬಳಸುತ್ತದೆ, Supplier ರಚಿಸುತ್ತದೆ.',
        'Functional interface ରେ ଠିକ୍ ଗୋଟିଏ abstract method ଥାଏ। Predicate ଯାଞ୍ଚ କରେ, Function ବଦଳାଏ, Consumer ବ୍ୟବହାର କରେ, Supplier ତିଆରି କରେ।',
        'الواجهة الوظيفية لها دالة مجردة واحدة فقط. Predicate يختبر، وFunction يحوّل، وConsumer يستخدم، وSupplier ينشئ.',
        'Ein funktionales Interface hat genau eine abstrakte Methode. Predicate prüft, Function wandelt um, Consumer verbraucht, Supplier erzeugt.'),
    say('method-refs', 'Method references', 'When a lambda only calls one method, a method reference with two colons says the same thing, for example String colon colon length.',
        'जब lambda सिर्फ़ एक method बुलाता है, तो दो colon वाला method reference वही बात कहता है, जैसे String colon colon length।',
        'Lambda ಒಂದೇ method ಕರೆಯುವಾಗ, ಎರಡು colon ಇರುವ method reference ಅದೇ ಹೇಳುತ್ತದೆ, ಉದಾಹರಣೆ String colon colon length.',
        'ଯେତେବେଳେ lambda କେବଳ ଗୋଟିଏ method ଡାକେ, ଦୁଇ colon ଥିବା method reference ସେହି କଥା କହେ, ଯେପରି String colon colon length।',
        'عندما تستدعي لامدا دالة واحدة فقط، يقول مرجع الدالة بنقطتين مزدوجتين الشيء نفسه، مثل String::length.',
        'Ruft ein Lambda nur eine Methode auf, sagt eine Methodenreferenz mit zwei Doppelpunkten dasselbe, etwa String::length.'),
    say('compose', 'Composing', 'Predicates join with and, or and negate. Functions join with andThen. Comparators chain with comparing and thenComparing.',
        'Predicates and, or और negate से जुड़ते हैं। Functions andThen से जुड़ते हैं। Comparators comparing और thenComparing से जुड़ते हैं।',
        'Predicates and, or, negate ಮೂಲಕ ಸೇರುತ್ತವೆ. Functions andThen ಮೂಲಕ. Comparators comparing ಮತ್ತು thenComparing ಮೂಲಕ.',
        'Predicates and, or ଓ negate ଦ୍ୱାରା ଯୋଡ଼ନ୍ତି। Functions andThen ଦ୍ୱାରା। Comparators comparing ଓ thenComparing ଦ୍ୱାରା।',
        'تتحد المحمولات بـ and وor وnegate، والدوال بـ andThen، والمقارنات بـ comparing وthenComparing.',
        'Predicates verbinden sich mit and, or und negate, Functions mit andThen, Comparators mit comparing und thenComparing.'),
    say('capture', 'Capturing', 'A lambda can read local variables only if they are effectively final. Inside a lambda, this means the surrounding object.',
        'Lambda local variables तभी पढ़ सकता है जब वे effectively final हों। Lambda के अंदर this का मतलब बाहर वाला object है।',
        'Lambda local variables ಅನ್ನು effectively final ಆಗಿದ್ದರೆ ಮಾತ್ರ ಓದಬಹುದು. Lambda ಒಳಗೆ this ಎಂದರೆ ಹೊರಗಿನ object.',
        'Lambda local variables କେବଳ effectively final ହେଲେ ପଢ଼ିପାରେ। Lambda ଭିତରେ this ର ଅର୍ଥ ବାହାର object।',
        'تقرأ لامدا المتغيرات المحلية فقط إذا كانت نهائية فعليًا. وداخل لامدا تعني this الكائن المحيط.',
        'Ein Lambda liest lokale Variablen nur, wenn sie effektiv final sind. Im Lambda bedeutet this das umgebende Objekt.'),
    say('exceptions', 'Checked exceptions', 'Function and Consumer cannot throw checked exceptions, so wrap the call and rethrow it as an unchecked exception with the cause.',
        'Function और Consumer checked exceptions नहीं फेंक सकते, इसलिए call को wrap करके cause के साथ unchecked exception फेंकिए।',
        'Function ಮತ್ತು Consumer checked exceptions ಎಸೆಯಲಾರವು, ಆದ್ದರಿಂದ call ಅನ್ನು wrap ಮಾಡಿ cause ಜೊತೆ unchecked ಆಗಿ ಎಸೆಯಿರಿ.',
        'Function ଓ Consumer checked exceptions ଫିଙ୍ଗିପାରନ୍ତି ନାହିଁ, ତେଣୁ call କୁ wrap କରି cause ସହ unchecked ଭାବେ ଫିଙ୍ଗନ୍ତୁ।',
        'لا تستطيع Function وConsumer رمي الاستثناءات المفحوصة، لذا غلّف الاستدعاء وأعد رميه كاستثناء غير مفحوص مع السبب.',
        'Function und Consumer dürfen keine geprüften Ausnahmen werfen, also umhülle den Aufruf und wirf eine ungeprüfte Ausnahme mit Ursache.'),
    say('inside', 'Inside the JVM', 'javac turns the lambda body into a private method and writes one invokedynamic instruction. On first use, LambdaMetafactory builds the object.',
        'javac lambda body को private method बनाता है और एक invokedynamic instruction लिखता है। पहली बार LambdaMetafactory object बनाता है।',
        'javac lambda body ಅನ್ನು private method ಮಾಡಿ ಒಂದು invokedynamic instruction ಬರೆಯುತ್ತದೆ. ಮೊದಲ ಬಳಕೆಯಲ್ಲಿ LambdaMetafactory object ರಚಿಸುತ್ತದೆ.',
        'javac lambda body କୁ private method କରେ ଏବଂ ଗୋଟିଏ invokedynamic instruction ଲେଖେ। ପ୍ରଥମ ଥର LambdaMetafactory object ତିଆରି କରେ।',
        'يحول javac جسم لامدا إلى دالة خاصة ويكتب تعليمة invokedynamic واحدة، وعند أول استخدام يبني LambdaMetafactory الكائن.',
        'javac macht aus dem Rumpf eine private Methode und schreibt eine invokedynamic-Anweisung. Beim ersten Aufruf baut die LambdaMetafactory das Objekt.'),
    say('scenario', 'Scenario', 'A retry helper takes the work as a Supplier and the meaning of success as a Predicate, so one helper retries any flaky call.',
        'Retry helper काम को Supplier और सफलता के अर्थ को Predicate के रूप में लेता है, इसलिए एक ही helper किसी भी flaky call को दोबारा चलाता है।',
        'Retry helper ಕೆಲಸವನ್ನು Supplier ಆಗಿ ಮತ್ತು ಯಶಸ್ಸನ್ನು Predicate ಆಗಿ ಪಡೆಯುತ್ತದೆ, ಆದ್ದರಿಂದ ಒಂದೇ helper ಯಾವುದೇ flaky call ಮರುಪ್ರಯತ್ನಿಸುತ್ತದೆ.',
        'Retry helper କାମକୁ Supplier ଏବଂ ସଫଳତାକୁ Predicate ଭାବେ ନିଏ, ତେଣୁ ଗୋଟିଏ helper ଯେକୌଣସି flaky call ପୁଣି ଚଲାଏ।',
        'يأخذ مساعد إعادة المحاولة العمل كـ Supplier ومعنى النجاح كـ Predicate، فيعيد مساعد واحد أي استدعاء غير مستقر.',
        'Ein Retry-Helfer nimmt die Arbeit als Supplier und den Erfolg als Predicate, so wiederholt ein Helfer jeden wackligen Aufruf.'),
]

QUIZ = [
    quiz('e', 'What makes an interface a functional interface?', ['Exactly one abstract method', 'The @FunctionalInterface annotation', 'Only static methods', 'No methods at all'], 0, 'Count the abstract ones.', 'The annotation is optional. It only asks the compiler to check the rule.'),
    quiz('e', 'Which interface fits a lambda that takes nothing and returns a value?', ['Supplier', 'Consumer', 'Predicate', 'Function'], 0, 'It supplies.', 'Supplier&lt;T&gt; has T get().'),
    quiz('e', 'What does this print?', ['6', 'BRAINY', 'true', 'Compile error'], 0, 'Function from String to Integer.', 'apply calls s.length() on "Brainy", which has 6 letters.',
         code='Function<String, Integer> len = s -> s.length();\nSystem.out.println(len.apply("Brainy"));', run=True),
    quiz('m', 'What does this print?', ['[cart, login]', '[login, cart]', '[cart]', '[login]'], 0, 'Keep words shorter than 6, then sort.', 'checkout and search have 6 or more letters, so cart and login remain, and natural order puts cart first.',
         code='List<String> t = new ArrayList<>(List.of("login", "checkout", "cart", "search"));\nt.removeIf(s -> s.length() >= 6);\nt.sort(Comparator.naturalOrder());\nSystem.out.println(t);', run=True),
    quiz('m', 'Which method reference is the same as <code>s -&gt; s.toUpperCase()</code>?', ['String::toUpperCase', 's::toUpperCase', 'String.toUpperCase', 'toUpperCase::String'], 0, 'ClassName::method for the incoming object.', 'It is an unbound instance method reference. The incoming String becomes the object the method runs on.'),
    quiz('m', 'Why does <code>int n = 0; Runnable r = () -&gt; n++;</code> not compile?', ['Lambdas can only use effectively final local variables', 'Runnable cannot have a body', 'n must be static', 'Lambdas cannot use int'], 0, 'Captured values are copies.', 'Changing n would make the copy inside the lambda wrong, so Java forbids it.'),
    quiz('m', 'What does this print?', ['true false', 'false true', 'true true', 'false false'], 0, 'Combine the two checks.', '15 is above 10 and odd, so the first is true. 12 is above 10 but even, so the second is false.',
         code='Predicate<Integer> big = n -> n > 10;\nPredicate<Integer> odd = n -> n % 2 == 1;\nSystem.out.println(big.and(odd).test(15) + " " + big.and(odd).test(12));', run=True),
    quiz('h', 'What does this print?', ['12', '7', '16', '9'], 0, 'andThen runs the second function after the first.', '(5 + 1) is 6, then 6 × 2 is 12. With compose the order would flip, giving 5 × 2 + 1 = 11.',
         code='Function<Integer, Integer> plus1 = x -> x + 1;\nFunction<Integer, Integer> times2 = x -> x * 2;\nSystem.out.println(plus1.andThen(times2).apply(5));', run=True),
    quiz('h', 'Inside a lambda written in an instance method, what does <code>this</code> refer to?', ['The object whose method contains the lambda', 'The lambda object', 'The functional interface', 'Nothing, this is not allowed'], 0, 'Lambdas do not add a scope for this.', 'An anonymous class would make this refer to the anonymous object instead.'),
    quiz('h', 'How many .class files does javac write for a class with three lambdas and no other nested classes?', ['1', '3', '4', '0'], 0, 'Lambdas use invokedynamic.', 'Lambda bodies become private methods of the same class. Classes for them are made in memory at run time.'),
    quiz('x', 'What does this print?', ['[cart, login, search]', '[search, login, cart]', '[login, cart, search]', '[cart, search, login]'], 0, 'Shortest first, then alphabetical for ties.', 'cart has 4 letters. login and search are 5 and 6. So the order is by length.',
         code='List<String> t = new ArrayList<>(List.of("search", "login", "cart"));\nt.sort(Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()));\nSystem.out.println(t);', run=True),
    quiz('x', 'Which of these does not compile?', ['<code>Object o = () -&gt; 1;</code>', '<code>Supplier&lt;Integer&gt; s = () -&gt; 1;</code>', '<code>Callable&lt;Integer&gt; c = () -&gt; 1;</code>', '<code>IntSupplier i = () -&gt; 1;</code>'], 0, 'A lambda needs a functional interface as its target.', 'Object is a class, not a functional interface, so the compiler has nothing to turn the lambda into. A cast such as (Supplier&lt;Integer&gt;) would fix it.'),
]

CALC = [
    calc('e', 'What does this print?', '12', 'Apply the operator.', ['<span class="eq">(3 + 1) × 3 = 12</span>'], code='BinaryOperator<Integer> f = (a, b) -> (a + 1) * b;\nSystem.out.println(f.apply(3, 3));', run=True),
    calc('e', 'How many names does the filter keep?', '2', 'Starts with "a".', ['asha and arun start with a.', 'So 2 are kept.'], code='System.out.println(List.of("asha", "ravi", "arun", "meera").stream().filter(s -> s.startsWith("a")).count());', run=True),
    calc('m', 'What does this print?', '22', 'andThen: first add 1, then times 2.', ['<span class="eq">10 + 1 = 11</span>', '<span class="eq">11 × 2 = 22</span>'], code='Function<Integer, Integer> f = x -> x + 1;\nSystem.out.println(f.andThen(x -> x * 2).apply(10));', run=True),
    calc('m', 'What does this print?', '21', 'compose runs the argument function first.', ['compose(x -> x * 2) runs first: <span class="eq">10 × 2 = 20</span>', 'then x + 1: <span class="eq">20 + 1 = 21</span>'], code='Function<Integer, Integer> f = x -> x + 1;\nSystem.out.println(f.compose((Integer x) -> x * 2).apply(10));', run=True),
    calc('m', 'A discount lambda takes 10 percent off, then a coupon takes 50 off. What is the final price of 1000?', '850.0', 'Percent first.', ['<span class="eq">1000 − 1000 × 10 ÷ 100 = 900</span>', '<span class="eq">900 − 50 = 850.0</span>']),
    calc('h', 'What does this print?', '10', 'Sum 0 to 4 into the array slot.', ['<span class="eq">0 + 1 + 2 + 3 + 4 = 10</span>'], code='int[] box = {0};\nIntStream.range(0, 5).forEach(i -> box[0] += i);\nSystem.out.println(box[0]);', run=True),
    calc('h', 'The retry helper succeeds on attempt 3 of at most 5, and each attempt waits 200 ms before the next. How many ms are spent waiting?', '400', 'Waits happen between attempts.', ['Attempts 1 and 2 fail, so there are 2 waits.', '<span class="eq">2 × 200 = 400</span>']),
    calc('x', 'What does this print?', '3', 'Count results that failed or were slow.', ['checkout failed, search was slow, cart failed.', 'login passed and was fast.', 'So 3.'],
         code='record R(String s, int ms) {}\nPredicate<R> failed = r -> r.s().equals("FAIL");\nPredicate<R> slow = r -> r.ms() > 1000;\nvar rs = List.of(new R("PASS", 420), new R("FAIL", 2300), new R("PASS", 1800), new R("FAIL", 300));\nSystem.out.println(rs.stream().filter(failed.or(slow)).count());', run=True),
]

T = {
    'slug': 'java-lambdas', 'title': 'Lambdas, functional interfaces and method references', 'short': 'Lambdas', 'emoji': '➡️', 'module': MODULE, 'minutes': 22,
    'lead': 'Lambdas let you hand a small piece of behaviour to another method: how to compare, what to keep, what to do with each item. This chapter goes from your first arrow to functional interfaces, method references, composing functions, captured variables, checked exceptions and the invokedynamic machinery the JVM uses to run them.',
    'desc': 'Java lambdas from zero to expert: lambda syntax, target types, functional interfaces, java.util.function, method references, composing Predicate, Function and Comparator, effectively final capture, checked exceptions, invokedynamic and LambdaMetafactory.',
    'summary': 'Why lambdas replaced anonymous classes, lambda syntax and target typing, functional interfaces and java.util.function, your own @FunctionalInterface, the four kinds of method reference, composing predicates, functions and comparators, effectively final capture and this, checked exceptions in lambdas, how invokedynamic runs a lambda, and a retry helper for flaky tests.',
    'keywords': ['lambda', 'functional interface', 'method reference', 'Predicate', 'Function', 'Consumer', 'Supplier', 'Comparator', 'effectively final', 'invokedynamic', 'Java 8'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
