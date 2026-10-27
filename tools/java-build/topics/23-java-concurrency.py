# Chapter 23: concurrency in depth: executors, futures, race conditions, locks, atomics, the memory model, concurrent collections,
# synchronizers, CompletableFuture, virtual threads, structured concurrency and scoped values.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

CODES = {
    'executor': j('''
import java.util.*;
import java.util.concurrent.*;

class Main {
    public static void main(String[] args) throws Exception {
        // try-with-resources (Java 19+): close() waits for every task, then shuts the pool down
        try (ExecutorService pool = Executors.newFixedThreadPool(3)) {
            Callable<String> login = () -> { Thread.sleep(200); return "login PASS"; };
            Callable<String> search = () -> { Thread.sleep(100); return "search PASS"; };
            Callable<String> cart = () -> { Thread.sleep(150); return "cart FAIL"; };

            Future<String> f = pool.submit(login);                 // one task, a result later
            System.out.println("submitted, done yet? " + f.isDone());
            System.out.println(f.get());                           // waits for the result

            for (Future<String> r : pool.invokeAll(List.of(search, cart))) {   // many tasks, wait for all
                System.out.println(r.get());
            }
        }
        System.out.println("pool closed");
    }
}
''', 'ExecutorService, Callable and Future', trace=False),
    'race': show('''
class Main {
    static int count = 0;
    public static void main(String[] args) throws Exception {
        Runnable work = () -> { for (int i = 0; i < 1_000_000; i++) count++; };
        Thread a = new Thread(work), b = new Thread(work);
        a.start(); b.start(); a.join(); b.join();
        System.out.println(count);       // expected 2000000
    }
}
''', 'A race condition: two threads, one counter', result='Prints a different number on almost every run, such as 1183342 or 1529871, and very rarely 2000000. <code>count++</code> is really three steps (read, add one, write), and two threads interleave them, so updates are lost. Because the result changes from run to run, it is not run on this page.'),
    'fixes': j('''
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.locks.*;

class Main {
    static int syncCount = 0;
    static synchronized void inc() { syncCount++; }

    public static void main(String[] args) throws Exception {
        AtomicInteger atomic = new AtomicInteger();
        LongAdder adder = new LongAdder();                  // fastest under heavy contention
        ReentrantLock lock = new ReentrantLock();
        int[] locked = {0};

        Runnable work = () -> {
            for (int i = 0; i < 1_000_000; i++) {
                inc();
                atomic.incrementAndGet();
                adder.increment();
                lock.lock();
                try { locked[0]++; } finally { lock.unlock(); }   // always unlock in finally
            }
        };
        try (var pool = Executors.newFixedThreadPool(4)) {
            for (int t = 0; t < 4; t++) pool.submit(work);
        }
        System.out.println("synchronized  " + syncCount);
        System.out.println("AtomicInteger " + atomic.get());
        System.out.println("LongAdder     " + adder.sum());
        System.out.println("ReentrantLock " + locked[0]);
    }
}
''', 'Four correct ways to count from many threads', trace=False),
    'trylock': j('''
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

class Main {
    public static void main(String[] args) throws Exception {
        ReentrantLock seat = new ReentrantLock();
        CountDownLatch held = new CountDownLatch(1);

        Thread booker = new Thread(() -> {
            seat.lock();
            try { held.countDown(); Thread.sleep(500); }      // holds the seat for half a second
            catch (InterruptedException e) { }
            finally { seat.unlock(); }
        });
        booker.start();
        held.await();

        // tryLock with a timeout: give up instead of waiting forever (one way to avoid deadlocks)
        if (seat.tryLock(100, TimeUnit.MILLISECONDS)) {
            try { System.out.println("got the seat"); } finally { seat.unlock(); }
        } else {
            System.out.println("seat busy, try another one");
        }
        booker.join();
        System.out.println("after the first booking: " + (seat.tryLock() ? "free" : "busy"));
    }
}
''', 'tryLock with a timeout', trace=False),
    'volatile': j('''
class Main {
    static volatile boolean running = true;     // without volatile the loop may never see the change

    public static void main(String[] args) throws Exception {
        Thread poller = new Thread(() -> {
            long checks = 0;
            while (running) checks++;
            System.out.println("poller saw the stop signal");
        });
        poller.start();
        Thread.sleep(200);
        running = false;                        // a write to a volatile happens-before every later read of it
        poller.join(2000);
        System.out.println("poller alive? " + poller.isAlive());
    }
}
''', 'volatile makes a change visible to other threads', trace=False),
    'chm': j('''
import java.util.*;
import java.util.concurrent.*;

class Main {
    public static void main(String[] args) throws Exception {
        ConcurrentHashMap<String, Integer> hits = new ConcurrentHashMap<>();
        List<String> log = List.of("/cart", "/login", "/cart", "/pay", "/cart", "/login");

        try (var pool = Executors.newFixedThreadPool(3)) {
            for (int round = 0; round < 1000; round++) {
                for (String path : log) pool.submit(() -> hits.merge(path, 1, Integer::sum));   // atomic read, add and write
            }
        }
        System.out.println(new TreeMap<>(hits));

        // check then act must be one atomic call, not get followed by put
        hits.computeIfAbsent("/search", p -> 0);
        hits.compute("/search", (p, n) -> n + 5);
        System.out.println("/search " + hits.get("/search"));

        CopyOnWriteArrayList<String> listeners = new CopyOnWriteArrayList<>(List.of("slack", "email"));
        for (String l : listeners) listeners.add("sms-" + l);    // safe: the loop reads a snapshot
        System.out.println(listeners);
    }
}
''', 'ConcurrentHashMap and CopyOnWriteArrayList', trace=False),
    'queue': j('''
import java.util.concurrent.*;

class Main {
    public static void main(String[] args) throws Exception {
        BlockingQueue<String> jobs = new ArrayBlockingQueue<>(2);    // a small queue: put waits when it is full
        String STOP = "STOP";

        Thread consumer = new Thread(() -> {
            try {
                while (true) {
                    String job = jobs.take();                          // waits when the queue is empty
                    if (job.equals(STOP)) break;
                    System.out.println("  processed " + job);
                }
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });
        consumer.start();
        for (String order : new String[]{"ORD-1", "ORD-2", "ORD-3", "ORD-4"}) {
            jobs.put(order);
        }
        jobs.put(STOP);                                               // a "poison pill" ends the consumer
        consumer.join();
        System.out.println("all orders processed");
    }
}
''', 'Producer and consumer with a BlockingQueue', trace=False),
    'sync-tools': j('''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

class Main {
    public static void main(String[] args) throws Exception {
        // CountDownLatch: wait until 3 services report ready
        CountDownLatch ready = new CountDownLatch(3);
        for (String s : List.of("db", "cache", "api")) {
            new Thread(() -> { sleep(100); ready.countDown(); }).start();
        }
        ready.await();
        System.out.println("all 3 services ready, start the tests");

        // Semaphore: at most 2 calls at the same time, like a rate limit on a test account
        Semaphore permits = new Semaphore(2);
        AtomicInteger now = new AtomicInteger(), peak = new AtomicInteger();
        try (var pool = Executors.newFixedThreadPool(6)) {
            for (int i = 0; i < 6; i++) pool.submit(() -> {
                permits.acquireUninterruptibly();
                try { peak.accumulateAndGet(now.incrementAndGet(), Math::max); sleep(100); now.decrementAndGet(); }
                finally { permits.release(); }
            });
        }
        System.out.println("6 calls made, never more than " + peak.get() + " at once");
    }

    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } }
}
''', 'CountDownLatch and Semaphore', trace=False),
    'cf': j('''
import java.util.concurrent.*;

class Main {
    static String call(String what, long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { throw new RuntimeException(e); }
        return what;
    }

    public static void main(String[] args) {
        long t0 = System.currentTimeMillis();
        String a = call("price", 400), b = call("stock", 600), c = call("reviews", 300);
        System.out.println("one after another: " + a + ", " + b + ", " + c + " in about " + round(t0) + " ms");

        t0 = System.currentTimeMillis();
        var price = CompletableFuture.supplyAsync(() -> call("price", 400));
        var stock = CompletableFuture.supplyAsync(() -> call("stock", 600));
        var reviews = CompletableFuture.supplyAsync(() -> call("reviews", 300));
        String page = CompletableFuture.allOf(price, stock, reviews)
            .thenApply(v -> price.join() + ", " + stock.join() + ", " + reviews.join())
            .join();
        System.out.println("in parallel:       " + page + " in about " + round(t0) + " ms");

        String combined = price.thenCombine(stock, (p, s) -> p + "+" + s).thenApply(String::toUpperCase).join();
        System.out.println(combined);
    }

    static long round(long t0) { return Math.round((System.currentTimeMillis() - t0) / 100.0) * 100; }
}
''', 'CompletableFuture: run calls in parallel and combine them', trace=False),
    'cf-errors': j('''
import java.util.concurrent.*;

class Main {
    public static void main(String[] args) {
        CompletableFuture<Integer> broken = CompletableFuture.supplyAsync(() -> {
            if (true) throw new IllegalStateException("inventory service down");
            return 5;
        });
        System.out.println(broken.exceptionally(e -> {                       // a fallback value
            System.out.println("recovered from: " + e.getCause().getMessage());
            return 0;
        }).join());

        System.out.println(broken.handle((v, e) -> e == null ? "ok " + v : "failed").join());   // sees both

        CompletableFuture<String> slow = CompletableFuture.supplyAsync(() -> {
            try { Thread.sleep(2000); } catch (InterruptedException e) { }
            return "late answer";
        });
        System.out.println(slow.completeOnTimeout("cached answer", 200, TimeUnit.MILLISECONDS).join());  // Java 9
        try {
            CompletableFuture.supplyAsync(() -> { try { Thread.sleep(2000); } catch (InterruptedException e) { } return 1; })
                .orTimeout(200, TimeUnit.MILLISECONDS).join();
        } catch (CompletionException e) {
            System.out.println("orTimeout: " + e.getCause().getClass().getSimpleName());
        }
    }
}
''', 'Errors and timeouts: exceptionally, handle, completeOnTimeout and orTimeout', trace=False),
    'virtual': j('''
import java.util.concurrent.*;
import java.util.stream.*;

class Main {
    public static void main(String[] args) throws Exception {
        Thread v = Thread.ofVirtual().name("checker").start(() -> System.out.println("virtual? " + Thread.currentThread().isVirtual()));
        v.join();

        long t0 = System.currentTimeMillis();
        try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {        // one new virtual thread per task
            IntStream.range(0, 10_000).forEach(i -> exec.submit(() -> {
                Thread.sleep(1000);                                            // blocking I/O stand-in
                return i;
            }));
        }
        long secs = Math.round((System.currentTimeMillis() - t0) / 1000.0);
        System.out.println("10000 tasks that each wait 1 s finished in about " + secs + " s");

        t0 = System.currentTimeMillis();
        try (var exec = Executors.newFixedThreadPool(100)) {                  // the classic way: a pool of 100
            IntStream.range(0, 1_000).forEach(i -> exec.submit(() -> { Thread.sleep(1000); return i; }));
        }
        secs = Math.round((System.currentTimeMillis() - t0) / 1000.0);
        System.out.println("1000 tasks on 100 platform threads took about " + secs + " s");
    }
}
''', 'Virtual threads: ten thousand blocking tasks at once', trace=False),
    'structured': j('''
import java.util.concurrent.*;
import java.util.concurrent.StructuredTaskScope.*;

void main() throws Exception {
    // Java 27 preview (JEP 533): subtasks live and die together, like the lines of a method
    try (var scope = StructuredTaskScope.open()) {
        Subtask<String> user = scope.fork(() -> { Thread.sleep(200); return "Asha"; });
        Subtask<Integer> cart = scope.fork(() -> { Thread.sleep(300); return 3; });
        scope.join();                                   // waits for both, fails if either fails
        IO.println(user.get() + " has " + cart.get() + " items in the cart");
    }

    try (var scope = StructuredTaskScope.open()) {
        Subtask<String> ok = scope.fork(() -> { Thread.sleep(2000); return "slow but fine"; });
        Subtask<String> bad = scope.fork(() -> { Thread.sleep(100); throw new IllegalStateException("payment service down"); });
        scope.join();
    } catch (ExecutionException e) {                   // Java 27: join throws ExecutionException
        IO.println("failed fast: " + e.getCause().getMessage() + ", and the slow sibling was cancelled");
    }

    // A different joiner: the first successful answer wins, like asking two mirrors
    try (var scope = StructuredTaskScope.open(Joiner.<String>anySuccessfulOrThrow())) {
        scope.fork(() -> { Thread.sleep(500); return "mirror-eu"; });
        scope.fork(() -> { Thread.sleep(100); return "mirror-in"; });
        IO.println("fastest mirror: " + scope.join());
    }
}
''', 'Structured concurrency (preview in Java 27)', jdk=27, preview=True, trace=False),
    'scoped': j('''
import java.util.concurrent.*;

class Main {
    // Java 25: a scoped value is set for one block of code and every method it calls, then it is gone
    static final ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();

    static void log(String msg) {
        System.out.println("[" + (REQUEST_ID.isBound() ? REQUEST_ID.get() : "no-request") + "] " + msg);
    }
    static void loadCart() { log("loading cart"); }
    static void pay() { log("charging card"); }

    public static void main(String[] args) {
        ScopedValue.where(REQUEST_ID, "req-7f3a").run(() -> {
            log("checkout started");
            loadCart();                                   // no need to pass the id down every method
            ScopedValue.where(REQUEST_ID, "req-7f3a/retry").run(Main::pay);   // rebound for an inner block only
            log("checkout done");
        });
        log("outside any request");
    }
}
''', 'Scoped values instead of ThreadLocal (final in Java 25)'),
    'scenario': j('''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

class Main {
    record Check(String endpoint, int status, long ms) {}

    // Stand in for an HTTP call: the result depends only on the endpoint, so the report is the same every run
    static Check probe(String endpoint) throws InterruptedException {
        int n = Math.abs(endpoint.hashCode());
        long ms = 100 + n % 400;
        Thread.sleep(ms);
        int status = n % 17 == 0 ? 503 : n % 11 == 0 ? 404 : 200;
        return new Check(endpoint, status, ms);
    }

    public static void main(String[] args) throws Exception {
        List<String> endpoints = new ArrayList<>();
        for (int i = 1; i <= 300; i++) endpoints.add("/api/v1/products/" + i);

        Semaphore limit = new Semaphore(50);                      // be kind to the server: 50 at a time
        Map<Integer, AtomicInteger> byStatus = new ConcurrentSkipListMap<>();
        Queue<Check> failures = new ConcurrentLinkedQueue<>();
        long t0 = System.currentTimeMillis();

        try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
            for (String e : endpoints) exec.submit(() -> {
                limit.acquire();
                try {
                    Check c = probe(e);
                    byStatus.computeIfAbsent(c.status(), s -> new AtomicInteger()).incrementAndGet();
                    if (c.status() != 200) failures.add(c);
                } finally { limit.release(); }
                return null;
            });
        }
        long secs = Math.round((System.currentTimeMillis() - t0) / 1000.0);
        System.out.println("checked " + endpoints.size() + " endpoints in about " + secs + " s");
        System.out.println("by status: " + byStatus);
        failures.stream().sorted(Comparator.comparing(Check::endpoint)).limit(3)
            .forEach(c -> System.out.println("  " + c.status() + " " + c.endpoint()));
    }
}
''', 'Real world: a smoke test of 300 endpoints on virtual threads', trace=False),
}

DG = {
    'vt': {'t': 'How virtual threads share a few carrier threads', 'w': 900, 'h': 300, 'mw': 640,
        'g': [[20, 20, 400, 260, 'Virtual threads (millions are fine)', 1], [480, 20, 400, 260, 'Carrier threads (one per CPU core)', 2]],
        'n': [['v1', 50, 60, 150, 44, 'task 1', {'c': 1}], ['v2', 240, 60, 150, 44, 'task 2', {'c': 1}],
              ['v3', 50, 140, 150, 44, 'task 3', {'c': 1}], ['v4', 240, 140, 150, 44, 'task 4', {'c': 1}],
              ['park', 120, 215, 200, 44, 'waiting for I/O', {'c': 5, 'sub': 'stack saved on the heap'}],
              ['c1', 560, 70, 240, 54, 'carrier 1', {'c': 2}], ['c2', 560, 170, 240, 54, 'carrier 2', {'c': 2}]],
        'e': [['v1', 'c1', {'t': 'mounted', 'id': 'm1'}], ['v2', 'c2', {'t': 'mounted', 'id': 'm2'}], ['v1', 'park', {'t': 'blocks', 'id': 'p1'}],
              ['v3', 'c1', {'t': 'mounted', 'id': 'm3'}], ['park', 'c2', {'t': 'resumes later', 'id': 'r1', 'd': 1}]],
        'st': [[['v1', 'v2', 'c1', 'c2', 'm1', 'm2'], 'Tasks 1 and 2 are mounted on the two carrier threads and run Java code.'],
               [['v1', 'park', 'p1'], 'Task 1 calls a blocking method, such as reading a socket. Instead of blocking the carrier, the JVM saves its stack on the heap and unmounts it.'],
               [['v3', 'c1', 'm3'], 'Carrier 1 is free right away, so task 3 is mounted on it. No CPU time is wasted waiting.'],
               [['park', 'c2', 'r1'], 'When the I/O answer arrives, task 1 is mounted again, on whichever carrier is free, and continues from the same line.'],
               [['v4'], 'This is why thousands of waiting tasks need only a handful of real threads. Pure calculation still needs real cores.']]},
}

PARTS = [
    part('executors', '🏭', 'Executors: tasks instead of threads', '''
<p>The multithreading chapter created threads by hand. Real programs rarely do that. They hand <b>tasks</b> to an <b>ExecutorService</b>, which owns a pool of threads and reuses them, the way a restaurant gives orders to a fixed team of cooks instead of hiring a cook per order.</p>
[[executor]]
<div class="tw"><table class="jt"><tr><th>Factory</th><th>Gives</th></tr>
<tr><td><code>newFixedThreadPool(n)</code></td><td>n threads, extra tasks wait in a queue</td></tr>
<tr><td><code>newCachedThreadPool()</code></td><td>creates threads as needed, reuses idle ones</td></tr>
<tr><td><code>newScheduledThreadPool(n)</code></td><td>run later or every few seconds</td></tr>
<tr><td><code>newVirtualThreadPerTaskExecutor()</code></td><td>Java 21: a new virtual thread for every task</td></tr></table></div>
<div class="note">A <code>Callable</code> returns a value and may throw. A <code>Runnable</code> does neither. <code>Future.get()</code> waits for the value, so call it as late as possible.</div>
''', kw=['ExecutorService', 'Executors', 'thread pool', 'Callable', 'Future', 'submit', 'invokeAll', 'shutdown', 'awaitTermination', 'AutoCloseable executor', 'newFixedThreadPool']),
    part('race', '🏁', 'Race conditions and four fixes', '''
<p>When two threads change the same data without coordination, the result depends on timing. That is a <b>race condition</b>. It is the most common reason for a test that fails "only sometimes on CI".</p>
[[race]]
<p>The fixes all make the read, change and write happen as one unit that other threads cannot split.</p>
[[fixes]]
<div class="tw"><table class="jt"><tr><th>Tool</th><th>Use it when</th></tr>
<tr><td><code>synchronized</code></td><td>simple, short critical sections</td></tr>
<tr><td><code>AtomicInteger</code> <code>AtomicReference</code></td><td>one variable, lock free, uses compare and swap (CAS)</td></tr>
<tr><td><code>LongAdder</code></td><td>counters hit by many threads, such as metrics</td></tr>
<tr><td><code>ReentrantLock</code></td><td>you need tryLock, timeouts, fairness or several conditions</td></tr></table></div>
[[trylock]]
''', kw=['race condition', 'lost update', 'count++ not atomic', 'synchronized', 'AtomicInteger', 'compare and swap', 'CAS', 'LongAdder', 'ReentrantLock', 'tryLock', 'deadlock avoidance', 'ReadWriteLock']),
    part('memory-model', '👁️', 'Visibility and the Java memory model', '''
<p>Each CPU core keeps its own cache, and the compiler may reorder instructions. So a value written by one thread is not guaranteed to be seen by another, unless there is a <b>happens-before</b> relationship between them. The Java Memory Model (JSR 133) defines those relationships.</p>
[[volatile]]
<div class="tw"><table class="jt"><tr><th>These create happens-before</th></tr>
<tr><td>Unlocking a monitor or lock, then locking the same one</td></tr>
<tr><td>Writing a <code>volatile</code> field, then reading it</td></tr>
<tr><td><code>Thread.start()</code>, and everything a thread did before another thread's <code>join()</code> returns</td></tr>
<tr><td>Putting into a concurrent collection, then taking it out</td></tr></table></div>
<div class="warn"><code>volatile</code> fixes <b>visibility</b>, not <b>atomicity</b>. <code>volatileCount++</code> still loses updates.</div>
''', kw=['Java memory model', 'JMM', 'happens-before', 'volatile', 'visibility', 'CPU cache', 'reordering', 'atomicity', 'JSR 133']),
    part('collections', '🗄️', 'Concurrent collections', '''
<p>A normal HashMap shared by threads can lose entries or, in old Java versions, even loop forever. The <code>java.util.concurrent</code> collections are built for sharing.</p>
[[chm]]
<div class="tip">The bug to look for in code reviews is "check then act": <code>if (!map.containsKey(k)) map.put(k, v)</code>. Between the check and the put, another thread can get in. Use <code>putIfAbsent</code>, <code>computeIfAbsent</code> or <code>merge</code>, which do both in one atomic step.</div>
<p>A <b>BlockingQueue</b> connects producers and consumers. <code>put</code> waits when the queue is full and <code>take</code> waits when it is empty, so a fast producer cannot flood a slow consumer.</p>
[[queue]]
''', kw=['ConcurrentHashMap', 'merge', 'compute', 'computeIfAbsent', 'check then act', 'CopyOnWriteArrayList', 'BlockingQueue', 'ArrayBlockingQueue', 'producer consumer', 'poison pill', 'ConcurrentLinkedQueue']),
    part('synchronizers', '🚦', 'Synchronizers: latches and semaphores', '''
<p>Synchronizers coordinate threads. A <b>CountDownLatch</b> lets threads wait until a count reaches zero, such as "start the tests when the database, cache and API are ready". A <b>Semaphore</b> hands out a fixed number of permits, which is a simple way to limit how many calls hit a server at once.</p>
[[sync-tools]]
<div class="note">Also in the toolbox: <code>CyclicBarrier</code> (wait for each other, then all continue, and reuse it), <code>Phaser</code> (a flexible barrier with phases) and <code>Exchanger</code> (two threads swap objects).</div>
''', kw=['CountDownLatch', 'Semaphore', 'permits', 'rate limit', 'CyclicBarrier', 'Phaser', 'Exchanger', 'synchronizer']),
    part('completable', '🔮', 'CompletableFuture', '''
<p><code>Future.get()</code> blocks. <b>CompletableFuture</b> (Java 8) lets you describe what to do <b>when</b> the result arrives: transform it, combine it with another, or recover from an error, without blocking a thread while you wait.</p>
[[cf]]
<div class="viz" data-viz="jcf"></div>
[[cf-errors]]
<div class="tw"><table class="jt"><tr><th>Method</th><th>Meaning</th></tr>
<tr><td><code>supplyAsync</code> <code>runAsync</code></td><td>start work on another thread</td></tr>
<tr><td><code>thenApply</code> <code>thenCompose</code></td><td>transform the value, or chain another async call</td></tr>
<tr><td><code>thenCombine</code> <code>allOf</code> <code>anyOf</code></td><td>join two, all or the first of several</td></tr>
<tr><td><code>exceptionally</code> <code>handle</code> <code>whenComplete</code></td><td>recover, see value and error, or just log</td></tr>
<tr><td><code>orTimeout</code> <code>completeOnTimeout</code></td><td>Java 9: fail or use a default when too slow</td></tr></table></div>
''', kw=['CompletableFuture', 'supplyAsync', 'thenApply', 'thenCompose', 'thenCombine', 'allOf', 'anyOf', 'exceptionally', 'handle', 'orTimeout', 'completeOnTimeout', 'CompletionException', 'async']),
    part('virtual', '🪶', 'Virtual threads (Java 21)', '''
<p>A normal (platform) thread is a real operating system thread with about a megabyte of stack, so a server can afford a few thousand. A <b>virtual thread</b> (JEP 444, final in Java 21) is managed by the JVM and costs a few hundred bytes when idle, so millions are fine. When a virtual thread blocks on I/O, the JVM parks it and gives its carrier thread to someone else.</p>
<div class="viz" data-viz="flow" data-k="vt"></div>
[[virtual]]
<div class="viz" data-viz="jvthreads"></div>
<div class="tip">Rules for virtual threads: create one per task and never pool them, keep using plain blocking code (no callbacks needed), limit access to scarce resources with a Semaphore instead of a small pool, and do not expect speed ups for pure calculation. Since Java 24 (JEP 491), <code>synchronized</code> blocks no longer pin a virtual thread to its carrier.</div>
''', kw=['virtual thread', 'Project Loom', 'JEP 444', 'carrier thread', 'platform thread', 'newVirtualThreadPerTaskExecutor', 'Thread.ofVirtual', 'pinning', 'JEP 491', 'mount', 'unmount', 'blocking I/O']),
    part('structured', '🌳', 'Structured concurrency and scoped values', '''
<p><b>Structured concurrency</b> treats a group of subtasks as one unit: they start inside a block, and the block does not end until all of them are done. If one fails, the others are cancelled. No thread is left running in the background by accident. It is still a preview (JEP 533, seventh preview in Java 27), with a new API since Java 25. In Java 27 <code>join()</code> reports a failed subtask with the familiar <code>ExecutionException</code>, and the joiner that returns the first good answer is called <code>anySuccessfulOrThrow</code>.</p>
[[structured]]
<p><b>Scoped values</b> (JEP 506, final in Java 25) share a value, such as a request id or the current user, with every method called inside a block, without passing it as a parameter. Unlike <code>ThreadLocal</code>, the value cannot be changed by callees, it disappears when the block ends, and it is cheap to share with millions of virtual threads.</p>
[[scoped]]
''', kw=['structured concurrency', 'StructuredTaskScope', 'fork', 'join', 'Joiner', 'anySuccessfulOrThrow', 'ExecutionException', 'JEP 533', 'scoped value', 'ScopedValue', 'JEP 506', 'ThreadLocal', 'request id', 'cancellation']),
    part('scenario', '🎬', 'Real world scenario: a fast smoke test', '''
<div class="scenario"><b>The situation</b>After every deployment, a team checks 300 product endpoints. Done one after another, it takes over a minute. A pool of 10 threads still takes about 10 seconds, and nobody wants to tune pool sizes.</div>
[[scenario]]
<p>Each endpoint gets its own virtual thread, a Semaphore keeps the load at 50 calls at a time, and the results go into concurrent collections. The code reads like a simple loop, finishes in a few seconds, and the report is sorted so it is the same on every run.</p>
''', kw=['smoke test', 'virtual threads', 'Semaphore', 'ConcurrentSkipListMap', 'parallel API checks', 'deployment check']),
]

INFO = {'title': 'Many cooks, one kitchen', 'panels': [
    panel([['e', '🏭'], ['t', 'pool.submit(task)', {'b': 1}]], 'Executors', 'Hand over tasks, not threads.', 'A pool reuses a fixed team of threads.'),
    panel([['e', '🏁'], ['t', 'count++  // 3 steps', {'b': 1}]], 'Races', 'Unsynchronised updates get lost.', 'Atomics, locks or synchronized fix it.'),
    panel([['e', '🔮'], ['t', 'allOf(a, b, c).join()', {'b': 1}]], 'CompletableFuture', 'Wait for the slowest, not the sum.', 'Recover with exceptionally, limit with orTimeout.'),
    panel([['e', '🪶'], ['t', 'newVirtualThreadPerTaskExecutor()', {'b': 1, 'size': 10}]], 'Virtual threads', 'A thread per task again.', 'Blocking is cheap, so simple code scales.')],
    'remember': 'Use executors for tasks, atomics or locks for shared counters, concurrent collections instead of synchronised maps, CompletableFuture to combine async results, and virtual threads for lots of waiting.'}

REAL = [
    ['🎟️', 'A ticket booking site', 'Uses <code>tryLock</code> with a short timeout on each seat, so two people clicking the same seat never both get it and nobody waits forever.'],
    ['🛍️', 'A product page', 'Fetches price, stock and reviews with three CompletableFutures, so the page waits 600 ms for the slowest instead of 1300 ms for all three.'],
    ['🧪', 'A test platform', 'Moved its API test runner to virtual threads and went from 200 to 5000 concurrent simulated users on the same machine.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to concurrency in depth: executors, race conditions, locks, the memory model, concurrent collections, CompletableFuture, virtual threads and structured concurrency.',
        'Concurrency की गहराई में स्वागत है: executors, race conditions, locks, memory model, concurrent collections, CompletableFuture, virtual threads और structured concurrency।',
        'Concurrency ಆಳಕ್ಕೆ ಸ್ವಾಗತ: executors, race conditions, locks, memory model, CompletableFuture, virtual threads.',
        'Concurrency ଗଭୀରତାକୁ ସ୍ୱାଗତ: executors, race conditions, locks, memory model, CompletableFuture, virtual threads।',
        'مرحبًا بك في التزامن بعمق: المنفذون، وحالات السباق، والأقفال، ونموذج الذاكرة، والمجموعات المتزامنة، وCompletableFuture، والخيوط الافتراضية.',
        'Willkommen zur Nebenläufigkeit im Detail: Executors, Race Conditions, Locks, Speichermodell, Concurrent Collections, CompletableFuture und virtuelle Threads.'),
    say('executors', 'Executors', 'Hand tasks to an ExecutorService that owns a pool of threads. Callable returns a value, and Future gets it later.',
        'Tasks को ExecutorService को दें जिसके पास threads का pool है। Callable value लौटाता है, और Future उसे बाद में देता है।',
        'Tasks ಅನ್ನು threads pool ಇರುವ ExecutorService ಗೆ ಕೊಡಿ. Callable value ಕೊಡುತ್ತದೆ, Future ನಂತರ ಪಡೆಯುತ್ತದೆ.',
        'Tasks କୁ threads pool ଥିବା ExecutorService କୁ ଦିଅନ୍ତୁ। Callable value ଦିଏ, Future ପରେ ପାଏ।',
        'سلّم المهام إلى ExecutorService الذي يملك مجموعة خيوط. Callable يعيد قيمة، وFuture يحصل عليها لاحقًا.',
        'Gib Aufgaben an einen ExecutorService mit Thread-Pool. Callable liefert einen Wert, Future holt ihn später.'),
    say('race', 'Race conditions', 'count plus plus is three steps, so two threads lose updates. synchronized, atomics, LongAdder or a lock make it safe.',
        'count plus plus तीन कदम है, इसलिए दो threads updates खो देते हैं। synchronized, atomics, LongAdder या lock इसे सुरक्षित बनाते हैं।',
        'count plus plus ಮೂರು ಹಂತ, ಆದ್ದರಿಂದ updates ಕಳೆಯುತ್ತವೆ. synchronized, atomics ಅಥವಾ lock ಸುರಕ್ಷಿತಗೊಳಿಸುತ್ತವೆ.',
        'count plus plus ତିନି ପଦକ୍ଷେପ, ତେଣୁ updates ହଜେ। synchronized, atomics କିମ୍ବା lock ସୁରକ୍ଷିତ କରେ।',
        'زيادة العداد ثلاث خطوات، فيضيع خيطان بعض التحديثات. synchronized أو الذريات أو LongAdder أو القفل تجعلها آمنة.',
        'count++ sind drei Schritte, daher gehen Updates verloren. synchronized, Atomics, LongAdder oder ein Lock machen es sicher.'),
    say('memory-model', 'Memory model', 'A write is only guaranteed visible to another thread through happens-before, such as a lock or a volatile field. volatile does not make plus plus atomic.',
        'एक write दूसरे thread को happens-before से ही दिखता है, जैसे lock या volatile field। volatile plus plus को atomic नहीं बनाता।',
        'Write ಇನ್ನೊಂದು thread ಗೆ happens-before ಮೂಲಕ ಮಾತ್ರ ಕಾಣುತ್ತದೆ. volatile atomic ಅಲ್ಲ.',
        'Write ଅନ୍ୟ thread କୁ happens-before ଦ୍ୱାରା ହିଁ ଦେଖାଯାଏ। volatile atomic ନୁହେଁ।',
        'الكتابة تظهر لخيط آخر فقط عبر علاقة happens-before مثل قفل أو حقل volatile، وvolatile لا يجعل الزيادة ذرية.',
        'Ein Schreibzugriff ist nur über happens-before sichtbar, etwa Lock oder volatile. volatile macht ++ nicht atomar.'),
    say('collections', 'Concurrent collections', 'Use ConcurrentHashMap with merge or compute, avoid check then act, and connect producers and consumers with a BlockingQueue.',
        'ConcurrentHashMap को merge या compute के साथ इस्तेमाल करें, check then act से बचें, और BlockingQueue से producers और consumers जोड़ें।',
        'ConcurrentHashMap merge ಅಥವಾ compute ಜೊತೆ ಬಳಸಿ, BlockingQueue ಮೂಲಕ producer consumer ಸಂಪರ್ಕಿಸಿ.',
        'ConcurrentHashMap merge କିମ୍ବା compute ସହ, BlockingQueue ଦ୍ୱାରା producer consumer ଯୋଡ଼ନ୍ତୁ।',
        'استخدم ConcurrentHashMap مع merge أو compute، وتجنب الفحص ثم التنفيذ، واربط المنتجين والمستهلكين بطابور BlockingQueue.',
        'Nutze ConcurrentHashMap mit merge oder compute, vermeide Prüfen-dann-Handeln und verbinde Erzeuger und Verbraucher mit einer BlockingQueue.'),
    say('synchronizers', 'Synchronizers', 'A CountDownLatch waits for a count to reach zero. A Semaphore limits how many threads do something at once.',
        'CountDownLatch count के शून्य होने का इंतज़ार करता है। Semaphore सीमित करता है कि एक साथ कितने threads काम करें।',
        'CountDownLatch count ಶೂನ್ಯವಾಗುವವರೆಗೆ ಕಾಯುತ್ತದೆ. Semaphore ಒಮ್ಮೆಗೆ ಎಷ್ಟು threads ಎಂದು ಮಿತಿಗೊಳಿಸುತ್ತದೆ.',
        'CountDownLatch count ଶୂନ ହେବା ପର୍ଯ୍ୟନ୍ତ ଅପେକ୍ଷା କରେ। Semaphore ଏକାଥରେ କେତେ threads ସୀମିତ କରେ।',
        'ينتظر CountDownLatch حتى يصل العد إلى صفر، ويحدد Semaphore عدد الخيوط التي تعمل في الوقت نفسه.',
        'Ein CountDownLatch wartet, bis der Zähler null ist. Ein Semaphore begrenzt, wie viele Threads gleichzeitig arbeiten.'),
    say('completable', 'CompletableFuture', 'CompletableFuture runs calls in parallel and combines them. The total time is the slowest call, not the sum. Recover with exceptionally and limit with orTimeout.',
        'CompletableFuture calls को parallel चलाकर जोड़ता है। कुल समय सबसे धीमे call का होता है, जोड़ नहीं। exceptionally से संभलें और orTimeout से सीमा लगाएँ।',
        'CompletableFuture calls ಸಮಾಂತರವಾಗಿ ಓಡಿಸಿ ಸೇರಿಸುತ್ತದೆ. ಒಟ್ಟು ಸಮಯ ನಿಧಾನದ call.',
        'CompletableFuture calls ସମାନ୍ତରାଳରେ ଚଲାଇ ଯୋଡ଼େ। ମୋଟ ସମୟ ସବୁଠୁ ଧୀର call।',
        'يشغل CompletableFuture الاستدعاءات بالتوازي ويجمعها، فيكون الزمن الكلي زمن أبطأ استدعاء لا مجموعها.',
        'CompletableFuture führt Aufrufe parallel aus und kombiniert sie. Die Gesamtzeit ist der langsamste Aufruf, nicht die Summe.'),
    say('virtual', 'Virtual threads', 'Virtual threads are cheap. When one blocks on I/O, it is parked and its carrier thread runs another task, so thousands of waiting tasks are fine.',
        'Virtual threads सस्ते हैं। जब कोई I/O पर रुकता है, उसे park किया जाता है और carrier thread दूसरा task चलाता है।',
        'Virtual threads ಅಗ್ಗ. I/O ನಲ್ಲಿ ತಡೆದಾಗ park ಆಗಿ carrier ಬೇರೆ task ಓಡಿಸುತ್ತದೆ.',
        'Virtual threads ଶସ୍ତା। I/O ରେ ଅଟକିଲେ park ହୁଏ ଏବଂ carrier ଅନ୍ୟ task ଚଲାଏ।',
        'الخيوط الافتراضية رخيصة، فعندما يتوقف أحدها على الإدخال والإخراج يُركن ويشغل الخيط الحامل مهمة أخرى.',
        'Virtuelle Threads sind günstig. Blockiert einer bei I/O, wird er geparkt und der Träger-Thread führt eine andere Aufgabe aus.'),
    say('structured', 'Structured concurrency', 'Structured concurrency keeps subtasks inside one block and cancels the rest when one fails. Scoped values share a request id without ThreadLocal.',
        'Structured concurrency subtasks को एक block में रखता है और एक fail होने पर बाकी cancel करता है। Scoped values ThreadLocal के बिना request id बाँटते हैं।',
        'Structured concurrency subtasks ಒಂದೇ block ನಲ್ಲಿ ಇಡುತ್ತದೆ. Scoped values request id ಹಂಚುತ್ತವೆ.',
        'Structured concurrency subtasks କୁ ଗୋଟିଏ block ରେ ରଖେ। Scoped values request id ବାଣ୍ଟନ୍ତି।',
        'يبقي التزامن المنظم المهام الفرعية داخل كتلة واحدة ويلغي البقية عند فشل إحداها، وتشارك القيم المحددة النطاق معرّف الطلب دون ThreadLocal.',
        'Strukturierte Nebenläufigkeit hält Teilaufgaben in einem Block und bricht den Rest ab, wenn eine scheitert. Scoped Values teilen eine Request-ID ohne ThreadLocal.'),
    say('scenario', 'Scenario', 'Three hundred endpoints are checked on virtual threads, fifty at a time, and the results are collected in concurrent collections.',
        'तीन सौ endpoints virtual threads पर, पचास एक साथ, जाँचे जाते हैं और परिणाम concurrent collections में जमा होते हैं।',
        'ಮುನ್ನೂರು endpoints virtual threads ನಲ್ಲಿ ಐವತ್ತು ಒಮ್ಮೆಗೆ ಪರೀಕ್ಷಿಸಲಾಗುತ್ತದೆ.',
        'ତିନି ଶହ endpoints virtual threads ରେ ପଚାଶ ଏକାଥରେ ଯାଞ୍ଚ ହୁଏ।',
        'تُفحص ثلاثمئة نقطة نهاية على خيوط افتراضية، خمسون في كل مرة، وتُجمع النتائج في مجموعات متزامنة.',
        'Dreihundert Endpunkte werden auf virtuellen Threads geprüft, fünfzig gleichzeitig, und die Ergebnisse landen in Concurrent Collections.'),
]

QUIZ = [
    quiz('e', 'What does a Callable have that a Runnable does not?', ['A return value and the right to throw checked exceptions', 'A name', 'A priority', 'A thread of its own'], 0, 'call() versus run().', 'Callable&lt;V&gt; has V call() throws Exception.'),
    quiz('e', 'Why is <code>count++</code> not safe from two threads?', ['It is a read, an add and a write that threads can interleave', 'int is too small', 'Threads cannot see static fields', 'It always throws'], 0, 'Three steps.', 'Two threads can read the same old value and both write the same new value.'),
    quiz('e', 'Which executor gives each task a new virtual thread?', ['newVirtualThreadPerTaskExecutor', 'newFixedThreadPool', 'newCachedThreadPool', 'newSingleThreadExecutor'], 0, 'Java 21.', 'Virtual threads are never pooled, so one per task is the right design.'),
    quiz('m', 'What does <code>volatile</code> guarantee?', ['Visibility of writes to other threads and ordering, but not atomic compound actions', 'That ++ is atomic', 'That only one thread runs', 'That the field is constant'], 0, 'Visible, not atomic.', 'Use AtomicInteger or a lock for read, modify, write.'),
    quiz('m', 'Three calls take 400, 600 and 300 ms. How long does allOf on three supplyAsync calls take, roughly?', ['600 ms', '1300 ms', '300 ms', '433 ms'], 0, 'Wait for the slowest.', 'They run at the same time, so the total is the maximum.'),
    quiz('m', 'Which ConcurrentHashMap call counts hits safely?', ['map.merge(key, 1, Integer::sum)', 'map.put(key, map.get(key) + 1)', 'if (!map.containsKey(key)) map.put(key, 1)', 'map.get(key) + 1'], 0, 'One atomic call.', 'get then put is "check then act" and can lose updates.'),
    quiz('m', 'What does this print?', ['5', '0', 'Compile error', 'It hangs'], 0, 'A latch of 5 counted down 5 times.', 'The loop calls countDown until the count is zero, which takes 5 calls. After that await returns at once instead of waiting, so the program prints 5.', code='void main() throws InterruptedException {\n    CountDownLatch l = new CountDownLatch(5);\n    int calls = 0;\n    while (l.getCount() > 0) { l.countDown(); calls++; }\n    l.await();\n    System.out.println(calls);\n}', run=True),
    quiz('h', 'What happens to a virtual thread that blocks on a socket read?', ['It is unmounted and its carrier thread runs another virtual thread', 'Its carrier thread blocks too', 'The JVM creates a new platform thread', 'It throws an exception'], 0, 'Parked, not blocking.', 'Its stack is saved on the heap until the data arrives.'),
    quiz('h', 'In structured concurrency with the default joiner, what happens when one forked subtask fails?', ['The other subtasks are cancelled and join throws', 'The others keep running in the background', 'The failure is ignored', 'The JVM exits'], 0, 'One unit.', 'That is the point: no orphan threads keep working after the result is already lost.'),
    quiz('h', 'Why are scoped values a better fit than ThreadLocal for virtual threads?', ['They are immutable, bounded to a block and cheap to share with many threads', 'ThreadLocal does not work at all with virtual threads', 'They are faster to type', 'They store values on disk'], 0, 'Lifetime and cost.', 'ThreadLocal values are mutable, live as long as the thread, and are copied per thread, which adds up with millions of threads.'),
    quiz('x', 'What does this print?', ['true', 'false', 'null', 'Compile error'], 0, 'Run inside a virtual thread.', 'isVirtual reports true inside a thread started by Thread.ofVirtual().', code='void main() throws InterruptedException {\n    Thread t = Thread.ofVirtual().start(() -> System.out.println(Thread.currentThread().isVirtual()));\n    t.join();\n}', run=True),
    quiz('x', 'What does this print?', ['fallback', 'ok', 'IllegalStateException', 'null'], 0, 'exceptionally provides the value.', 'The supplier throws, so exceptionally runs and returns "fallback".', code='System.out.println(CompletableFuture.supplyAsync(() -> { if (true) throw new IllegalStateException("x"); return "ok"; }).exceptionally(e -> "fallback").join());', run=True),
]

CALC = [
    calc('e', 'Two threads each add 1 to an AtomicInteger 500 times. What is the final value?', '1000', 'Atomics never lose updates.', ['<span class="eq">2 × 500 = 1000</span>']),
    calc('e', 'Three services take 400, 600 and 300 ms. How many ms does calling them one after another take?', '1300', 'Add them.', ['<span class="eq">400 + 600 + 300 = 1300</span>']),
    calc('m', 'How many ms are saved by running those three calls in parallel?', '700', 'Sum minus the slowest.', ['<span class="eq">1300 − max(400, 600, 300) = 1300 − 600 = 700</span>']),
    calc('m', '1000 tasks each wait 1 second on a fixed pool of 100 platform threads. About how many seconds does it take?', '10', 'Rounds of 100.', ['<span class="eq"><span class="fr"><i>1000</i><i>100</i></span> = 10 rounds × 1 s = 10 s</span>']),
    calc('m', 'What does this print?', '{a=2, b=1}', 'merge adds 1 per occurrence.', ['a appears twice and b once.'], code='var m = new ConcurrentHashMap<String, Integer>();\nfor (String k : List.of("a", "b", "a")) m.merge(k, 1, Integer::sum);\nSystem.out.println(new TreeMap<>(m));', run=True),
    calc('h', 'A Semaphore has 50 permits and 300 calls take 0.3 s each. Ignoring overhead, about how many seconds does the smoke test take?', '1.8', 'Rounds of 50.', ['<span class="eq"><span class="fr"><i>300</i><i>50</i></span> = 6 rounds</span>', '<span class="eq">6 × 0.3 = 1.8 s</span>']),
    calc('h', 'A platform thread reserves about 1 MB of stack. How many MB do 4000 platform threads reserve?', '4000', 'One MB each.', ['<span class="eq">4000 × 1 MB = 4000 MB, about 4 GB</span>', 'This is why servers could not simply use a thread per request before virtual threads.']),
    calc('x', 'What does this print?', '3', 'Count the successful tryLock calls on a free lock.', ['A ReentrantLock can be locked again by the thread that holds it.', 'All 3 tryLock calls succeed and the hold count is 3.'], code='var lock = new java.util.concurrent.locks.ReentrantLock();\nint ok = 0;\nfor (int i = 0; i < 3; i++) if (lock.tryLock()) ok++;\nSystem.out.println(lock.getHoldCount());', run=True),
]

T = {
    'slug': 'java-concurrency', 'title': 'Concurrency in depth: from executors to virtual threads', 'short': 'Modern concurrency', 'emoji': '🧵', 'module': MODULE, 'minutes': 28,
    'lead': 'Doing many things at once is where Java programs get fast, and where the hardest bugs hide. This chapter builds on the multithreading chapter with executors and futures, race conditions and their fixes, the memory model, concurrent collections, latches and semaphores, CompletableFuture, virtual threads from Java 21, and structured concurrency and scoped values from Java 25 to 27.',
    'desc': 'Java concurrency in depth: ExecutorService, Callable, Future, race conditions, synchronized, AtomicInteger, LongAdder, ReentrantLock, volatile and happens-before, ConcurrentHashMap, BlockingQueue, CountDownLatch, Semaphore, CompletableFuture, virtual threads, structured concurrency and scoped values.',
    'summary': 'Executors and futures, race conditions and four fixes, tryLock, visibility and happens-before, concurrent collections and check then act, producer consumer queues, CountDownLatch and Semaphore, CompletableFuture with errors and timeouts, virtual threads and how they use carrier threads, structured concurrency (Java 27 preview) and scoped values (Java 25), and a 300 endpoint smoke test.',
    'keywords': ['concurrency', 'ExecutorService', 'Future', 'race condition', 'AtomicInteger', 'ReentrantLock', 'volatile', 'happens-before', 'ConcurrentHashMap', 'BlockingQueue', 'CompletableFuture', 'virtual threads', 'structured concurrency', 'scoped values', 'Java 21', 'Java 25'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
