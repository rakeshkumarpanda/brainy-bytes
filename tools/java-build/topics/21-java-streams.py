# Chapter 21: the Streams API, collectors, primitive streams, Optional, stream gatherers and parallel streams.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

CODES = {
    'first': j('''
import java.util.*;

class Main {
    public static void main(String[] args) {
        List<Integer> times = List.of(420, 2300, 180, 1800, 950, 3100);

        // Old style: a loop with a temporary list
        List<String> slow = new ArrayList<>();
        for (int t : times) {
            if (t > 1000) slow.add(t / 1000.0 + " s");
        }
        System.out.println(slow);

        // Stream style: say what you want, not how to loop
        List<String> slow2 = times.stream()
            .filter(t -> t > 1000)
            .map(t -> t / 1000.0 + " s")
            .toList();
        System.out.println(slow2);
    }
}
''', 'A loop and the stream that says the same thing'),
    'lazy': j('''
import java.util.*;

class Main {
    public static void main(String[] args) {
        List<String> names = List.of("asha", "ravi", "meera", "arun", "zoya");
        var pipeline = names.stream()
            .filter(n -> { System.out.println("  filter " + n); return n.length() == 4; })
            .map(n -> { System.out.println("  map    " + n); return n.toUpperCase(); });
        System.out.println("Pipeline built. Nothing has run yet.");

        Optional<String> first = pipeline.findFirst();   // the terminal operation pulls elements
        System.out.println("Result: " + first.get());
    }
}
''', 'Streams are lazy: nothing runs until a terminal operation'),
    'once': j('''
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        Stream<String> s = Stream.of("a", "b", "c");
        System.out.println(s.count());
        System.out.println(s.count());       // a stream can be used only once
    }
}
''', 'A stream can only be consumed once', expect='throw'),
    'sources': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        System.out.println(Stream.of("chrome", "firefox", "webkit").toList());
        System.out.println(Arrays.stream(new int[]{3, 1, 2}).sum());
        System.out.println(IntStream.rangeClosed(1, 5).boxed().toList());
        System.out.println(Stream.iterate(1, n -> n <= 100, n -> n * 3).toList());   // Java 9: with a stop condition
        System.out.println(Stream.generate(() -> "retry").limit(3).toList());
        System.out.println("banana".chars().filter(c -> c == 'a').count());
        System.out.println(Map.of("pass", 8).entrySet().stream().map(e -> e.getKey() + "=" + e.getValue()).toList());
        System.out.println(Stream.ofNullable(null).count());                          // Java 9: zero or one element
    }
}
''', 'Ways to start a stream'),
    'intermediate': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        List<List<String>> suites = List.of(List.of("login", "logout"), List.of("cart", "login"), List.of("pay"));

        System.out.println(suites.stream().flatMap(List::stream).toList());             // flatten
        System.out.println(suites.stream().flatMap(List::stream).distinct().sorted().toList());
        System.out.println(Stream.of(5, 3, 8, 1).sorted(Comparator.reverseOrder()).skip(1).limit(2).toList());

        List<Integer> log = List.of(200, 200, 201, 500, 200, 404);
        System.out.println(log.stream().takeWhile(c -> c < 300).toList());   // Java 9: until the first failure
        System.out.println(log.stream().dropWhile(c -> c < 300).toList());   // Java 9: from the first failure on

        // mapMulti (Java 16): one input can push zero, one or many outputs
        System.out.println(Stream.of("a,b", "", "c").<String>mapMulti((s, push) -> {
            for (String p : s.split(",")) if (!p.isEmpty()) push.accept(p);
        }).toList());
    }
}
''', 'flatMap, distinct, sorted, skip, limit, takeWhile, dropWhile and mapMulti'),
    'terminal': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        List<Integer> marks = List.of(72, 91, 45, 88, 60);

        System.out.println("count    " + marks.stream().count());
        System.out.println("sum      " + marks.stream().reduce(0, Integer::sum));
        System.out.println("max      " + marks.stream().max(Integer::compare).get());
        System.out.println("any < 50 " + marks.stream().anyMatch(m -> m < 50));
        System.out.println("all > 40 " + marks.stream().allMatch(m -> m > 40));
        System.out.println("none 100 " + marks.stream().noneMatch(m -> m == 100));
        System.out.println("first 80+ " + marks.stream().filter(m -> m >= 80).findFirst().orElse(-1));
        System.out.println("array    " + Arrays.toString(marks.stream().sorted().toArray()));
    }
}
''', 'Terminal operations give you a result'),
    'tolist': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        List<String> a = Stream.of("x", "y").toList();                       // Java 16: unmodifiable
        List<String> b = Stream.of("x", "y").collect(Collectors.toList());   // a modifiable ArrayList today
        b.add("z");
        System.out.println(b);
        a.add("z");
    }
}
''', 'toList() gives an unmodifiable list', expect='throw'),
    'collectors': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    record Result(String suite, String name, String status, int ms) {}

    public static void main(String[] args) {
        List<Result> rs = List.of(
            new Result("checkout", "pay by card", "PASS", 1200), new Result("checkout", "apply coupon", "FAIL", 800),
            new Result("login", "valid user", "PASS", 300), new Result("login", "locked user", "PASS", 450),
            new Result("search", "by name", "FAIL", 2100));

        var perStatus = rs.stream().collect(Collectors.groupingBy(Result::status, TreeMap::new, Collectors.counting()));
        var slowOrNot = rs.stream().collect(Collectors.partitioningBy(r -> r.ms() > 1000, Collectors.mapping(Result::name, Collectors.toList())));
        var avgPerSuite = rs.stream().collect(Collectors.groupingBy(Result::suite, TreeMap::new, Collectors.averagingInt(Result::ms)));
        var names = rs.stream().map(Result::name).collect(Collectors.joining(", ", "[", "]"));
        var msByName = rs.stream().collect(Collectors.toMap(Result::name, Result::ms, Integer::sum, LinkedHashMap::new));
        var stats = rs.stream().collect(Collectors.summarizingInt(Result::ms));
        // teeing (Java 12): two collectors over the same data, then combine them
        var passRate = rs.stream().collect(Collectors.teeing(
            Collectors.counting(),
            Collectors.filtering(r -> r.status().equals("PASS"), Collectors.counting()),
            (all, pass) -> "pass rate " + (100 * pass / all) + "%"));

        System.out.println(perStatus);
        System.out.println(slowOrNot);
        System.out.println(avgPerSuite);
        System.out.println(names);
        System.out.println(msByName);
        System.out.println(stats);
        System.out.println(passRate);
    }
}
''', 'Collectors: groupingBy, partitioningBy, joining, toMap, summarizing and teeing'),
    'tomapdup': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        // Two entries with the same key and no merge function
        Map<String, Integer> m = Stream.of("login", "cart", "login")
            .collect(Collectors.toMap(s -> s, String::length));
        System.out.println(m);
    }
}
''', 'toMap without a merge function fails on duplicate keys', expect='throw'),
    'primitive': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        List<String> prices = List.of("499", "1299", "89", "2500");

        IntSummaryStatistics st = prices.stream().mapToInt(Integer::parseInt).summaryStatistics();
        System.out.println(st.getMin() + " " + st.getMax() + " " + st.getAverage() + " " + st.getSum());

        System.out.println(IntStream.rangeClosed(1, 5).map(i -> i * i).sum());
        System.out.println(IntStream.of(4, 8, 6).average().orElse(0));
        System.out.println(DoubleStream.of(1.5, 2.5).map(Math::ceil).boxed().toList());
    }
}
''', 'IntStream, LongStream and DoubleStream avoid boxing'),
    'optional': j('''
import java.util.*;

class Main {
    record User(String name, String email) {}

    static Optional<User> find(String name) {
        return name.equals("asha") ? Optional.of(new User("asha", "asha@shop.test")) : Optional.empty();
    }

    static String slowDefault() {
        System.out.println("  (slowDefault ran)");
        return "guest@shop.test";
    }

    public static void main(String[] args) {
        System.out.println(find("asha").map(User::email).orElse("none"));
        System.out.println(find("ravi").map(User::email).orElse("none"));
        System.out.println(find("asha").filter(u -> u.email().endsWith(".com")).isPresent());

        System.out.println("orElse with a value present:");
        System.out.println(find("asha").map(User::email).orElse(slowDefault()));      // always runs slowDefault
        System.out.println("orElseGet with a value present:");
        System.out.println(find("asha").map(User::email).orElseGet(Main::slowDefault)); // runs it only when empty

        find("ravi").ifPresentOrElse(u -> System.out.println("hi " + u.name()), () -> System.out.println("no such user"));
        System.out.println(find("ravi").or(() -> find("asha")).get().name());           // Java 9
        System.out.println(Optional.ofNullable(System.getenv("NO_SUCH_VAR")).orElse("default"));
        find("ravi").orElseThrow(() -> new NoSuchElementException("user ravi not found"));
    }
}
''', 'Optional: map, filter, orElse against orElseGet, ifPresentOrElse, or and orElseThrow', expect='throw'),
    'gatherers': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        List<Integer> responseMs = List.of(120, 140, 900, 950, 130, 110, 1000);

        // windowFixed: batches of 3, for example to send rows to an API in chunks
        System.out.println(responseMs.stream().gather(Gatherers.windowFixed(3)).toList());
        // windowSliding: every run of 3 in a row, for moving averages
        System.out.println(responseMs.stream().gather(Gatherers.windowSliding(3))
            .map(w -> w.stream().mapToInt(i -> i).average().orElse(0)).map(Math::round).toList());
        // scan: running totals
        System.out.println(responseMs.stream().gather(Gatherers.scan(() -> 0, Integer::sum)).toList());
        // fold: one final value, built step by step
        System.out.println(responseMs.stream().gather(Gatherers.fold(() -> "", (acc, ms) -> acc + (ms > 500 ? "S" : "f"))).findFirst().get());
    }
}
''', 'Stream gatherers (final in Java 24): windows, scan and fold'),
    'custom-gatherer': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    // A custom gatherer: pass on an element only when it differs from the one before (like uniq in a shell)
    static <T> Gatherer<T, ?, T> changesOnly() {
        return Gatherer.ofSequential(
            () -> new Object[1],                                    // state: the last element seen
            (state, element, downstream) -> {
                if (!Objects.equals(state[0], element)) {
                    state[0] = element;
                    return downstream.push(element);
                }
                return true;                                         // keep going
            });
    }

    public static void main(String[] args) {
        List<String> health = List.of("UP", "UP", "DOWN", "DOWN", "DOWN", "UP", "UP");
        System.out.println(health.stream().gather(changesOnly()).toList());
    }
}
''', 'Your own gatherer: report only status changes'),
    'parallel': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) {
        // A correct parallel stream: no shared state, an associative operation
        long primes = LongStream.rangeClosed(2, 200_000).parallel()
            .filter(n -> LongStream.rangeClosed(2, (long) Math.sqrt(n)).noneMatch(d -> n % d == 0))
            .count();
        System.out.println("primes up to 200000: " + primes);

        // collect is safe in parallel: each thread fills its own list, then the lists are merged
        List<Integer> evens = IntStream.range(0, 1000).parallel().filter(i -> i % 2 == 0).boxed().toList();
        System.out.println(evens.size() + " evens, still in order: " + evens.subList(0, 5));
    }
}
''', 'Parallel streams done right', trace=False),
    'parallel-bug': show('''
List<Integer> out = new ArrayList<>();
IntStream.range(0, 10_000).parallel().forEach(out::add);   // many threads write one ArrayList
System.out.println(out.size());                             // often less than 10000, sometimes a crash
''', 'The classic parallel stream bug', result='Several threads call add on the same ArrayList at once. Some additions overwrite each other, so the size is often below 10000, and sometimes an ArrayIndexOutOfBoundsException is thrown. The output changes from run to run, which is why it is not run on this page. Use <code>toList()</code> or <code>collect</code> instead.'),
    'scenario': j('''
import java.util.*;
import java.util.stream.*;

class Main {
    record Run(String test, String status, int ms) {}

    public static void main(String[] args) {
        // The last three nightly runs of a regression suite
        List<Run> runs = List.of(
            new Run("login", "PASS", 310), new Run("cart", "FAIL", 950), new Run("pay", "PASS", 2400), new Run("search", "PASS", 700),
            new Run("login", "PASS", 290), new Run("cart", "PASS", 880), new Run("pay", "PASS", 2600), new Run("search", "PASS", 650),
            new Run("login", "PASS", 305), new Run("cart", "FAIL", 990), new Run("pay", "PASS", 2550), new Run("search", "FAIL", 4000));

        Map<String, Set<String>> outcomes = runs.stream().collect(Collectors.groupingBy(Run::test, TreeMap::new,
            Collectors.mapping(Run::status, Collectors.toSet())));
        List<String> flaky = outcomes.entrySet().stream().filter(e -> e.getValue().size() > 1).map(Map.Entry::getKey).toList();
        System.out.println("Flaky tests: " + flaky);

        System.out.println("Average time per test:");
        runs.stream().collect(Collectors.groupingBy(Run::test, TreeMap::new, Collectors.averagingInt(Run::ms)))
            .forEach((test, avg) -> System.out.printf("  %-7s %6.0f ms%n", test, avg));

        System.out.println("Three slowest single runs: " + runs.stream()
            .sorted(Comparator.comparingInt(Run::ms).reversed()).limit(3).map(r -> r.test() + " " + r.ms()).toList());

        long passed = runs.stream().filter(r -> r.status().equals("PASS")).count();
        System.out.printf("Pass rate: %d of %d = %.1f%%%n", passed, runs.size(), 100.0 * passed / runs.size());
    }
}
''', 'Real world: nightly test report analytics'),
}

DG = {
    'pipeline': {'t': 'A stream pipeline has three parts', 'w': 900, 'h': 210, 'mw': 640,
        'n': [['src', 20, 60, 170, 80, 'Source', {'c': 0, 'sub': 'list.stream()\nIntStream.range'}],
              ['i1', 230, 60, 150, 80, 'filter', {'c': 2, 'sub': 'intermediate\nlazy'}],
              ['i2', 410, 60, 150, 80, 'map', {'c': 2, 'sub': 'intermediate\nlazy'}],
              ['i3', 590, 60, 120, 80, 'limit', {'c': 3, 'sub': 'short circuit'}],
              ['t', 740, 60, 140, 80, 'toList()', {'c': 1, 'sub': 'terminal\nstarts the work'}]],
        'e': [['src', 'i1'], ['i1', 'i2'], ['i2', 'i3'], ['i3', 't'], ['t', 'src', {'t': 'pulls one element at a time', 'd': 1, 'via': [[810, 180], [105, 180]]}]],
        'st': [[['src'], 'A source gives elements: a collection, an array, a range, a file, a generator.'],
               [['i1', 'i2', 'src>i1', 'i1>i2'], 'Intermediate operations return a new stream and only describe the work. They are lazy.'],
               [['i3', 'i2>i3'], 'Some operations short circuit: limit, findFirst and anyMatch can stop the whole pipeline early.'],
               [['t', 'i3>t'], 'Exactly one terminal operation starts everything and produces a result. After it, the stream is used up.'],
               [['t>src'], 'The terminal operation pulls elements through the whole chain one at a time, not stage by stage.']]},
}

PARTS = [
    part('what', '🌊', 'What a stream is', '''
<p>A <b>stream</b> is a pipeline that data flows through. You describe the steps (keep these, change them to that, stop after three), and Java runs them for you. A stream does not store data. It reads from a <b>source</b>, passes each element through <b>intermediate operations</b>, and ends with one <b>terminal operation</b> that gives the result.</p>
[[first]]
<div class="viz" data-viz="flow" data-k="pipeline"></div>
<p>Picture a factory conveyor belt. Workers along the belt check, paint and pack each item. Nothing moves until the packer at the end says "send me the next one".</p>
''', kw=['stream', 'pipeline', 'source', 'intermediate operation', 'terminal operation', 'declarative', 'internal iteration']),
    part('lazy', '😴', 'Laziness and short circuits', '''
<p>Intermediate operations are <b>lazy</b>. Building the pipeline does nothing. When the terminal operation asks for a result, elements travel through all the steps <b>one at a time</b>, and the work stops as soon as the answer is known.</p>
[[lazy]]
<p>Five names were in the list, yet filter and map ran only once each. "asha" already matched, so <code>findFirst</code> had its answer and the other four names were never touched. Try it with your own numbers:</p>
<div class="viz" data-viz="jstream"></div>
[[once]]
''', kw=['lazy evaluation', 'short circuit', 'findFirst', 'limit', 'IllegalStateException', 'stream has already been operated upon or closed', 'vertical processing']),
    part('sources', '🚰', 'Creating streams', '''
<p>Almost anything can feed a stream: collections, arrays, number ranges, single values, generators, the characters of a string and the lines of a file (<code>Files.lines</code>, covered in the file chapter).</p>
[[sources]]
<div class="note"><code>Stream.generate</code> and <code>Stream.iterate</code> without a stop condition are <b>infinite</b>. Always pair them with <code>limit</code>, <code>takeWhile</code> or a short circuiting terminal operation.</div>
''', kw=['Stream.of', 'Arrays.stream', 'IntStream.range', 'rangeClosed', 'Stream.iterate', 'Stream.generate', 'chars', 'ofNullable', 'infinite stream', 'Files.lines']),
    part('intermediate', '🔧', 'Intermediate operations', '''
<div class="tw"><table class="jt"><tr><th>Operation</th><th>What it does</th></tr>
<tr><td><code>filter</code></td><td>keeps elements that pass a Predicate</td></tr>
<tr><td><code>map</code> <code>mapToInt</code></td><td>turns each element into another value</td></tr>
<tr><td><code>flatMap</code> <code>mapMulti</code></td><td>turns each element into zero or more elements and flattens them</td></tr>
<tr><td><code>distinct</code> <code>sorted</code></td><td>removes duplicates (equals), sorts (stateful, they must see everything)</td></tr>
<tr><td><code>limit</code> <code>skip</code></td><td>first n, or all but the first n</td></tr>
<tr><td><code>takeWhile</code> <code>dropWhile</code></td><td>Java 9: until a condition fails, or from where it fails</td></tr>
<tr><td><code>peek</code></td><td>looks at each element without changing it, for debugging only</td></tr></table></div>
[[intermediate]]
''', kw=['filter', 'map', 'flatMap', 'mapMulti', 'distinct', 'sorted', 'limit', 'skip', 'takeWhile', 'dropWhile', 'peek', 'stateful operation']),
    part('terminal', '🏁', 'Terminal operations', '''
<p>A terminal operation runs the pipeline and returns something that is not a stream: a number, a boolean, an Optional, a collection, or nothing at all (<code>forEach</code>).</p>
[[terminal]]
<p><code>toList()</code> (Java 16) is the shortest way to collect, but the list it gives cannot be changed. If you need to add to it later, use <code>collect(Collectors.toCollection(ArrayList::new))</code>.</p>
[[tolist]]
''', kw=['forEach', 'collect', 'toList', 'reduce', 'count', 'min', 'max', 'anyMatch', 'allMatch', 'noneMatch', 'findFirst', 'findAny', 'toArray', 'UnsupportedOperationException']),
    part('collectors', '🧺', 'Collectors: grouping and summarising', '''
<p><code>collect</code> with the helpers in <code>Collectors</code> answers report style questions in one line: how many per status, average time per suite, names of the slow tests.</p>
[[collectors]]
<div class="tw"><table class="jt"><tr><th>Question</th><th>Collector</th></tr>
<tr><td>How many in each group</td><td><code>groupingBy(key, counting())</code></td></tr>
<tr><td>Split into yes and no</td><td><code>partitioningBy(predicate)</code></td></tr>
<tr><td>One text from many</td><td><code>joining(", ")</code></td></tr>
<tr><td>Look up by key</td><td><code>toMap(key, value, merge)</code></td></tr>
<tr><td>Min, max, average, sum at once</td><td><code>summarizingInt</code></td></tr>
<tr><td>Two answers combined</td><td><code>teeing(a, b, combine)</code></td></tr></table></div>
[[tomapdup]]
<div class="tip">Pass <code>TreeMap::new</code> to <code>groupingBy</code> when you want the groups in sorted order. A plain HashMap has no reliable order, which makes report output and test assertions unstable.</div>
''', kw=['Collectors', 'groupingBy', 'counting', 'partitioningBy', 'mapping', 'averagingInt', 'joining', 'toMap', 'merge function', 'IllegalStateException duplicate key', 'summarizingInt', 'teeing', 'filtering', 'TreeMap']),
    part('primitive', '🔢', 'Primitive streams', '''
<p><code>Stream&lt;Integer&gt;</code> stores every number as an object. <code>IntStream</code>, <code>LongStream</code> and <code>DoubleStream</code> work with plain numbers, so they are faster and add <code>sum</code>, <code>average</code> and <code>summaryStatistics</code>. Use <code>mapToInt</code> to enter them and <code>boxed</code> to leave.</p>
[[primitive]]
''', kw=['IntStream', 'LongStream', 'DoubleStream', 'mapToInt', 'boxed', 'sum', 'average', 'summaryStatistics', 'boxing', 'autoboxing cost']),
    part('optional', '🎁', 'Optional', '''
<p><code>Optional&lt;T&gt;</code> is a box that holds one value or nothing. A method that returns Optional tells the caller, in its signature, "I might not find anything". It replaces returning <code>null</code> and the NullPointerException that follows.</p>
[[optional]]
<div class="warn"><code>orElse(x)</code> always evaluates <code>x</code>, even when a value is present. If the default is expensive (a database call, creating a user), use <code>orElseGet(() -&gt; ...)</code>, which runs only when the box is empty.</div>
<div class="tw"><table class="jt"><tr><th>Do</th><th>Do not</th></tr>
<tr><td>Return Optional from a find or lookup method</td><td>Use Optional for fields or method parameters</td></tr>
<tr><td>Chain <code>map</code>, <code>filter</code>, <code>orElse</code></td><td>Call <code>get()</code> without checking</td></tr>
<tr><td>Use <code>orElseThrow</code> with a clear message</td><td>Return <code>null</code> from a method declared to return Optional</td></tr></table></div>
''', kw=['Optional', 'Optional.of', 'ofNullable', 'empty', 'orElse', 'orElseGet', 'orElseThrow', 'ifPresentOrElse', 'Optional.or', 'NoSuchElementException', 'null handling']),
    part('gatherers', '🪣', 'Stream gatherers (Java 24)', '''
<p>Before Java 24, if no built in intermediate operation fitted, you had to leave the stream. <b>Gatherers</b> (JEP 485, final in Java 24, so in the Java 25 LTS) are custom intermediate operations, plugged in with <code>gather(...)</code>. The JDK ships useful ones in <code>Gatherers</code>.</p>
[[gatherers]]
<p>You can write your own with <code>Gatherer.ofSequential</code>: a state, and a function that decides what to push downstream for each element.</p>
[[custom-gatherer]]
<div class="tip">Real uses: send test data rows to an API in batches of 100 (<code>windowFixed</code>), alert when the moving average response time rises (<code>windowSliding</code>), and call a slow service for many ids with limited parallelism (<code>mapConcurrent</code>, which uses virtual threads).</div>
''', kw=['gatherers', 'Gatherer', 'gather', 'windowFixed', 'windowSliding', 'scan', 'fold', 'mapConcurrent', 'JEP 485', 'Java 24', 'custom intermediate operation']),
    part('parallel', '⚡', 'Parallel streams', '''
<p><code>parallel()</code> splits the work across the CPU cores using the common ForkJoinPool. It helps for large amounts of pure calculation with no shared state. It hurts for small lists, for I/O, and for anything that writes to a shared object.</p>
[[parallel]]
[[parallel-bug]]
<div class="note">Rules of thumb: measure before and after, keep lambdas free of side effects, prefer <code>collect</code> or <code>toList</code> to <code>forEach</code> plus add, and remember <code>findAny</code> and <code>forEach</code> do not keep order in parallel. For waiting on many web calls, use virtual threads (next chapters) instead.</div>
''', kw=['parallel stream', 'parallel()', 'ForkJoinPool', 'common pool', 'thread safety', 'side effects', 'race condition', 'forEachOrdered', 'findAny']),
    part('scenario', '🎬', 'Real world scenario: a nightly test report', '''
<div class="scenario"><b>The situation</b>Every morning a QA lead reads three nightly runs of the regression suite. They want the flaky tests, the average time per test, the slowest runs and the pass rate, without opening a spreadsheet.</div>
[[scenario]]
<p>A test that both passed and failed across runs is <b>flaky</b>: <code>groupingBy</code> plus <code>mapping</code> to a Set of statuses finds them in one pass. The same few lines work on real data read from JUnit XML or a database.</p>
''', kw=['test report', 'flaky test detection', 'groupingBy', 'averagingInt', 'pass rate', 'analytics', 'printf']),
]

INFO = {'title': 'Data on a conveyor belt', 'panels': [
    panel([['e', '🚰'], ['t', 'list.stream()', {'b': 1}]], 'Source', 'Elements come from somewhere.', 'Collections, arrays, ranges, files, generators.'),
    panel([['e', '🔧'], ['t', '.filter(...).map(...)', {'b': 1, 'size': 11}]], 'Intermediate', 'Describe the work.', 'Lazy: nothing runs yet.'),
    panel([['e', '🏁'], ['t', '.toList()', {'b': 1}]], 'Terminal', 'One call starts it all.', 'Elements are pulled through one at a time.'),
    panel([['e', '🎁'], ['t', 'Optional<User>', {'b': 1}]], 'Optional', 'Maybe a value, maybe not.', 'orElseGet for expensive defaults.')],
    'remember': 'Source, then lazy intermediate steps, then exactly one terminal operation. Prefer collectors to shared state, toList for results, and Optional for "might not exist".'}

REAL = [
    ['🛒', 'An online shop', 'Builds its "frequently bought together" list with <code>groupingBy(Order::product, counting())</code> over yesterday\'s orders.'],
    ['📈', 'A monitoring tool', 'Uses <code>windowSliding(5)</code> on response times and raises an alert when the moving average crosses 800 ms.'],
    ['🧾', 'A test framework', 'Turns hundreds of JUnit results into a Slack summary with <code>partitioningBy</code> and <code>joining</code>.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to streams. A stream is a pipeline: a source, some lazy steps, and one terminal operation that produces the result.',
        'Streams में आपका स्वागत है। Stream एक pipeline है: एक source, कुछ lazy steps, और एक terminal operation जो result देता है।',
        'Streams ಗೆ ಸ್ವಾಗತ. Stream ಒಂದು pipeline: ಒಂದು source, ಕೆಲವು lazy ಹಂತಗಳು, ಮತ್ತು result ಕೊಡುವ ಒಂದು terminal operation.',
        'Streams କୁ ସ୍ୱାଗତ। Stream ଏକ pipeline: ଗୋଟିଏ source, କିଛି lazy ପଦକ୍ଷେପ, ଏବଂ result ଦେଉଥିବା ଗୋଟିଏ terminal operation।',
        'مرحبًا بك في التدفقات. التدفق خط معالجة: مصدر، وخطوات كسولة، وعملية نهائية واحدة تعطي النتيجة.',
        'Willkommen bei Streams. Ein Stream ist eine Pipeline: eine Quelle, faule Zwischenschritte und eine Endoperation, die das Ergebnis liefert.'),
    say('what', 'What a stream is', 'A stream does not store data. It reads from a source and passes each element through the steps you describe.',
        'Stream data जमा नहीं करता। यह source से पढ़ता है और हर element को आपके बताए steps से गुज़ारता है।',
        'Stream data ಸಂಗ್ರಹಿಸುವುದಿಲ್ಲ. ಅದು source ನಿಂದ ಓದಿ ಪ್ರತಿ element ಅನ್ನು ನೀವು ಹೇಳಿದ ಹಂತಗಳ ಮೂಲಕ ಕಳುಹಿಸುತ್ತದೆ.',
        'Stream data ସଂରକ୍ଷଣ କରେ ନାହିଁ। ଏହା source ରୁ ପଢ଼େ ଏବଂ ପ୍ରତ୍ୟେକ element କୁ ଆପଣଙ୍କ ପଦକ୍ଷେପ ଦେଇ ପଠାଏ।',
        'التدفق لا يخزن البيانات، بل يقرأ من مصدر ويمرر كل عنصر عبر الخطوات التي تصفها.',
        'Ein Stream speichert keine Daten. Er liest aus einer Quelle und schickt jedes Element durch deine Schritte.'),
    say('lazy', 'Laziness', 'Intermediate steps are lazy. Elements travel one at a time, and the work stops as soon as the answer is known. A stream can be used only once.',
        'Intermediate steps lazy होते हैं। Elements एक एक करके चलते हैं, और जवाब मिलते ही काम रुक जाता है। Stream एक ही बार इस्तेमाल होता है।',
        'Intermediate ಹಂತಗಳು lazy. Elements ಒಂದೊಂದಾಗಿ ಹೋಗುತ್ತವೆ, ಉತ್ತರ ಸಿಕ್ಕ ತಕ್ಷಣ ಕೆಲಸ ನಿಲ್ಲುತ್ತದೆ. Stream ಒಮ್ಮೆ ಮಾತ್ರ ಬಳಸಬಹುದು.',
        'Intermediate ପଦକ୍ଷେପ lazy। Elements ଗୋଟି ଗୋଟି ଯାଆନ୍ତି, ଉତ୍ତର ମିଳିବା ମାତ୍ରେ କାମ ବନ୍ଦ ହୁଏ। Stream ଥରେ ମାତ୍ର ବ୍ୟବହାର ହୁଏ।',
        'الخطوات الوسيطة كسولة، والعناصر تمر واحدًا تلو الآخر، ويتوقف العمل بمجرد معرفة الجواب. ويُستخدم التدفق مرة واحدة فقط.',
        'Zwischenschritte sind faul. Elemente laufen einzeln durch, und die Arbeit endet, sobald die Antwort feststeht. Ein Stream ist nur einmal nutzbar.'),
    say('sources', 'Sources', 'Streams start from collections, arrays, ranges, single values, generators and files. Infinite streams need a limit.',
        'Streams collections, arrays, ranges, values, generators और files से शुरू होते हैं। Infinite streams को limit चाहिए।',
        'Streams collections, arrays, ranges, generators ಮತ್ತು files ನಿಂದ ಆರಂಭವಾಗುತ್ತವೆ. Infinite streams ಗೆ limit ಬೇಕು.',
        'Streams collections, arrays, ranges, generators ଓ files ରୁ ଆରମ୍ଭ ହୁଏ। Infinite streams କୁ limit ଦରକାର।',
        'تبدأ التدفقات من المجموعات والمصفوفات والنطاقات والمولدات والملفات، والتدفقات اللانهائية تحتاج حدًا.',
        'Streams starten aus Collections, Arrays, Bereichen, Generatoren und Dateien. Unendliche Streams brauchen ein limit.'),
    say('intermediate', 'Intermediate operations', 'filter keeps, map changes, flatMap flattens, distinct and sorted look at everything, and takeWhile stops at the first failure.',
        'filter रखता है, map बदलता है, flatMap समतल करता है, distinct और sorted सब देखते हैं, और takeWhile पहली विफलता पर रुकता है।',
        'filter ಉಳಿಸುತ್ತದೆ, map ಬದಲಿಸುತ್ತದೆ, flatMap ಚಪ್ಪಟೆ ಮಾಡುತ್ತದೆ, takeWhile ಮೊದಲ ವಿಫಲತೆಯಲ್ಲಿ ನಿಲ್ಲುತ್ತದೆ.',
        'filter ରଖେ, map ବଦଳାଏ, flatMap ସମତଳ କରେ, takeWhile ପ୍ରଥମ ବିଫଳତାରେ ଅଟକେ।',
        'يحتفظ filter ويغير map ويسطح flatMap، ويرى distinct وsorted كل شيء، ويتوقف takeWhile عند أول فشل.',
        'filter behält, map ändert, flatMap glättet, distinct und sorted sehen alles, takeWhile stoppt beim ersten Fehlschlag.'),
    say('terminal', 'Terminal operations', 'A terminal operation runs the pipeline and returns a result. toList gives an unmodifiable list.',
        'Terminal operation pipeline चलाता है और result देता है। toList एक ऐसी list देता है जिसे बदला नहीं जा सकता।',
        'Terminal operation pipeline ಓಡಿಸಿ result ಕೊಡುತ್ತದೆ. toList ಬದಲಿಸಲಾಗದ list ಕೊಡುತ್ತದೆ.',
        'Terminal operation pipeline ଚଲାଏ ଏବଂ result ଦିଏ। toList ବଦଳାଇ ନହେବା list ଦିଏ।',
        'تشغل العملية النهائية خط المعالجة وتعيد نتيجة، وتعطي toList قائمة غير قابلة للتعديل.',
        'Eine Endoperation führt die Pipeline aus und liefert ein Ergebnis. toList liefert eine unveränderliche Liste.'),
    say('collectors', 'Collectors', 'groupingBy counts per group, partitioningBy splits yes and no, joining makes text, toMap builds a lookup and teeing combines two answers.',
        'groupingBy हर group गिनता है, partitioningBy हाँ और ना में बाँटता है, joining text बनाता है, toMap lookup बनाता है और teeing दो जवाब जोड़ता है।',
        'groupingBy ಗುಂಪು ಎಣಿಸುತ್ತದೆ, partitioningBy ಹೌದು ಇಲ್ಲ ಎಂದು ವಿಭಜಿಸುತ್ತದೆ, joining text ಮಾಡುತ್ತದೆ, teeing ಎರಡು ಉತ್ತರ ಸೇರಿಸುತ್ತದೆ.',
        'groupingBy ଗୋଷ୍ଠୀ ଗଣେ, partitioningBy ହଁ ନା ଭାଗ କରେ, joining text କରେ, teeing ଦୁଇ ଉତ୍ତର ଯୋଡ଼େ।',
        'يعد groupingBy لكل مجموعة، ويقسم partitioningBy إلى نعم ولا، وينشئ joining نصًا، ويبني toMap جدول بحث، ويجمع teeing جوابين.',
        'groupingBy zählt pro Gruppe, partitioningBy teilt in ja und nein, joining baut Text, toMap eine Nachschlagetabelle, teeing kombiniert zwei Antworten.'),
    say('primitive', 'Primitive streams', 'IntStream, LongStream and DoubleStream work with plain numbers, avoid boxing and add sum, average and statistics.',
        'IntStream, LongStream और DoubleStream सादे numbers के साथ काम करते हैं, boxing से बचते हैं और sum, average देते हैं।',
        'IntStream, LongStream, DoubleStream ಸರಳ numbers ಜೊತೆ ಕೆಲಸ ಮಾಡಿ boxing ತಪ್ಪಿಸುತ್ತವೆ.',
        'IntStream, LongStream, DoubleStream ସାଧା numbers ସହ କାମ କରି boxing ଏଡ଼ାନ୍ତି।',
        'تعمل IntStream وLongStream وDoubleStream على أرقام عادية فتتجنب التغليف وتضيف المجموع والمتوسط والإحصاءات.',
        'IntStream, LongStream und DoubleStream arbeiten mit einfachen Zahlen, vermeiden Boxing und bieten sum, average und Statistiken.'),
    say('optional', 'Optional', 'Optional is a box with one value or nothing. Use orElseGet for expensive defaults, and never call get without checking.',
        'Optional एक box है जिसमें एक value है या कुछ नहीं। महँगे default के लिए orElseGet इस्तेमाल करें, और बिना जाँचे get न बुलाएँ।',
        'Optional ಒಂದು value ಅಥವಾ ಏನೂ ಇಲ್ಲದ box. ದುಬಾರಿ default ಗೆ orElseGet ಬಳಸಿ.',
        'Optional ଗୋଟିଏ value କିମ୍ବା କିଛି ନଥିବା box। ମହଙ୍ଗା default ପାଇଁ orElseGet ବ୍ୟବହାର କରନ୍ତୁ।',
        'Optional صندوق فيه قيمة واحدة أو لا شيء. استخدم orElseGet للقيم الافتراضية المكلفة، ولا تستدع get دون فحص.',
        'Optional ist eine Box mit einem Wert oder nichts. Nutze orElseGet für teure Standardwerte und rufe get nie ungeprüft auf.'),
    say('gatherers', 'Gatherers', 'Gatherers, final in Java 24, are custom intermediate operations. The JDK gives fixed and sliding windows, scan, fold and mapConcurrent.',
        'Gatherers, जो Java 24 में final हुए, custom intermediate operations हैं। JDK windows, scan, fold और mapConcurrent देता है।',
        'Java 24 ನಲ್ಲಿ final ಆದ Gatherers custom intermediate operations. JDK windows, scan, fold ಕೊಡುತ್ತದೆ.',
        'Java 24 ରେ final ହୋଇଥିବା Gatherers custom intermediate operations। JDK windows, scan, fold ଦିଏ।',
        'المجمّعات، النهائية في Java 24، عمليات وسيطة مخصصة، ويقدم JDK نوافذ ثابتة ومنزلقة وscan وfold وmapConcurrent.',
        'Gatherer, final seit Java 24, sind eigene Zwischenoperationen. Das JDK liefert feste und gleitende Fenster, scan, fold und mapConcurrent.'),
    say('parallel', 'Parallel streams', 'Parallel streams split pure calculation across cores. Never write to a shared list from a parallel stream.',
        'Parallel streams शुद्ध गणना को cores में बाँटते हैं। Parallel stream से कभी shared list में न लिखें।',
        'Parallel streams ಲೆಕ್ಕವನ್ನು cores ನಲ್ಲಿ ಹಂಚುತ್ತವೆ. Shared list ಗೆ ಎಂದಿಗೂ ಬರೆಯಬೇಡಿ.',
        'Parallel streams ଗଣନାକୁ cores ରେ ବାଣ୍ଟନ୍ତି। Shared list ରେ କେବେ ଲେଖନ୍ତୁ ନାହିଁ।',
        'توزع التدفقات المتوازية الحساب البحت على الأنوية، ولا تكتب أبدًا في قائمة مشتركة من تدفق متوازٍ.',
        'Parallele Streams verteilen reine Rechenarbeit auf Kerne. Schreibe nie aus einem parallelen Stream in eine gemeinsame Liste.'),
    say('scenario', 'Scenario', 'A few collectors turn three nightly runs into flaky tests, average times, the slowest runs and the pass rate.',
        'कुछ collectors तीन nightly runs से flaky tests, औसत समय, सबसे धीमे runs और pass rate निकालते हैं।',
        'ಕೆಲವು collectors ಮೂರು nightly runs ನಿಂದ flaky tests, ಸರಾಸರಿ ಸಮಯ ಮತ್ತು pass rate ತೆಗೆಯುತ್ತವೆ.',
        'କିଛି collectors ତିନି nightly runs ରୁ flaky tests, ହାରାହାରି ସମୟ ଓ pass rate ବାହାର କରନ୍ତି।',
        'تحول بضعة مجمِّعات ثلاث تشغيلات ليلية إلى اختبارات متقلبة ومتوسط الأزمنة وأبطأ التشغيلات ونسبة النجاح.',
        'Ein paar Collectors machen aus drei nächtlichen Läufen wacklige Tests, Durchschnittszeiten, die langsamsten Läufe und die Erfolgsquote.'),
]

QUIZ = [
    quiz('e', 'Which of these is a terminal operation?', ['count', 'filter', 'map', 'sorted'], 0, 'It gives a result, not a stream.', 'filter, map and sorted return streams. count returns a long and starts the work.'),
    quiz('e', 'What does this print?', ['[2, 4]', '[1, 3, 5]', '[4, 16]', '6'], 0, 'Keep the even numbers.', 'filter keeps 2 and 4.', code='System.out.println(Stream.of(1, 2, 3, 4, 5).filter(n -> n % 2 == 0).toList());', run=True),
    quiz('e', 'When does the code inside filter run?', ['When a terminal operation asks for elements', 'When filter is called', 'At compile time', 'Never'], 0, 'Lazy.', 'Intermediate operations only describe work.'),
    quiz('m', 'What does this print?', ['[a, b, c, d]', '[[a, b], [c, d]]', '[ab, cd]', '4'], 0, 'flatMap flattens.', 'Each inner list becomes elements of one stream.', code='System.out.println(List.of(List.of("a", "b"), List.of("c", "d")).stream().flatMap(List::stream).toList());', run=True),
    quiz('m', 'What does this print?', ['{false=[1, 3], true=[2, 4]}', '{true=[2, 4], false=[1, 3]}', '[[1, 3], [2, 4]]', '{1=odd}'], 0, 'partitioningBy always has two keys.', 'The map prints false first. Odd numbers go to false.', code='System.out.println(Stream.of(1, 2, 3, 4).collect(Collectors.partitioningBy(n -> n % 2 == 0)));', run=True),
    quiz('m', 'Why can <code>orElse(createUser())</code> be a bug?', ['createUser() runs even when a value is present', 'orElse does not exist', 'It returns null', 'It throws always'], 0, 'Arguments are evaluated first.', 'Java evaluates method arguments before the call. orElseGet takes a Supplier, so it can wait.'),
    quiz('m', 'What does this print?', ['[200, 201]', '[200, 201, 404, 200]', '[404, 200]', '[200, 201, 200]'], 0, 'takeWhile stops at the first failure.', 'It stops at 404 and never looks at the last 200. filter would keep that last 200 too.', code='System.out.println(Stream.of(200, 201, 404, 200).takeWhile(c -> c < 300).toList());', run=True),
    quiz('h', 'What happens when you call a terminal operation twice on the same stream?', ['IllegalStateException', 'It runs twice', 'The second call returns empty', 'Compile error'], 0, 'Streams are single use.', 'The message is "stream has already been operated upon or closed".'),
    quiz('h', 'What does this print?', ['[[1, 2], [3, 4], [5]]', '[[1, 2], [2, 3], [3, 4], [4, 5]]', '[1, 2, 3, 4, 5]', '[[1, 2, 3, 4, 5]]'], 0, 'windowFixed makes batches.', 'The last batch holds what is left.', code='System.out.println(Stream.of(1, 2, 3, 4, 5).gather(Gatherers.windowFixed(2)).toList());', run=True),
    quiz('h', 'Which collector would you use to get "pass rate" from two counts over the same list in one pass?', ['teeing', 'joining', 'toMap', 'flatMapping'], 0, 'Two collectors, one combine.', 'teeing feeds every element to two collectors and combines their results.'),
    quiz('x', 'Why is <code>parallel().forEach(list::add)</code> into an ArrayList wrong?', ['Several threads change one non thread safe list at once', 'parallel streams cannot call forEach', 'ArrayList cannot hold Integers', 'It sorts the list'], 0, 'Shared mutable state.', 'Updates are lost or an exception is thrown. collect and toList give each thread its own container.'),
    quiz('x', 'What does this print?', ['15', '10', '5', '120'], 0, 'reduce with an identity.', '0 + 1 + 2 + 3 + 4 + 5 = 15.', code='System.out.println(IntStream.rangeClosed(1, 5).reduce(0, (a, b) -> a + b));', run=True),
]

CALC = [
    calc('e', 'What does this print?', '3', 'Count the names with 4 letters.', ['asha, ravi and arun have 4 letters.', 'So 3.'], code='System.out.println(Stream.of("asha", "ravi", "meera", "arun").filter(n -> n.length() == 4).count());', run=True),
    calc('e', 'What does this print?', '55', 'Squares of 1 to 5.', ['<span class="eq">1 + 4 + 9 + 16 + 25 = 55</span>'], code='System.out.println(IntStream.rangeClosed(1, 5).map(i -> i * i).sum());', run=True),
    calc('m', 'What does this print?', '71.2', 'Average of the five marks.', ['<span class="eq">72 + 91 + 45 + 88 + 60 = 356</span>', '<span class="eq"><span class="fr"><i>356</i><i>5</i></span> = 71.2</span>'], code='System.out.println(IntStream.of(72, 91, 45, 88, 60).average().getAsDouble());', run=True),
    calc('m', 'The lazy example filters until findFirst succeeds. Names are asha, ravi, meera. asha has 4 letters. How many times does filter run?', '1', 'findFirst stops at the first match.', ['asha passes the filter immediately.', 'So filter runs once, then map once.']),
    calc('m', 'What does this print?', '[1, 3, 6, 10]', 'Running totals.', ['1', '<span class="eq">1 + 2 = 3</span>', '<span class="eq">3 + 3 = 6</span>', '<span class="eq">6 + 4 = 10</span>'], code='System.out.println(Stream.of(1, 2, 3, 4).gather(Gatherers.scan(() -> 0, Integer::sum)).toList());', run=True),
    calc('h', 'A suite has 12 runs and 9 passed. What pass rate does printf("%.1f") show?', '75.0', 'Pass ÷ total × 100.', ['<span class="eq"><span class="fr"><i>9</i><i>12</i></span> × 100 = 75.0</span>']),
    calc('h', 'What does this print?', '4', 'windowSliding(3) over 6 elements.', ['Windows start at positions 0, 1, 2 and 3.', '<span class="eq">6 − 3 + 1 = 4</span>'], code='System.out.println(Stream.of(1, 2, 3, 4, 5, 6).gather(Gatherers.windowSliding(3)).count());', run=True),
    calc('x', 'What does this print?', '{FAIL=2, PASS=3}', 'Count per status, sorted keys.', ['FAIL appears twice, PASS three times.', 'TreeMap sorts the keys.'], code='var s = List.of("PASS", "FAIL", "PASS", "PASS", "FAIL");\nvar counts = s.stream().collect(Collectors.groupingBy(String::toString, TreeMap::new, Collectors.counting()));\nSystem.out.println(counts);', run=True),
]

T = {
    'slug': 'java-streams', 'title': 'Streams, Collectors, Optional and Gatherers', 'short': 'Streams', 'emoji': '🌊', 'module': MODULE, 'minutes': 26,
    'lead': 'Streams let you describe what you want from a collection: keep these, change them to that, group by this, stop after three. This chapter covers lazy pipelines, every common operation, collectors for reports, primitive streams, Optional, the stream gatherers that became final in Java 24, and parallel streams with their traps.',
    'desc': 'Java Streams API from beginner to expert: pipelines, laziness, intermediate and terminal operations, Collectors groupingBy, partitioningBy, toMap, teeing, primitive streams, Optional, stream gatherers from Java 24, and parallel streams.',
    'summary': 'What a stream pipeline is, laziness and short circuits with an interactive pipeline, creating streams, intermediate and terminal operations, toList versus collect, collectors for grouping and summarising, primitive streams, Optional and its traps, stream gatherers (Java 24) including your own, parallel streams, and a nightly test report built with collectors.',
    'keywords': ['stream', 'Streams API', 'filter', 'map', 'flatMap', 'collect', 'Collectors', 'groupingBy', 'Optional', 'gatherers', 'parallel stream', 'IntStream', 'Java 8', 'Java 24'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
