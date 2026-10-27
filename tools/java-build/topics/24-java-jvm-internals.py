# Chapter 24: how a Java program runs inside the JVM: the class file, class loading, runtime memory areas, bytecode and the
# operand stack, the JIT compiler, garbage collectors, JDK Flight Recorder, the AOT cache and compact object headers.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

HELLO = '''
class Main {
    public static void main(String[] args) {
        System.out.println("Hello from bytecode");
    }
}
'''

SQUARE = '''
class Main {
    static int square(int x) {
        return x * x;
    }

    public static void main(String[] args) {
        long sum = 0;
        for (int i = 0; i < 200_000; i++) {
            sum += square(i % 1000);
        }
        System.out.println(sum);
    }
}
'''

POINTS = '''
class Main {
    record Point(int x, int y) {}

    public static void main(String[] args) {
        Runtime rt = Runtime.getRuntime();
        System.gc();
        long before = rt.totalMemory() - rt.freeMemory();
        Object[] points = new Object[2_000_000];
        for (int i = 0; i < points.length; i++) points[i] = new Point(i, i);
        System.gc();
        long after = rt.totalMemory() - rt.freeMemory();
        // each array slot is a 4 byte compressed reference, so take those away
        long perPoint = Math.round((after - before - 4.0 * points.length) / points.length);
        System.out.println("bytes per Point object: about " + perPoint);
    }
}
'''

CODES = {
    'classfile': sh({'Main.java': HELLO},
        'javac Main.java && echo "--- first 8 bytes of Main.class ---" && od -A d -t x1 -N 8 Main.class && echo "--- the version javap reads ---" && javap -v Main | grep -E "major|minor" && java Main',
        'Every class file starts with CAFEBABE',
        shown='$ javac Main.java\n$ od -A d -t x1 -N 8 Main.class     # dump the first 8 bytes in hex\n$ javap -v Main | grep -E "major|minor"\n$ java Main'),
    'lazy': j('''
class Main {
    static class Config {
        static final String URL;
        static {
            System.out.println("Config is being initialised");
            URL = "https://shop.test";
        }
    }

    static class Unused {
        static { System.out.println("Unused is initialised"); }
    }

    public static void main(String[] args) {
        System.out.println("main starts");
        Unused[] none = new Unused[3];
        System.out.println("an array of Unused does not initialise Unused");
        System.out.println("first use: " + Config.URL);
        System.out.println("second use: " + Config.URL);
    }
}
''', 'Classes are initialised lazily, once, on first real use'),
    'loaders': j('''
class Main {
    static String who(Class<?> c) {
        ClassLoader l = c.getClassLoader();
        return c.getSimpleName() + " -> " + (l == null ? "bootstrap" : l.getName());
    }

    public static void main(String[] args) throws Exception {
        System.out.println(who(String.class));
        System.out.println(who(java.sql.Connection.class));
        System.out.println(who(Main.class));
        System.out.println("parent of app: " + Main.class.getClassLoader().getParent().getName());

        try {
            Class.forName("com.shop.Ghost");
        } catch (ClassNotFoundException e) {
            System.out.println("ClassNotFoundException: " + e.getMessage());
        }
    }
}
''', 'Which loader loaded each class', trace=False),
    'frames': j('''
class Main {
    static int price(int qty) {
        int base = qty * 50;
        return withTax(base);
    }

    static int withTax(int amount) {
        int tax = amount / 10;
        return amount + tax;
    }

    public static void main(String[] args) {
        int total = price(3);
        System.out.println("total " + total);
    }
}
''', 'Each method call gets its own stack frame'),
    'overflow': j('''
class Main {
    static int depth = 0;

    static void dig() {
        depth++;
        dig();                 // no exit condition, every call adds a frame
    }

    public static void main(String[] args) {
        try {
            dig();
        } catch (StackOverflowError e) {
            System.out.println("StackOverflowError after more than 1000 frames: " + (depth > 1000));
        }
        System.out.println("the heap and the program are fine, only that thread's stack was full");
    }
}
''', 'StackOverflowError: one thread runs out of stack', trace=False),
    'bytecode': sh({'Main.java': SQUARE},
        'javac Main.java && javap -c Main | sed -n "/static int square/,/ireturn/p"',
        'The bytecode of square',
        shown='$ javac Main.java\n$ javap -c Main     # only the square method is shown here'),
    'jit': sh({'Main.java': SQUARE},
        'javac Main.java && java -XX:+PrintCompilation Main | grep -E "Main::square|^[0-9]+$" | awk \'NF==1 {print "program printed " $1; next} {t=$3; sub(/^[^:]*::/, "", $4); m=""; if ($0 ~ /not entrant/) m="  (old version thrown away)"; print "tier " t ": Main::" $4 m}\'',
        'Watching the JIT compile square',
        shown='$ javac Main.java\n$ java -XX:+PrintCompilation Main | grep Main::square     # tidied with awk'),
    'gc25': sh({'Main.java': HELLO},
        'javac Main.java && java -XX:ActiveProcessorCount=1 -Xmx512m -Xlog:gc Main | head -1 && java -Xlog:gc Main | head -1',
        'Java 25 picks a collector from the machine size',
        shown='$ java -XX:ActiveProcessorCount=1 -Xmx512m -Xlog:gc Main     # pretend to be a tiny container\n$ java -Xlog:gc Main', replace=[(r'^\[[0-9.]+s\]', '[0.004s]')]),
    'gc27': sh({'Main.java': HELLO},
        'javac Main.java && java -XX:ActiveProcessorCount=1 -Xmx512m -Xlog:gc Main | head -1',
        'Java 27 uses G1 on the same tiny machine (JEP 523)', jdk=27,
        shown='$ java -XX:ActiveProcessorCount=1 -Xmx512m -Xlog:gc Main', replace=[(r'^\[[0-9.]+s\]', '[0.004s]')]),
    'headers': sh({'Main.java': POINTS},
        'javac Main.java && echo "Java 27 default (compact headers on):" && java -Xmx1g Main && echo "-XX:-UseCompactObjectHeaders (the old 12 byte header):" && java -Xmx1g -XX:-UseCompactObjectHeaders Main',
        'Compact object headers make small objects smaller', jdk=27,
        shown='$ java -Xmx1g Main\n$ java -Xmx1g -XX:-UseCompactObjectHeaders Main'),
    'jfr': sh({'Main.java': '''
import jdk.jfr.*;

class Main {
    @Name("shop.Checkout") @Label("Checkout")
    static class CheckoutEvent extends Event {     // your own event type
        @Label("Order") String order;
        @Label("Items") int items;
    }

    public static void main(String[] args) throws Exception {
        for (int i = 1; i <= 3; i++) {
            CheckoutEvent e = new CheckoutEvent();
            e.begin();
            Thread.sleep(20 * i);                  // pretend to call the payment service
            e.order = "ORD-" + i;
            e.items = i;
            e.commit();
        }
        System.out.println("3 checkouts done");
    }
}
'''},
        'javac Main.java && java -Ddb.password=hunter2 -Dshop.region=eu -XX:StartFlightRecording:filename=rec.jfr Main | grep -v "jfr,startup" && echo "--- one Checkout event ---" && jfr print --events shop.Checkout rec.jfr | sed -n "1,6p" && echo "--- system properties stored in the recording ---" && jfr print --events jdk.InitialSystemProperty rec.jfr | grep -A1 -E "key = .(db.password|shop.region)"',
        'Recording a custom event with JDK Flight Recorder', jdk=27,
        shown='$ java -Ddb.password=hunter2 -Dshop.region=eu -XX:StartFlightRecording:filename=rec.jfr Main\n$ jfr print --events shop.Checkout rec.jfr\n$ jfr print --events jdk.InitialSystemProperty rec.jfr',
        replace=[(r'startTime = .*', 'startTime = 10:15:02.181 (2026-10-24)'), (r'duration = [0-9.]+ ms', 'duration = 22 ms')]),
    'aot': sh({'Main.java': '''
import java.net.URI;
import java.net.http.HttpRequest;
import java.time.Duration;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        var req = HttpRequest.newBuilder(URI.create("https://shop.test/api")).GET().build();
        var words = Stream.of("pay", "cart", "login").sorted().collect(Collectors.joining(","));
        System.out.println(req.method() + " " + words + " " + Duration.ofSeconds(90));
    }
}
'''},
        'javac Main.java && jar cf app.jar Main.class && echo "--- 1. training run writes the cache ---" && java -XX:AOTCacheOutput=app.aot -cp app.jar Main 2>&1 | grep -E "^GET|creation is complete" && echo "--- 2. classes loaded the slow way, without and with the cache ---" && java -Xlog:class+load -cp app.jar Main | grep -vc "shared objects file" && java -XX:AOTCache=app.aot -Xlog:class+load -cp app.jar Main | grep -vc "shared objects file"',
        'An AOT cache in two commands (Java 25)',
        shown='$ jar cf app.jar Main.class     # the cache works with classes from JAR files\n$ java -XX:AOTCacheOutput=app.aot -cp app.jar Main     # training run\n$ java -Xlog:class+load -cp app.jar Main | grep -vc "shared objects file"\n$ java -XX:AOTCache=app.aot -Xlog:class+load -cp app.jar Main | grep -vc "shared objects file"',
        replace=[(r'app\.aot \d+ bytes', 'app.aot (about 10 MB)')]),
    'inspect': j('''
import java.lang.management.*;

class Main {
    public static void main(String[] args) {
        RuntimeMXBean rt = ManagementFactory.getRuntimeMXBean();
        System.out.println("JVM: " + rt.getVmName() + " " + Runtime.version().feature());
        System.out.println("CPUs the JVM can use: " + Runtime.getRuntime().availableProcessors());
        for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
            System.out.println("collector: " + gc.getName());
        }
    }
}
''', 'A health check that reports how the JVM was started', trace=False, args=None, more=None),
}

DG = {
    'journey': {'t': 'From Main.java to running machine code', 'w': 900, 'h': 330, 'mw': 640,
        'g': [[20, 20, 250, 290, 'Your computer, at build time', 1], [300, 20, 580, 290, 'Inside the JVM, at run time', 2]],
        'n': [['src', 60, 50, 170, 50, 'Main.java', {'c': 1, 'sub': 'source code'}],
              ['javac', 60, 140, 170, 50, 'javac', {'c': 3, 'sub': 'checks and compiles'}],
              ['cls', 60, 230, 170, 50, 'Main.class', {'c': 1, 'sub': 'bytecode, CAFEBABE'}],
              ['load', 330, 50, 160, 50, 'Class loader', {'c': 2, 'sub': 'finds and reads'}],
              ['ver', 330, 140, 160, 50, 'Verifier', {'c': 2, 'sub': 'is it safe'}],
              ['int', 520, 50, 160, 50, 'Interpreter', {'c': 4, 'sub': 'one bytecode at a time'}],
              ['jit', 520, 140, 160, 50, 'JIT compiler', {'c': 5, 'sub': 'C1 then C2'}],
              ['mc', 710, 95, 150, 50, 'Machine code', {'c': 4, 'sub': 'runs on the CPU'}],
              ['gc', 520, 235, 340, 50, 'Garbage collector', {'c': 3, 'sub': 'frees objects nobody can reach'}]],
        'e': [['src', 'javac', {'id': 'e1'}], ['javac', 'cls', {'id': 'e2'}], ['cls', 'load', {'t': 'java Main', 'id': 'e3'}], ['load', 'ver', {'id': 'e4'}],
              ['ver', 'int', {'id': 'e5'}], ['int', 'jit', {'t': 'hot', 'id': 'e6'}], ['int', 'mc', {'id': 'e7'}], ['jit', 'mc', {'id': 'e8'}]],
        'st': [[['src', 'javac', 'cls', 'e1', 'e2'], 'Build time: javac checks your code and writes bytecode into Main.class. Bytecode is the same on Windows, Linux and macOS.'],
               [['cls', 'load', 'e3'], 'Run time starts with java Main. The application class loader finds Main.class and reads its bytes.'],
               [['load', 'ver', 'e4'], 'The verifier checks the bytecode cannot break the JVM, for example by jumping outside a method or mixing up types.'],
               [['ver', 'int', 'e5', 'int', 'e7', 'mc'], 'The interpreter starts at once. It reads one bytecode instruction at a time and does what it says. Starting is quick, running is slow.'],
               [['int', 'jit', 'e6', 'e8', 'mc'], 'The JVM counts calls and loops. Hot methods are compiled to real machine code by the JIT compiler, first quickly (C1), then very well (C2).'],
               [['gc'], 'All the while the garbage collector reclaims objects that nothing points to any more, so you never call free yourself.']]},
    'areas': {'t': 'The runtime memory areas while price(3) runs', 'w': 900, 'h': 330, 'mw': 640,
        'g': [[20, 20, 280, 290, 'Stack of the main thread', 1], [330, 20, 270, 290, 'Heap (shared by all threads)', 2], [630, 20, 250, 290, 'Metaspace (class data)', 3]],
        'n': [['fm', 40, 230, 240, 56, 'main()', {'c': 1, 'sub': 'args, total'}],
              ['fp', 40, 150, 240, 56, 'price(3)', {'c': 1, 'sub': 'qty = 3, base = 150'}],
              ['ft', 40, 70, 240, 56, 'withTax(150)', {'c': 1, 'sub': 'amount = 150, tax = 15'}],
              ['arr', 350, 70, 230, 56, 'String[] args', {'c': 2, 'sub': 'an empty array object'}],
              ['str', 350, 230, 230, 56, '"total 165"', {'c': 2, 'sub': 'a String object, later'}],
              ['meta', 650, 70, 210, 70, 'class Main', {'c': 3, 'sub': 'methods, bytecode, constant pool'}],
              ['code', 650, 190, 210, 70, 'Code cache', {'c': 4, 'sub': 'machine code from the JIT'}]],
        'e': [['fm', 'arr', {'t': 'reference', 'id': 'r1'}], ['fm', 'str', {'t': 'reference', 'id': 'r2', 'd': 1}]],
        'st': [[['fm', 'arr', 'r1', 'meta'], 'main starts. Its frame holds the local variables. args points to an array object that lives on the heap. The class itself lives in metaspace.'],
               [['fp'], 'Calling price(3) pushes a new frame on top with its own qty and base. Each thread has its own stack, so locals are never shared.'],
               [['ft'], 'withTax pushes a third frame. If calls go too deep, the stack fills and the thread gets a StackOverflowError.'],
               [['ft', 'fp'], 'withTax returns 165, and its frame is popped. Popping a frame is instant, which is why local variables cost nothing to clean up.'],
               [['fm', 'str', 'r2'], 'Back in main, "total " + total builds a String object on the heap. When nothing refers to it any more, the garbage collector may reclaim it.'],
               [['code'], 'If price became hot, its machine code would be stored in the code cache, another area outside the heap.']]},
    'opstack': {'t': 'How square(7) runs on the operand stack', 'w': 900, 'h': 270, 'mw': 640,
        'g': [[20, 20, 400, 230, 'Bytecode', 1], [460, 20, 420, 230, 'The frame of square', 2]],
        'n': [['b0', 40, 50, 170, 40, '0: iload_0', {'c': 1}], ['b1', 230, 50, 170, 40, '1: iload_0', {'c': 1}],
              ['b2', 40, 130, 170, 40, '2: imul', {'c': 1}], ['b3', 230, 130, 170, 40, '3: ireturn', {'c': 1}],
              ['loc', 690, 162, 170, 56, 'local 0 (x)', {'c': 3, 'sub': '7'}],
              ['s1', 480, 170, 170, 40, 'stack: 7', {'c': 2}], ['s2', 480, 110, 170, 40, 'stack: 7, 7', {'c': 2}],
              ['s3', 480, 50, 170, 40, 'stack: 49', {'c': 4}], ['ret', 690, 42, 170, 56, 'back to the caller', {'c': 5, 'sub': 'returns 49'}]],
        'e': [['loc', 's1', {'t': 'copy', 'id': 'c1'}], ['s3', 'ret', {'t': 'pop', 'id': 'c2', 'd': 1}]],
        'st': [[['loc'], 'The argument x = 7 sits in local variable slot 0 of the frame. The operand stack is empty.'],
               [['b0', 'loc', 's1', 'c1'], 'iload_0 copies local 0 onto the operand stack. The i means int.'],
               [['b1', 's2'], 'iload_0 again. Now the stack holds 7 and 7.'],
               [['b2', 's3'], 'imul pops two ints, multiplies them, and pushes the answer 49.'],
               [['b3', 'ret', 'c2'], 'ireturn pops 49 and hands it to the caller, whose frame continues. The JVM is a stack machine, so every instruction works this way.']]},
}

PARTS = [
    part('journey', '🧭', 'The journey of a Java program', '''
<p>The basics chapter showed the short version: javac makes bytecode and the JVM runs it. This chapter opens the JVM and looks at each stage, with real commands you can type. It is the knowledge that helps when a service starts slowly, eats memory, or crashes with an error that makes no sense.</p>
<div class="viz" data-viz="flow" data-k="journey"></div>
<div class="note">Think of a theatre script translated once into a common language (bytecode). Every theatre (JVM) in the world can read it, and an actor who repeats a scene many times learns it by heart (JIT) so it gets faster each night.</div>
''', kw=['JVM', 'how Java runs', 'bytecode', 'interpreter', 'JIT', 'class loader', 'verifier', 'execution engine', 'write once run anywhere']),
    part('classfile', '📄', 'Inside a class file', '''
<p>A <code>.class</code> file is a small binary file with a fixed layout: a magic number, a version, a <b>constant pool</b> (all the names and literal values the class uses), the fields, the methods with their bytecode, and some attributes. The first four bytes are always <code>CA FE BA BE</code>.</p>
[[classfile]]
<p>The next bytes hold the version. 0x45 is 69, which means Java 25. A Java 21 JVM refuses this file with <code>UnsupportedClassVersionError</code>, which is the error you see when a library was built with a newer JDK than the one in production. The fix is to run a newer JDK or build with <code>javac --release 21</code>.</p>
<div class="tw"><table class="jt"><tr><th>Java</th><th>Class file major version</th></tr>
<tr><td>8</td><td>52</td></tr><tr><td>11</td><td>55</td></tr><tr><td>17</td><td>61</td></tr><tr><td>21</td><td>65</td></tr><tr><td>25</td><td>69</td></tr><tr><td>27</td><td>71</td></tr></table></div>
''', kw=['class file', 'CAFEBABE', 'magic number', 'major version', 'constant pool', 'javap -v', 'UnsupportedClassVersionError', '--release']),
    part('loading', '🚚', 'Class loading: delegation and lazy initialisation', '''
<p>The JVM does not load every class at start. It loads a class the first time the code needs it. Three built in class loaders share the work, and each one asks its <b>parent</b> first. This rule, called <b>parent delegation</b>, is why nobody can sneak in a fake <code>java.lang.String</code>.</p>
<div class="viz" data-viz="jclassload"></div>
[[loaders]]
<p>Loading is followed by linking (verify, prepare, resolve) and then <b>initialisation</b>, when static fields get their values and static blocks run. Initialisation happens once, at the first real use, such as reading a static field or calling <code>new</code>. Step through the program to see exactly when it happens.</p>
[[lazy]]
<div class="tip">ClassNotFoundException means code asked for a class by name and no loader found it. NoClassDefFoundError means the class was there when the code was compiled but is missing or failed to initialise at run time. Both usually point to a missing JAR on the classpath.</div>
''', kw=['class loader', 'bootstrap', 'platform class loader', 'application class loader', 'parent delegation', 'static initialiser', 'lazy loading', 'ClassNotFoundException', 'NoClassDefFoundError', 'linking']),
    part('memory', '🗄️', 'The runtime memory areas', '''
<p>A running JVM divides its memory into areas with different jobs. Every <b>thread</b> has its own <b>stack</b> of frames, one frame per method call, holding that call's local variables. All <b>objects</b> live on the shared <b>heap</b>. Class data such as methods and the constant pool lives in <b>metaspace</b>, and JIT compiled machine code lives in the <b>code cache</b>.</p>
<div class="viz" data-viz="flow" data-k="areas"></div>
[[frames]]
<p>Each thread's stack has a limited size, about 1 MB by default on 64 bit Linux and changeable with <code>-Xss</code>. Deep or endless recursion fills it.</p>
[[overflow]]
<div class="tw"><table class="jt"><tr><th>Area</th><th>Holds</th><th>Error when full</th><th>Size flag</th></tr>
<tr><td>Stack (per thread)</td><td>frames, local variables</td><td>StackOverflowError</td><td><code>-Xss</code></td></tr>
<tr><td>Heap</td><td>all objects and arrays</td><td>OutOfMemoryError: Java heap space</td><td><code>-Xms</code> <code>-Xmx</code></td></tr>
<tr><td>Metaspace</td><td>classes and methods</td><td>OutOfMemoryError: Metaspace</td><td><code>-XX:MaxMetaspaceSize</code></td></tr>
<tr><td>Code cache</td><td>JIT machine code</td><td>a warning, then the JIT stops</td><td><code>-XX:ReservedCodeCacheSize</code></td></tr></table></div>
''', kw=['stack', 'heap', 'metaspace', 'code cache', 'stack frame', 'local variables', 'StackOverflowError', 'OutOfMemoryError', '-Xss', '-Xmx', 'PermGen']),
    part('bytecode', '🔢', 'Bytecode and the operand stack', '''
<p>Bytecode instructions are one byte long, plus any operands, which is where the name comes from. The JVM is a <b>stack machine</b>: instructions take their inputs from a small operand stack in the current frame and push their results back onto it. Here is the real bytecode of a method that squares a number.</p>
[[bytecode]]
<div class="viz" data-viz="flow" data-k="opstack"></div>
<p>The first letter of many instructions tells the type: <code>i</code> for int, <code>l</code> for long, <code>d</code> for double, <code>a</code> for a reference. Calls use <code>invokestatic</code>, <code>invokevirtual</code>, <code>invokeinterface</code>, <code>invokespecial</code> and, for lambdas and string concatenation, <code>invokedynamic</code>.</p>
''', kw=['bytecode', 'operand stack', 'stack machine', 'iload', 'imul', 'ireturn', 'invokevirtual', 'invokedynamic', 'javap -c', 'opcode']),
    part('jit', '🔥', 'The interpreter and the JIT compiler', '''
<p>HotSpot starts every method in the <b>interpreter</b>. It counts how often each method runs and how often each loop turns. When a method gets hot, the <b>C1</b> compiler turns it into machine code quickly (tier 2 or tier 3, the second one also collects a profile). If it stays hot, the <b>C2</b> compiler uses that profile to produce highly optimised code (tier 4), for example by inlining small methods into their callers.</p>
[[jit]]
<p>That is why the first requests to a fresh Java service are slower than later ones, and why performance tests always include a warm up phase. If the profile turns out to be wrong, for example a branch that was never taken suddenly runs, the JVM throws away the optimised code (deoptimisation) and goes back to the interpreter for a while.</p>
<div class="tip">Never measure Java speed with one run of a loop and System.currentTimeMillis. Use JMH, the Java Microbenchmark Harness, which handles warm up, dead code removal and statistics for you.</div>
''', kw=['JIT', 'just in time', 'HotSpot', 'C1', 'C2', 'tiered compilation', 'PrintCompilation', 'inlining', 'deoptimisation', 'warm up', 'JMH']),
    part('gc', '♻️', 'Garbage collectors and object headers', '''
<p>The garbage collection chapter explained when an object becomes garbage. The JVM ships several <b>collectors</b> that differ in how they clean up. Most objects die young, so the heap is split into a young and an old generation and the young part is cleaned often and cheaply.</p>
<div class="tw"><table class="jt"><tr><th>Collector</th><th>Best for</th><th>Flag</th></tr>
<tr><td>G1</td><td>the default: balanced pauses and throughput</td><td><code>-XX:+UseG1GC</code></td></tr>
<tr><td>ZGC</td><td>very short pauses (under a millisecond) on large heaps, generational only since Java 24</td><td><code>-XX:+UseZGC</code></td></tr>
<tr><td>Parallel</td><td>batch jobs that only care about throughput</td><td><code>-XX:+UseParallelGC</code></td></tr>
<tr><td>Serial</td><td>tiny heaps and single core tools</td><td><code>-XX:+UseSerialGC</code></td></tr></table></div>
<p>Up to Java 26 the JVM quietly picked Serial on a machine with one CPU or less than 1792 MB of memory, which surprised many teams running small containers. Java 27 (JEP 523) uses G1 everywhere.</p>
[[gc25]]
[[gc27]]
<p>Every object also starts with a <b>header</b> that the JVM uses for locking, hashing and garbage collection. It used to be 12 bytes. <b>Compact object headers</b> shrink it to 8 bytes. They became a supported option in Java 25 (JEP 519) and are on by default in Java 27 (JEP 534). For apps with millions of small objects this saves real memory.</p>
[[headers]]
<p>A Point with two ints needs 8 bytes of fields. With the old header that is 12 + 8 = 20 bytes, rounded up to 24 because objects are aligned to 8 bytes. With compact headers it is 8 + 8 = 16 bytes, a third less.</p>
''', kw=['garbage collector', 'G1', 'ZGC', 'Parallel GC', 'Serial GC', 'generational', 'JEP 523', 'compact object headers', 'JEP 519', 'JEP 534', 'object header', 'UseCompactObjectHeaders', '-Xlog:gc']),
    part('jfr', '📹', 'JDK Flight Recorder: see what really happened', '''
<p><b>JDK Flight Recorder</b> (JFR) is built into the JVM and records events such as garbage collections, slow locks, file and socket reads, and CPU samples, with an overhead of about one percent. You can add your own events too, which turns JFR into a cheap timing tool for business steps like checkout.</p>
[[jfr]]
<p>Look at the last lines. Recordings often travel to other teams or support tickets, so Java 27 (JEP 536) <b>redacts</b> values that look like secrets before they are written. Keys matching patterns such as <code>*password*</code>, <code>*token*</code>, <code>*secret*</code> and <code>*api*key*</code> become <code>[REDACTED]</code>. The patterns can be changed with <code>-XX:FlightRecorderOptions:redact-key=...</code>.</p>
<div class="tip">On a live server you do not need to restart anything: <code>jcmd &lt;pid&gt; JFR.start duration=60s filename=prod.jfr</code> records for a minute, and JDK Mission Control or <code>jfr print</code> opens the file.</div>
''', kw=['JFR', 'Java Flight Recorder', 'JDK Flight Recorder', 'jdk.jfr.Event', 'custom event', 'jcmd', 'JFR.start', 'jfr print', 'Mission Control', 'redaction', 'JEP 536', 'profiling']),
    part('aot', '⚡', 'Faster startup with the AOT cache', '''
<p>Each time a Java program starts, the JVM loads, verifies and links the same classes again. Project Leyden fixes that with an <b>ahead of time cache</b>. You run the app once as a training run, and the JVM saves the loaded and linked classes, and since Java 25 the method profiles too, into a cache file. Later starts read the cache instead of doing the work again.</p>
[[aot]]
<p>Without the cache, dozens of classes had to be found and parsed from the JDK image. With the cache almost none were. The JEP authors measured 42 percent faster startup for both a small stream program and the Spring PetClinic demo. Java 24 added the cache (JEP 483), Java 25 made it a single command and stored method profiles (JEP 514 and JEP 515), and Java 26 lets it work with any collector, including ZGC (JEP 516).</p>
<div class="note">Use the same JDK and the same classpath for training and production. If they differ, the JVM simply ignores the cache and starts the normal way.</div>
''', kw=['AOT cache', 'ahead of time', 'Project Leyden', 'startup time', 'AOTCacheOutput', 'AOTCache', 'JEP 483', 'JEP 514', 'JEP 515', 'JEP 516', 'CDS', 'class data sharing', 'training run']),
    part('scenario', '🎬', 'Real world scenario: a service that misbehaves in a small container', '''
<div class="scenario"><b>The situation</b>A test reporting service runs fine on laptops, but in a 1 CPU, 1 GB container it starts slowly, pauses for long stretches and is sometimes killed for using too much memory.</div>
<p>The first step is always to ask the JVM how it was started. A small health check endpoint can report it.</p>
[[inspect]]
<p>This run is on a build machine with several CPUs, so it shows G1. On Java 25 in the 1 CPU container the same check would show the Serial collector (named Copy and MarkSweepCompact), and the default heap would be only a quarter of the memory. The team sets the flags on purpose instead of trusting the defaults:</p>
<div class="tw"><table class="jt"><tr><th>Problem</th><th>Flag or tool</th></tr>
<tr><td>Heap too small or too large for the container</td><td><code>-XX:MaxRAMPercentage=75</code></td></tr>
<tr><td>Serial collector picked on a small machine</td><td><code>-XX:+UseG1GC</code>, or move to Java 27</td></tr>
<tr><td>Slow first start</td><td><code>-XX:AOTCache=app.aot</code> from a training run</td></tr>
<tr><td>Too much memory for many small objects</td><td>compact object headers (default in Java 27)</td></tr>
<tr><td>Nobody knows where time goes</td><td><code>jcmd &lt;pid&gt; JFR.start</code> and a custom event per report</td></tr>
<tr><td>Crash with no clues</td><td><code>-XX:+HeapDumpOnOutOfMemoryError</code></td></tr></table></div>
''', kw=['container', 'Docker', 'MaxRAMPercentage', 'JVM flags', 'ManagementFactory', 'GarbageCollectorMXBean', 'HeapDumpOnOutOfMemoryError', 'JVM tuning', 'production troubleshooting']),
]

INFO = {'title': 'A tour of the engine room', 'panels': [
    panel([['e', '📄'], ['t', 'CA FE BA BE', {'b': 1}]], 'Class file', 'Every class starts with the same four bytes.', 'Then the version, constant pool and bytecode.'),
    panel([['e', '🚚'], ['t', 'ask the parent first', {'b': 1}]], 'Class loaders', 'Bootstrap, platform, application.', 'Loaded lazily, initialised once.'),
    panel([['e', '🔥'], ['t', 'interpreter → C1 → C2', {'b': 1, 'size': 11}]], 'JIT', 'Hot code becomes machine code.', 'Warm up before you measure.'),
    panel([['e', '📹'], ['t', 'JFR.start', {'b': 1}]], 'Flight Recorder', 'Record what really happened.', 'Secrets are redacted in Java 27.')],
    'remember': 'javac writes bytecode, class loaders bring it in on first use, the interpreter starts it, the JIT makes hot code fast, and the garbage collector cleans up. JFR shows what happened, and the AOT cache makes the next start faster.'}

REAL = [
    ['🐳', 'A team moving to Kubernetes', 'Found their pods used the Serial collector because each had one CPU. Setting G1 explicitly cut the longest pauses from seconds to tens of milliseconds.'],
    ['🚀', 'A serverless function', 'Was slow on every cold start. A training run in the build pipeline and an AOT cache in the image made cold starts noticeably faster.'],
    ['📦', 'A library author', 'Got UnsupportedClassVersionError reports and fixed them by building with <code>--release 17</code> so users on Java 17 could still load the classes.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to the inside of the JVM: class files, class loaders, memory areas, bytecode, the JIT compiler, garbage collectors, Flight Recorder and the AOT cache.',
        'JVM के अंदर स्वागत है: class files, class loaders, memory areas, bytecode, JIT compiler, garbage collectors, Flight Recorder और AOT cache।',
        'JVM ಒಳಗೆ ಸ್ವಾಗತ: class files, class loaders, memory areas, bytecode, JIT, garbage collectors, Flight Recorder.',
        'JVM ଭିତରକୁ ସ୍ୱାଗତ: class files, class loaders, memory areas, bytecode, JIT, garbage collectors, Flight Recorder।',
        'مرحبًا بك داخل JVM: ملفات الأصناف، ومحمّلات الأصناف، ومناطق الذاكرة، والبايت كود، ومترجم JIT، وجامعات القمامة، ومسجل الطيران.',
        'Willkommen im Inneren der JVM: Class-Dateien, Class Loader, Speicherbereiche, Bytecode, JIT-Compiler, Garbage Collector, Flight Recorder und AOT-Cache.'),
    say('journey', 'The journey', 'javac turns source into bytecode. At run time a class loader reads it, the verifier checks it, the interpreter runs it, and the JIT compiles hot code to machine code.',
        'javac source को bytecode बनाता है। चलते समय class loader उसे पढ़ता है, verifier जाँचता है, interpreter चलाता है, और JIT hot code को machine code बनाता है।',
        'javac source ಅನ್ನು bytecode ಮಾಡುತ್ತದೆ. class loader ಓದುತ್ತದೆ, verifier ಪರಿಶೀಲಿಸುತ್ತದೆ, interpreter ಓಡಿಸುತ್ತದೆ, JIT machine code ಮಾಡುತ್ತದೆ.',
        'javac source କୁ bytecode କରେ। class loader ପଢ଼େ, verifier ଯାଞ୍ଚ କରେ, interpreter ଚଲାଏ, JIT machine code କରେ।',
        'يحوّل javac الشيفرة إلى بايت كود، ثم يقرؤه محمّل الأصناف ويفحصه المدقق ويشغله المفسر، ويترجم JIT الشيفرة الساخنة إلى شيفرة آلة.',
        'javac macht aus Quelltext Bytecode. Zur Laufzeit liest ihn ein Class Loader, der Verifier prüft ihn, der Interpreter führt ihn aus und der JIT übersetzt heißen Code.'),
    say('classfile', 'Class file', 'Every class file starts with CAFEBABE, then a version number. Version 69 means Java 25. An older JVM refuses a newer class file.',
        'हर class file CAFEBABE से शुरू होती है, फिर version number। Version 69 का मतलब Java 25 है। पुराना JVM नई class file नहीं चलाता।',
        'ಪ್ರತಿ class file CAFEBABE ನಿಂದ ಆರಂಭ, ನಂತರ version. 69 ಅಂದರೆ Java 25.',
        'ପ୍ରତି class file CAFEBABE ରୁ ଆରମ୍ଭ, ତା ପରେ version। 69 ମାନେ Java 25।',
        'يبدأ كل ملف صنف بالبايتات CAFEBABE ثم رقم الإصدار، والإصدار 69 يعني Java 25، وترفض JVM الأقدم ملفًا أحدث.',
        'Jede Class-Datei beginnt mit CAFEBABE, dann folgt die Version. 69 bedeutet Java 25. Eine ältere JVM lehnt eine neuere Datei ab.'),
    say('loading', 'Class loading', 'Class loaders ask their parent first. A class is loaded when first needed and initialised once, on first real use.',
        'Class loaders पहले अपने parent से पूछते हैं। Class पहली ज़रूरत पर load होती है और पहली असली इस्तेमाल पर एक बार initialise होती है।',
        'Class loaders ಮೊದಲು parent ಅನ್ನು ಕೇಳುತ್ತವೆ. ಮೊದಲ ಬಳಕೆಯಲ್ಲಿ ಒಮ್ಮೆ initialise ಆಗುತ್ತದೆ.',
        'Class loaders ପ୍ରଥମେ parent କୁ ପଚାରନ୍ତି। ପ୍ରଥମ ବ୍ୟବହାରରେ ଥରେ initialise ହୁଏ।',
        'تسأل محمّلات الأصناف أصلها أولًا، ويُحمَّل الصنف عند أول حاجة ويُهيأ مرة واحدة عند أول استخدام فعلي.',
        'Class Loader fragen zuerst ihre Eltern. Eine Klasse wird beim ersten Bedarf geladen und beim ersten echten Gebrauch einmal initialisiert.'),
    say('memory', 'Memory areas', 'Each thread has a stack of frames for local variables. Objects live on the shared heap. Classes live in metaspace.',
        'हर thread के पास local variables के लिए frames का stack होता है। Objects shared heap पर रहते हैं। Classes metaspace में रहती हैं।',
        'ಪ್ರತಿ thread ಗೆ frames stack ಇದೆ. Objects heap ನಲ್ಲಿ, classes metaspace ನಲ್ಲಿ.',
        'ପ୍ରତି thread ର frames stack ଅଛି। Objects heap ରେ, classes metaspace ରେ।',
        'لكل خيط مكدس من الإطارات للمتغيرات المحلية، وتعيش الكائنات في الكومة المشتركة، والأصناف في metaspace.',
        'Jeder Thread hat einen Stack aus Frames für lokale Variablen. Objekte liegen im gemeinsamen Heap, Klassen im Metaspace.'),
    say('bytecode', 'Bytecode', 'The JVM is a stack machine. iload pushes a local onto the operand stack, imul multiplies the top two, and ireturn returns the result.',
        'JVM एक stack machine है। iload local को operand stack पर रखता है, imul ऊपर के दो को गुणा करता है, ireturn परिणाम लौटाता है।',
        'JVM stack machine. iload stack ಮೇಲೆ ಇಡುತ್ತದೆ, imul ಗುಣಿಸುತ್ತದೆ, ireturn ಹಿಂದಿರುಗಿಸುತ್ತದೆ.',
        'JVM stack machine। iload stack ଉପରେ ରଖେ, imul ଗୁଣନ କରେ, ireturn ଫେରାଏ।',
        'JVM آلة مكدس: iload يدفع متغيرًا محليًا إلى المكدس، وimul يضرب القيمتين العلويتين، وireturn يعيد النتيجة.',
        'Die JVM ist eine Stackmaschine. iload legt eine Variable auf den Operandenstack, imul multipliziert die oberen zwei, ireturn gibt das Ergebnis zurück.'),
    say('jit', 'JIT compiler', 'Methods start in the interpreter. Hot methods are compiled by C1, then by C2 using the profile. This is why Java needs a warm up.',
        'Methods interpreter में शुरू होते हैं। Hot methods पहले C1 से, फिर profile के साथ C2 से compile होते हैं। इसीलिए Java को warm up चाहिए।',
        'Methods interpreter ನಲ್ಲಿ ಆರಂಭ. Hot methods C1 ನಂತರ C2 ನಿಂದ compile ಆಗುತ್ತವೆ.',
        'Methods interpreter ରେ ଆରମ୍ଭ। Hot methods C1 ପରେ C2 ଦ୍ୱାରା compile ହୁଏ।',
        'تبدأ الدوال في المفسر، ثم تُترجم الدوال الساخنة بواسطة C1 ثم C2 حسب الملف الشخصي، ولهذا تحتاج Java إلى إحماء.',
        'Methoden starten im Interpreter. Heiße Methoden kompiliert erst C1, dann C2 mit dem Profil. Deshalb braucht Java eine Aufwärmphase.'),
    say('gc', 'Collectors', 'G1 is the default collector, and from Java 27 it is used even on tiny machines. Compact object headers shrink every object header from 12 to 8 bytes.',
        'G1 default collector है, और Java 27 से छोटी machines पर भी। Compact object headers हर object header को 12 से 8 bytes करते हैं।',
        'G1 default collector, Java 27 ರಿಂದ ಸಣ್ಣ machines ನಲ್ಲೂ. Compact headers 12 ರಿಂದ 8 bytes.',
        'G1 default collector, Java 27 ରୁ ଛୋଟ machines ରେ ମଧ୍ୟ। Compact headers 12 ରୁ 8 bytes।',
        'G1 هو الجامع الافتراضي، ومنذ Java 27 يُستخدم حتى على الأجهزة الصغيرة، وتصغّر الترويسات المضغوطة ترويسة كل كائن من 12 إلى 8 بايت.',
        'G1 ist der Standard-Collector, ab Java 27 auch auf kleinen Maschinen. Kompakte Objekt-Header verkleinern jeden Header von 12 auf 8 Bytes.'),
    say('jfr', 'Flight Recorder', 'JDK Flight Recorder records what the JVM did with about one percent overhead. You can add your own events, and Java 27 redacts secrets.',
        'JDK Flight Recorder लगभग एक प्रतिशत overhead में JVM की गतिविधि रिकॉर्ड करता है। आप अपने events जोड़ सकते हैं, और Java 27 secrets छिपाता है।',
        'JDK Flight Recorder ಸುಮಾರು ಒಂದು ಶೇಕಡಾ overhead ನಲ್ಲಿ ದಾಖಲಿಸುತ್ತದೆ. Java 27 secrets ಮರೆಮಾಡುತ್ತದೆ.',
        'JDK Flight Recorder ପ୍ରାୟ ଏକ ପ୍ରତିଶତ overhead ରେ ରେକର୍ଡ କରେ। Java 27 secrets ଲୁଚାଏ।',
        'يسجل مسجل الطيران ما فعلته JVM بكلفة نحو واحد بالمئة، ويمكنك إضافة أحداثك، وتخفي Java 27 الأسرار.',
        'Der JDK Flight Recorder zeichnet mit etwa einem Prozent Aufwand auf, was die JVM tat. Eigene Events sind möglich, und Java 27 schwärzt Geheimnisse.'),
    say('aot', 'AOT cache', 'A training run saves loaded and linked classes into an AOT cache, so later starts skip that work and start faster.',
        'एक training run loaded और linked classes को AOT cache में सहेजता है, ताकि बाद की शुरुआत तेज़ हो।',
        'Training run classes ಅನ್ನು AOT cache ನಲ್ಲಿ ಉಳಿಸುತ್ತದೆ, ಮುಂದಿನ start ವೇಗ.',
        'Training run classes କୁ AOT cache ରେ ସଞ୍ଚୟ କରେ, ପରବର୍ତ୍ତୀ start ଦ୍ରୁତ।',
        'يحفظ تشغيل تدريبي الأصناف المحمّلة والمربوطة في ذاكرة AOT، فيكون الإقلاع اللاحق أسرع.',
        'Ein Trainingslauf speichert geladene und gelinkte Klassen in einem AOT-Cache, sodass spätere Starts schneller sind.'),
    say('scenario', 'Scenario', 'In a small container, check how the JVM was started, then set the heap percentage, the collector and the AOT cache on purpose.',
        'छोटे container में पहले देखें कि JVM कैसे शुरू हुआ, फिर heap percentage, collector और AOT cache जानबूझकर सेट करें।',
        'ಸಣ್ಣ container ನಲ್ಲಿ JVM ಹೇಗೆ ಆರಂಭವಾಯಿತು ನೋಡಿ, ನಂತರ heap, collector ಹೊಂದಿಸಿ.',
        'ଛୋଟ container ରେ JVM କିପରି ଆରମ୍ଭ ହେଲା ଦେଖନ୍ତୁ, ତା ପରେ heap, collector ସେଟ୍ କରନ୍ତୁ।',
        'في حاوية صغيرة تحقق أولًا من طريقة تشغيل JVM، ثم اضبط نسبة الكومة والجامع وذاكرة AOT عن قصد.',
        'Prüfe in einem kleinen Container zuerst, wie die JVM gestartet wurde, und setze dann Heap-Anteil, Collector und AOT-Cache bewusst.'),
]

QUIZ = [
    quiz('e', 'What are the first four bytes of every class file?', ['CA FE BA BE', 'JAVA', '00 00 00 00', 'The class name'], 0, 'A coffee joke.', 'The magic number 0xCAFEBABE marks a file as a Java class file.'),
    quiz('e', 'Where do objects created with <code>new</code> live?', ['On the heap', 'On the stack of the thread', 'In metaspace', 'In the code cache'], 0, 'Shared by all threads.', 'Frames on the stack only hold references to them.'),
    quiz('e', 'Which loader loads <code>java.lang.String</code>?', ['The bootstrap class loader', 'The application class loader', 'The platform class loader', 'Your own loader'], 0, 'getClassLoader() returns null.', 'Core classes in java.base always come from the bootstrap loader.'),
    quiz('m', 'A library built with Java 25 fails on a Java 21 server. Which error appears?', ['UnsupportedClassVersionError', 'ClassNotFoundException', 'StackOverflowError', 'VerifyError'], 0, 'Version 69 is too new for that JVM.', 'Build with --release 21 or upgrade the server JDK.'),
    quiz('m', 'When does a static block run?', ['Once, on the first real use of the class', 'Every time an object is created', 'When the JVM starts, for every class on the classpath', 'When the class is compiled'], 0, 'Lazy and once.', 'Creating an array of the type does not count as real use.'),
    quiz('m', 'What does tier 4 in PrintCompilation output mean?', ['The method was compiled by C2 with full optimisation', 'The method failed four times', 'It runs in the interpreter', 'It was loaded by the fourth class loader'], 0, 'The highest tier.', 'Tiers 1 to 3 are C1 code, tier 4 is C2 code built from the profile.'),
    quiz('m', 'What does the bytecode <code>imul</code> do?', ['Pops two ints, multiplies them and pushes the result', 'Multiplies two longs', 'Calls a method named mul', 'Loads a local variable'], 0, 'i means int.', 'The JVM is a stack machine, so imul works on the operand stack.'),
    quiz('h', 'On Java 25, which collector does the JVM pick on a machine with 1 CPU and 512 MB?', ['Serial', 'G1', 'ZGC', 'Parallel'], 0, 'Small machine ergonomics.', 'Java 27 removed this exception with JEP 523, so G1 is used everywhere.'),
    quiz('h', 'Why can a recording from Java 27 be shared more safely?', ['Values of keys that look like secrets are written as [REDACTED]', 'Recordings are encrypted with ML-KEM', 'JFR no longer records system properties', 'Recordings expire after an hour'], 0, 'JEP 536.', 'Patterns such as *password* and *token* are redacted before the data is written.'),
    quiz('h', 'What does a training run with <code>-XX:AOTCacheOutput=app.aot</code> produce?', ['A cache of loaded and linked classes and method profiles for faster later starts', 'A native executable', 'A JAR file', 'A heap dump'], 0, 'Project Leyden.', 'Later runs use -XX:AOTCache=app.aot and skip loading and linking work.'),
    quiz('x', 'What does this print?', ['B1', '1B', '1', 'B'], 0, 'Static blocks run before the first real use completes.', 'Reading B.X initialises B first, so its static block prints B before the value 1 is printed.', code='class B {\n    static int X = 1;\n    static { System.out.print("B"); }\n}\n\nvoid main() {\n    System.out.println(B.X);\n}', run=True),
    quiz('x', 'What does this print?', ['bootstrap', 'app', 'platform', 'null pointer'], 0, 'Who loads core classes.', 'getClassLoader() returns null for classes from the bootstrap loader.', code='ClassLoader l = Integer.class.getClassLoader();\nSystem.out.println(l == null ? "bootstrap" : l.getName());', run=True),
]

CALC = [
    calc('e', 'Class file version 69 is Java 25. Each Java release adds 1. What major version is Java 27?', '71', 'Add the difference.', ['<span class="eq">69 + (27 − 25) = 71</span>']),
    calc('e', 'A Point has two int fields. How many bytes do the fields take?', '8', 'An int is 4 bytes.', ['<span class="eq">2 × 4 = 8 bytes</span>']),
    calc('m', 'With compact headers a Point is 16 bytes, with the old headers 24. How many MB are saved for 1,000,000 Points? Use 1 MB = 1,000,000 bytes.', '8', 'Difference times count.', ['<span class="eq">(24 − 16) × 1,000,000 = 8,000,000 bytes = 8 MB</span>']),
    calc('m', 'Spring PetClinic started in 4.486 s without and 2.604 s with an AOT cache. What percent faster is that, to the nearest whole number?', '42', 'Saved time divided by the old time.', ['<span class="eq"><span class="fr"><i>4.486 − 2.604</i><i>4.486</i></span> = <span class="fr"><i>1.882</i><i>4.486</i></span> ≈ 0.42</span>', 'That is about 42 percent, as JEP 483 reports.']),
    calc('m', 'What does this print?', '3', 'Count the frames: main, a, b.', ['main calls a, which calls b.', 'Inside b the stack holds three of these frames.'], code='static int depth() {\n    return StackWalker.getInstance().walk(s -> s.count()).intValue();\n}\nstatic int b() { return depth() - 1; }\nstatic int a() { return b(); }\n\nvoid main() {\n    System.out.println(a());\n}', run=True),
    calc('h', 'A service runs 200 platform threads with the default 1 MB stack each. How many MB of stack can they reserve?', '200', 'One MB per thread.', ['<span class="eq">200 × 1 MB = 200 MB</span>', 'This memory is outside the heap, so -Xmx does not limit it.']),
    calc('h', 'A container has 1024 MB and you set <code>-XX:MaxRAMPercentage=75</code>. How many MB may the heap grow to?', '768', '75 percent of 1024.', ['<span class="eq">1024 × <span class="fr"><i>75</i><i>100</i></span> = 768 MB</span>', 'The rest is left for stacks, metaspace, the code cache and native memory.']),
    calc('x', 'What does this print?', 'true', 'Compare two loaders.', ['Both classes come from your program, so the same application class loader loads them.'], code='record A() {}\nrecord B() {}\n\nvoid main() {\n    System.out.println(A.class.getClassLoader() == B.class.getClassLoader());\n}', run=True),
]

T = {
    'slug': 'java-jvm-internals', 'title': 'Inside the JVM: how a Java program really runs', 'short': 'Inside the JVM', 'emoji': '⚙️', 'module': MODULE, 'minutes': 26,
    'lead': 'What happens between typing java Main and seeing output? This chapter follows a program through the class file, the class loaders, the memory areas, bytecode, the JIT compiler and the garbage collector, then shows the tools that make Java services fast and easy to diagnose: Flight Recorder, the AOT cache from Java 24 to 26, compact object headers and G1 everywhere in Java 27.',
    'desc': 'How the JVM runs Java: class file format, CAFEBABE, class loaders and parent delegation, static initialisation, stack, heap and metaspace, bytecode and the operand stack, interpreter, C1 and C2 JIT tiers, garbage collectors, JDK Flight Recorder with custom events and redaction, the AOT cache and compact object headers.',
    'summary': 'The journey from source to machine code, the class file layout and versions, class loaders and lazy initialisation, stack frames and the heap, bytecode on the operand stack, tiered JIT compilation, G1, ZGC and the Java 27 G1 default, compact object headers, Flight Recorder events and secret redaction, the AOT cache, and tuning a service for a small container.',
    'keywords': ['JVM internals', 'class loader', 'bytecode', 'JIT', 'HotSpot', 'garbage collector', 'G1', 'ZGC', 'stack', 'heap', 'metaspace', 'JFR', 'AOT cache', 'Project Leyden', 'compact object headers', 'Java 27'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
