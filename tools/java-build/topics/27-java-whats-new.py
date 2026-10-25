# Chapter 27: what is new in Java, from the Java 21 LTS to Java 27, with a real run for each feature and what it is good for
# at work: the release train, preview features, sequenced collections, the FFM API, multi file launch, ML-KEM, ML-DSA,
# the KDF API, compact source files, flexible constructor bodies, lazy constants, PEM encoding and hybrid TLS.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

LAZY = '''
void main() {
    // Java 27 preview (JEP 531): computed once, on first use, then treated as a constant by the JVM
    LazyConstant<String> config = LazyConstant.of(() -> {
        IO.println("reading config file...");
        return "env=prod";
    });
    IO.println("app started");
    IO.println(config.get());
    IO.println(config.get());
}
'''

CODES = {
    'preview': sh({'Main.java': LAZY},
        'echo "--- without the flag ---" && javac --release 27 Main.java 2>&1 | head -1 && echo "--- with --enable-preview ---" && javac --release 27 --enable-preview Main.java 2>&1 | head -1 && java --enable-preview Main',
        'Preview features need a flag at compile time and at run time', jdk=27,
        shown='$ javac --release 27 Main.java\n$ javac --release 27 --enable-preview Main.java\n$ java --enable-preview Main'),
    'sequenced': j('''
void main() {
    // Java 21 (JEP 431): one set of methods for every ordered collection
    List<String> queue = new ArrayList<>(List.of("login", "search", "cart"));
    queue.addFirst("health");
    queue.addLast("pay");
    IO.println(queue.getFirst() + " ... " + queue.getLast());
    IO.println("reversed view: " + queue.reversed());

    LinkedHashMap<String, Integer> visits = new LinkedHashMap<>();
    visits.put("home", 10);
    visits.put("cart", 4);
    visits.putFirst("landing", 25);              // insert at the front
    IO.println("first entry: " + visits.firstEntry() + ", last: " + visits.lastEntry());

    LinkedHashSet<String> tags = new LinkedHashSet<>(List.of("new", "sale", "eco"));
    IO.println("removed last tag: " + tags.removeLast() + ", left: " + tags);
}
''', 'Sequenced collections: getFirst, getLast and reversed (Java 21)'),
    'multifile': sh({'Main.java': '''
void main() {
    IO.println(Prices.withTax(200));
}
''', 'Prices.java': '''
class Prices {
    static double withTax(double amount) {
        return amount * 1.18;
    }
}
'''}, 'java Main.java', 'Run a small program of several files without javac (Java 22)', shown='$ java Main.java     # Prices.java is found and compiled in memory'),
    'ffm': sh({'Main.java': '''
import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;

void main() throws Throwable {
    // Java 22 (JEP 454): call the C library function strlen without writing any C or JNI code
    Linker linker = Linker.nativeLinker();
    MethodHandle strlen = linker.downcallHandle(
            linker.defaultLookup().find("strlen").orElseThrow(),
            FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS));

    try (Arena arena = Arena.ofConfined()) {               // native memory, freed when the block ends
        MemorySegment text = arena.allocateFrom("Hello from C");
        IO.println("strlen says " + (long) strlen.invokeExact(text));
    }
}
'''}, 'echo "--- default ---" && java Main.java 2>&1 && echo "--- with native access allowed ---" && java --enable-native-access=ALL-UNNAMED Main.java',
        'The foreign function and memory API calls C directly (Java 22)',
        shown='$ java Main.java\n$ java --enable-native-access=ALL-UNNAMED Main.java', replace=[(r'\(file:[^)]*\)', '(file:/app/Main.java)')]),
    'pqc': j('''
import javax.crypto.*;
import java.security.*;
import java.util.*;

void main() throws Exception {
    // Java 24 (JEP 496): ML-KEM agrees on a secret key in a way quantum computers cannot break
    KeyPair server = KeyPairGenerator.getInstance("ML-KEM").generateKeyPair();
    KEM kem = KEM.getInstance("ML-KEM");
    KEM.Encapsulated sent = kem.newEncapsulator(server.getPublic()).encapsulate();   // client side
    SecretKey clientKey = sent.key();
    SecretKey serverKey = kem.newDecapsulator(server.getPrivate()).decapsulate(sent.encapsulation());   // server side
    IO.println("bytes sent over the network: " + sent.encapsulation().length);
    IO.println("both sides got the same AES key? " + Arrays.equals(clientKey.getEncoded(), serverKey.getEncoded()));

    // Java 24 (JEP 497): ML-DSA signatures
    KeyPair signer = KeyPairGenerator.getInstance("ML-DSA").generateKeyPair();
    Signature sig = Signature.getInstance("ML-DSA");
    sig.initSign(signer.getPrivate());
    sig.update("invoice 42: 1500 rupees".getBytes());
    byte[] signature = sig.sign();
    sig.initVerify(signer.getPublic());
    sig.update("invoice 42: 9500 rupees".getBytes());         // someone changed the amount
    IO.println("signature of " + signature.length + " bytes still valid after tampering? " + sig.verify(signature));
}
''', 'Post quantum key exchange and signatures (Java 24)', trace=False),
    'kdf': j('''
import javax.crypto.*;
import javax.crypto.spec.HKDFParameterSpec;
import java.util.HexFormat;

void main() throws Exception {
    // Java 25 (JEP 510): the Key Derivation Function API, here with HKDF
    KDF hkdf = KDF.getInstance("HKDF-SHA256");
    var spec = HKDFParameterSpec.ofExtract()
            .addIKM("master-secret-from-the-vault".getBytes())
            .addSalt("tenant-42".getBytes())
            .thenExpand("orders-db-encryption".getBytes(), 16);   // 16 bytes = an AES-128 key
    SecretKey key = hkdf.deriveKey("AES", spec);
    IO.println(key.getAlgorithm() + " key: " + HexFormat.of().formatHex(key.getEncoded()));
    IO.println("same inputs always give the same key, so it never needs to be stored");
}
''', 'Deriving keys with the KDF API (Java 25)', trace=False),
    'compact': sh({'Hello.java': '''
void main() {
    String name = IO.readln("Your name: ");
    IO.println("Hello, " + name + "! This is the whole program.");
}
'''}, 'echo Asha | java Hello.java', 'Compact source files, instance main and IO (Java 25)', shown='$ java Hello.java'),
    'flexible': j('''
class Person {
    final String name;
    Person(String name) {
        System.out.println("Person stores the name");
        this.name = name;
    }
}

class Employee extends Person {
    final int age;

    Employee(String name, int age) {
        if (age < 18) throw new IllegalArgumentException("too young: " + age);   // Java 25: allowed before super
        this.age = age;                    // fields of this class may be set before super too
        super(name.strip());
    }
}

void main() {
    IO.println(new Employee("  Asha ", 29).name);
    try {
        new Employee("Ravi", 15);
    } catch (IllegalArgumentException e) {
        IO.println("rejected before Person ran: " + e.getMessage());
    }
}
''', 'Flexible constructor bodies: check arguments before super (Java 25)'),
    'lazy': j(LAZY, 'Lazy constants: expensive values computed once (Java 27 preview)', jdk=27, preview=True, trace=False),
    'pem': j('''
import java.security.*;

void main() throws Exception {
    // Java 27 preview (JEP 538): read and write the PEM text format used by certificates and keys
    KeyPair kp = KeyPairGenerator.getInstance("EC").generateKeyPair();
    String pem = PEMEncoder.of().encodeToString(kp.getPublic());
    List<String> lines = pem.lines().toList();
    IO.println(lines.getFirst());
    IO.println("... " + (lines.size() - 2) + " lines of Base64 ...");
    IO.println(lines.getLast());

    PublicKey back = PEMDecoder.of().decode(pem, PublicKey.class);
    IO.println("same key after the round trip? " + back.equals(kp.getPublic()));
}
''', 'PEM encoding without Bouncy Castle (Java 27 preview)', jdk=27, preview=True, trace=False),
    'tls': j('''
import javax.net.ssl.SSLContext;
import java.util.List;

void main() throws Exception {
    // Java 27 (JEP 527): TLS 1.3 offers a hybrid of X25519 and ML-KEM first
    List<String> groups = List.of(SSLContext.getDefault().getDefaultSSLParameters().getNamedGroups());
    IO.println("first choice: " + groups.getFirst());
    IO.println("all groups offered: " + groups);
}
''', 'Hybrid post quantum TLS is on by default (Java 27)', jdk=27, trace=False),
    'jdeps': sh({'Main.java': '''
class Main {
    public static void main(String[] args) throws Exception {
        var f = sun.misc.Unsafe.class.getDeclaredField("theUnsafe");   // an old trick many libraries used
        System.out.println("found " + f.getName());
    }
}
'''}, 'javac Main.java 2>&1 | head -1 && jdeps --jdk-internals Main.class | grep -v "^$" | head -2',
        'Finding uses of JDK internals before an upgrade',
        shown='$ javac Main.java\n$ jdeps --jdk-internals Main.class'),
}

DG = {
    'train': {'t': 'How a feature travels to final', 'w': 900, 'h': 300, 'mw': 640,
        'n': [['inc', 30, 40, 200, 60, 'Incubator', {'c': 5, 'sub': 'jdk.incubator module'}],
              ['pre', 30, 180, 200, 60, 'Preview', {'c': 3, 'sub': '--enable-preview'}],
              ['fin', 340, 110, 200, 60, 'Final', {'c': 4, 'sub': 'usable everywhere'}],
              ['lts', 650, 40, 220, 60, 'Next LTS', {'c': 1, 'sub': 'every two years: 21, 25, 29'}],
              ['ex', 650, 180, 220, 60, 'Example', {'c': 2, 'sub': 'virtual threads: 19, 20, then 21'}]],
        'e': [['inc', 'pre', {'t': 'API settles', 'id': 't1'}], ['pre', 'fin', {'t': 'feedback done', 'id': 't2'}], ['fin', 'lts', {'id': 't3'}],
              ['fin', 'ex', {'id': 't4', 'd': 1}]],
        'st': [[['inc'], 'Some APIs start as incubators in a jdk.incubator module, such as the Vector API, now in its 12th incubator round in Java 27.'],
               [['pre', 't1'], 'Language and API features usually start as previews. They are complete but may still change, so they are off unless you ask for them.'],
               [['pre'], 'A preview can repeat. Structured concurrency is in its seventh preview in Java 27, and lazy constants in their third.'],
               [['fin', 't2'], 'When the feedback is in, the feature becomes final and works in every program with no flags.'],
               [['lts', 't3'], 'A new release comes every six months, in March and September. Every fourth one, every two years, is a long term support release that companies standardise on.'],
               [['ex', 't4'], 'Virtual threads were a preview in Java 19 and 20, final in 21, and fixed for synchronized blocks in 24.']]},
}

PARTS = [
    part('train', '🚆', 'The release train, LTS and preview features', '''
<p>Java ships a new version every six months, in March and September. Java 25 (September 2025) is the latest <b>long term support</b> (LTS) release, Java 26 came in March 2026 and Java 27 in September 2026. Most companies run an LTS in production and try the newer releases in CI.</p>
<div class="viz" data-viz="jrelease"></div>
<div class="viz" data-viz="flow" data-k="train"></div>
<p>A <b>preview</b> feature is complete but may still change, so javac and java refuse it unless you pass <code>--enable-preview</code>. Use previews to learn and give feedback, not in production code.</p>
[[preview]]
''', kw=['release cadence', 'six month release', 'LTS', 'long term support', 'Java 25 LTS', 'Java 26', 'Java 27', 'preview feature', '--enable-preview', 'incubator', 'upgrade plan']),
    part('j21', '🧵', 'Java 21 LTS: sequenced collections', '''
<p>Java 21 brought virtual threads, record patterns and pattern matching for switch, each covered in its own chapter. One small change you will use daily is <b>sequenced collections</b>. Before Java 21, getting the last element of a list was <code>list.get(list.size() - 1)</code>, and for a LinkedHashSet there was no simple way at all.</p>
[[sequenced]]
<p>At work: reading the latest event from an ordered log, showing recent searches newest first with <code>reversed()</code>, or evicting the oldest entry from a LinkedHashMap cache with <code>pollFirstEntry()</code>.</p>
''', kw=['sequenced collections', 'SequencedCollection', 'getFirst', 'getLast', 'reversed', 'addFirst', 'putFirst', 'firstEntry', 'JEP 431', 'Java 21']),
    part('j22', '🔗', 'Java 22 and 23: native code, multi file launch, Markdown docs', '''
<p>The <b>foreign function and memory API</b> (JEP 454, final in Java 22) lets Java call C libraries and work with memory outside the heap safely, replacing most JNI code. Database drivers, machine learning libraries and image tools use it to reach native code.</p>
[[ffm]]
<p>Calling native code can crash the JVM, so it counts as a <b>restricted</b> operation. Today it prints a warning. A future release will block it unless the application allows it with <code>--enable-native-access</code>.</p>
<p>Java 11 could already run one source file with <code>java Hello.java</code>. Java 22 (JEP 458) extends that to programs made of several files, which is handy for scripts and small tools that grow.</p>
[[multifile]]
<p>Java 23 (JEP 467) lets documentation comments be written in Markdown with <code>///</code> instead of HTML inside <code>/** */</code>, so API docs are easier to read in the source.</p>
''', kw=['foreign function and memory API', 'FFM', 'Panama', 'Linker', 'MemorySegment', 'Arena', 'JNI replacement', 'JEP 454', 'restricted methods', 'enable-native-access', 'multi file source launch', 'JEP 458', 'Markdown doc comments', 'JEP 467']),
    part('j24', '🔐', 'Java 24: quantum safe cryptography', '''
<p>Big quantum computers could one day break RSA and elliptic curve keys. Attackers can record encrypted traffic today and decrypt it later. Java 24 added the NIST standard algorithms that resist this: <b>ML-KEM</b> for agreeing on keys (JEP 496) and <b>ML-DSA</b> for signatures (JEP 497).</p>
[[pqc]]
<p>Java 24 also brought stream gatherers and virtual threads that no longer get pinned by <code>synchronized</code>, both covered in earlier chapters, the ahead of time cache from the JVM chapter, and the final removal of the Security Manager's ability to be turned on (JEP 486).</p>
''', kw=['post quantum cryptography', 'ML-KEM', 'ML-DSA', 'KEM', 'JEP 496', 'JEP 497', 'harvest now decrypt later', 'Java 24', 'Security Manager removed']),
    part('j25', '✨', 'Java 25 LTS: simpler programs and safer constructors', '''
<p>Java 25 made starting with Java much simpler. <b>Compact source files</b> and <b>instance main methods</b> (JEP 512) remove the class, <code>static</code> and <code>String[] args</code> ceremony, and the new <code>IO</code> class reads and prints text without <code>System.out</code> or a Scanner.</p>
[[compact]]
<p><b>Flexible constructor bodies</b> (JEP 513) allow statements before <code>super(...)</code>. Arguments can now be checked before the parent class does any work, and fields can be set early so the parent never sees them half initialised.</p>
[[flexible]]
<p>The <b>Key Derivation Function API</b> (JEP 510) turns one master secret into many separate keys, one per tenant or per purpose, which is how modern TLS and secret managers work.</p>
[[kdf]]
<p>Java 25 also made scoped values (concurrency chapter), module import declarations (modules chapter) and compact object headers (JVM chapter) final.</p>
''', kw=['Java 25', 'compact source files', 'instance main', 'IO.println', 'IO.readln', 'JEP 512', 'flexible constructor bodies', 'statements before super', 'JEP 513', 'KDF', 'HKDF', 'JEP 510']),
    part('j26', '🧪', 'Java 26 and 27: what is final and what to try', '''
<p>Java 26 added HTTP/3 to HttpClient (JDBC and HTTP chapter), warns before final fields can be changed by reflection (modules chapter), removed the old Applet API (JEP 504) and let the AOT cache work with every garbage collector (JVM chapter). Java 27 made G1 the default everywhere and compact object headers the default (JVM chapter), and switched TLS to a quantum safe hybrid key exchange:</p>
[[tls]]
<p><code>X25519MLKEM768</code> combines a classic elliptic curve exchange with ML-KEM, so the connection stays safe if either one is broken. Servers that do not support it simply pick the next group, so nothing breaks. The Java 25 update used to build this page offers it first too, as Oracle has brought it to recent Java 25 updates.</p>
<p>Two previews worth trying. <b>Lazy constants</b> (third preview, JEP 531) hold a value that is computed once on first use, such as a config file or a client object, and then trusted by the JIT like a <code>final</code> field.</p>
[[lazy]]
<p>The <b>PEM API</b> (third preview, JEP 538) reads and writes the text format of keys and certificates that every server uses, a job that needed Bouncy Castle or hand written Base64 code before.</p>
[[pem]]
<div class="tw"><table class="jt"><tr><th>Still in preview or incubator in Java 27</th><th>Round</th></tr>
<tr><td>Structured concurrency (JEP 533)</td><td>7th preview</td></tr>
<tr><td>Primitive types in patterns (JEP 532)</td><td>5th preview</td></tr>
<tr><td>Lazy constants (JEP 531)</td><td>3rd preview</td></tr>
<tr><td>PEM encodings (JEP 538)</td><td>3rd preview</td></tr>
<tr><td>Vector API (JEP 537)</td><td>12th incubator</td></tr></table></div>
''', kw=['Java 26', 'Java 27', 'lazy constants', 'LazyConstant', 'JEP 531', 'PEM', 'PEMEncoder', 'PEMDecoder', 'JEP 538', 'hybrid key exchange', 'X25519MLKEM768', 'JEP 527', 'applet API removed', 'JEP 504', 'Vector API']),
    part('scenario', '🎬', 'Real world scenario: upgrading a service from Java 17 to Java 25', '''
<div class="scenario"><b>The situation</b>A payments service runs on Java 17. The team wants virtual threads, sequenced collections and the startup gains of Java 25, without surprises in production.</div>
<p>Step one is finding code that relies on JDK internals, because strong encapsulation and the removal of old APIs are what usually break upgrades.</p>
[[jdeps]]
<div class="tw"><table class="jt"><tr><th>Step</th><th>Why</th></tr>
<tr><td>Run <code>jdeps --jdk-internals</code> and <code>jdeprscan</code></td><td>find internal and deprecated API use early</td></tr>
<tr><td>Upgrade build plugins, Lombok, Mockito, ByteBuddy, Spring</td><td>libraries that generate bytecode must know the new class file version</td></tr>
<tr><td>Build and test with the new JDK in CI first</td><td>catch behaviour changes before production</td></tr>
<tr><td>Read the release notes for removed options</td><td>for example the Security Manager can no longer be enabled since Java 24</td></tr>
<tr><td>Then adopt features one by one</td><td>virtual threads for blocking I/O, records for DTOs, pattern matching for parsing</td></tr></table></div>
''', kw=['Java upgrade', 'migration', 'Java 17 to Java 25', 'jdeps', 'jdeprscan', 'sun.misc.Unsafe', 'JDK internals', 'release notes', 'upgrade checklist']),
]

INFO = {'title': 'Java keeps getting newer', 'panels': [
    panel([['e', '🚆'], ['t', 'March and September', {'b': 1, 'size': 11}]], 'Release train', 'Two releases a year.', 'An LTS every two years: 21, 25 ...'),
    panel([['e', '📚'], ['t', 'list.getLast()', {'b': 1}]], 'Java 21', 'Sequenced collections.', 'First, last and reversed for every ordered collection.'),
    panel([['e', '🔐'], ['t', 'KEM.getInstance("ML-KEM")', {'b': 1, 'size': 10}]], 'Java 24 to 27', 'Quantum safe crypto.', 'Now on by default in TLS.'),
    panel([['e', '✨'], ['t', 'void main() { IO.println("hi"); }', {'b': 1, 'size': 9}]], 'Java 25', 'Simple programs, safe constructors.', 'Checks can come before super().')],
    'remember': 'Run an LTS in production, try new releases in CI, and use previews only to learn. Java 21 to 27 bring sequenced collections, native calls without JNI, quantum safe crypto, compact source files, flexible constructors and safer TLS by default.'}

REAL = [
    ['🏦', 'A bank', 'Switched internal TLS to a hybrid post quantum key exchange to protect recorded traffic from future quantum attacks, with no code change after moving to a new JDK.'],
    ['🧠', 'A machine learning team', 'Replaced a fragile JNI wrapper with the FFM API to call a C inference library, and deleted all their C glue code.'],
    ['🎓', 'A coding school', 'Teaches first programs as compact source files with <code>void main()</code> and <code>IO.println</code>, and introduces classes only once students need them.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to what is new in Java, from the Java 21 LTS to Java 27, with a real run for every feature.',
        'Java में क्या नया है, Java 21 LTS से Java 27 तक, हर feature के असली run के साथ, उसमें स्वागत है।',
        'Java 21 LTS ನಿಂದ Java 27 ವರೆಗೆ ಹೊಸದು ಏನು ಎಂಬುದಕ್ಕೆ ಸ್ವಾಗತ.',
        'Java 21 LTS ରୁ Java 27 ପର୍ଯ୍ୟନ୍ତ ନୂଆ କଣ, ତାକୁ ସ୍ୱାଗତ।',
        'مرحبًا بك في الجديد في Java من الإصدار 21 طويل الدعم حتى Java 27، مع تشغيل حقيقي لكل ميزة.',
        'Willkommen zu den Neuerungen in Java, vom LTS Java 21 bis Java 27, mit einem echten Lauf für jedes Feature.'),
    say('train', 'Release train', 'A new Java comes every March and September. Every two years one is a long term support release. Preview features need the enable preview flag.',
        'हर मार्च और सितंबर में नया Java आता है। हर दो साल में एक long term support release होता है। Preview features के लिए enable preview flag चाहिए।',
        'ಪ್ರತಿ ಮಾರ್ಚ್ ಮತ್ತು ಸೆಪ್ಟೆಂಬರ್ ಹೊಸ Java. ಎರಡು ವರ್ಷಕ್ಕೊಮ್ಮೆ LTS.',
        'ପ୍ରତି ମାର୍ଚ୍ଚ ଏବଂ ସେପ୍ଟେମ୍ବରରେ ନୂଆ Java। ଦୁଇ ବର୍ଷରେ ଥରେ LTS।',
        'يصدر Java جديد كل مارس وسبتمبر، وكل سنتين يكون أحدها إصدارًا طويل الدعم، وتحتاج الميزات التجريبية إلى خيار enable preview.',
        'Jeden März und September erscheint ein neues Java. Alle zwei Jahre ist eines ein LTS-Release. Preview-Features brauchen die Option enable preview.'),
    say('j21', 'Java 21', 'Sequenced collections add getFirst, getLast, addFirst and reversed to lists, ordered sets and ordered maps.',
        'Sequenced collections lists, ordered sets और ordered maps में getFirst, getLast, addFirst और reversed जोड़ते हैं।',
        'Sequenced collections getFirst, getLast, reversed ಸೇರಿಸುತ್ತವೆ.',
        'Sequenced collections getFirst, getLast, reversed ଯୋଡ଼ନ୍ତି।',
        'تضيف المجموعات المتسلسلة getFirst وgetLast وaddFirst وreversed إلى القوائم والمجموعات والخرائط المرتبة.',
        'Sequenced Collections bringen getFirst, getLast, addFirst und reversed für Listen, geordnete Sets und Maps.'),
    say('j22', 'Java 22 and 23', 'The foreign function and memory API calls C code without JNI. Programs of several files run with java Main dot java, and docs can be written in Markdown.',
        'Foreign function and memory API बिना JNI के C code बुलाता है। कई files के programs java Main dot java से चलते हैं, और docs Markdown में लिखे जा सकते हैं।',
        'FFM API JNI ಇಲ್ಲದೆ C code ಕರೆಯುತ್ತದೆ. ಹಲವು files ನ program ನೇರವಾಗಿ ಓಡುತ್ತದೆ.',
        'FFM API JNI ବିନା C code ଡାକେ। ଅନେକ files program ସିଧା ଚାଲେ।',
        'تستدعي واجهة الدوال والذاكرة الخارجية شيفرة C دون JNI، وتعمل البرامج متعددة الملفات مباشرة، ويمكن كتابة التوثيق بـ Markdown.',
        'Die Foreign Function and Memory API ruft C-Code ohne JNI auf. Programme aus mehreren Dateien laufen direkt, und Doku geht in Markdown.'),
    say('j24', 'Java 24', 'Java 24 adds ML-KEM for key exchange and ML-DSA for signatures, which stay safe against future quantum computers.',
        'Java 24 key exchange के लिए ML-KEM और signatures के लिए ML-DSA जोड़ता है, जो भविष्य के quantum computers से सुरक्षित हैं।',
        'Java 24 ML-KEM ಮತ್ತು ML-DSA ಸೇರಿಸುತ್ತದೆ, quantum ವಿರುದ್ಧ ಸುರಕ್ಷಿತ.',
        'Java 24 ML-KEM ଏବଂ ML-DSA ଯୋଡ଼େ, quantum ବିରୁଦ୍ଧରେ ସୁରକ୍ଷିତ।',
        'تضيف Java 24 خوارزمية ML-KEM لتبادل المفاتيح وML-DSA للتوقيعات، وهما آمنتان أمام الحواسيب الكمومية المستقبلية.',
        'Java 24 bringt ML-KEM für Schlüsseltausch und ML-DSA für Signaturen, sicher auch gegen künftige Quantencomputer.'),
    say('j25', 'Java 25', 'Java 25 allows a program that is just void main, adds the IO class, lets constructors check arguments before super, and adds a key derivation API.',
        'Java 25 सिर्फ void main वाला program, IO class, super से पहले arguments की जाँच, और key derivation API लाता है।',
        'Java 25 void main program, IO class, super ಮೊದಲು ಪರಿಶೀಲನೆ, KDF API.',
        'Java 25 void main program, IO class, super ପୂର୍ବରୁ ଯାଞ୍ଚ, KDF API।',
        'تسمح Java 25 ببرنامج من void main فقط، وتضيف الصنف IO، وتسمح للبانيات بفحص الوسائط قبل super، وتضيف واجهة اشتقاق المفاتيح.',
        'Java 25 erlaubt Programme nur aus void main, bringt die Klasse IO, Prüfungen vor super und eine API zur Schlüsselableitung.'),
    say('j26', 'Java 26 and 27', 'TLS now offers a hybrid quantum safe key exchange by default. Lazy constants and the PEM API are previews worth trying.',
        'TLS अब default रूप से hybrid quantum safe key exchange देता है। Lazy constants और PEM API आज़माने लायक previews हैं।',
        'TLS ಈಗ hybrid quantum safe key exchange ನೀಡುತ್ತದೆ. Lazy constants ಮತ್ತು PEM previews.',
        'TLS ବର୍ତ୍ତମାନ hybrid quantum safe key exchange ଦିଏ। Lazy constants ଏବଂ PEM previews।',
        'يعرض TLS الآن تبادل مفاتيح هجينًا آمنًا كموميًا افتراضيًا، والثوابت الكسولة وواجهة PEM ميزات تجريبية تستحق التجربة.',
        'TLS bietet jetzt standardmäßig einen hybriden, quantensicheren Schlüsseltausch. Lazy Constants und die PEM-API sind lohnende Previews.'),
    say('scenario', 'Scenario', 'Before an upgrade, find uses of JDK internals with jdeps, upgrade bytecode libraries, test in CI, then adopt new features one by one.',
        'Upgrade से पहले jdeps से JDK internals का इस्तेमाल खोजें, bytecode libraries upgrade करें, CI में test करें, फिर नए features एक एक करके अपनाएँ।',
        'Upgrade ಮೊದಲು jdeps ಬಳಸಿ, CI ನಲ್ಲಿ test ಮಾಡಿ.',
        'Upgrade ପୂର୍ବରୁ jdeps ବ୍ୟବହାର କରି CI ରେ test କରନ୍ତୁ।',
        'قبل الترقية ابحث عن استخدام الأجزاء الداخلية بأداة jdeps، وحدّث مكتبات البايت كود، واختبر في CI، ثم اعتمد الميزات الجديدة واحدة تلو الأخرى.',
        'Vor einem Upgrade findest du JDK-Interna mit jdeps, aktualisierst Bytecode-Bibliotheken, testest in CI und führst Neuerungen schrittweise ein.'),
]

QUIZ = [
    quiz('e', 'Which of these is a long term support (LTS) release?', ['Java 25', 'Java 26', 'Java 27', 'Java 23'], 0, 'Every two years.', 'The LTS releases are 8, 11, 17, 21 and 25.'),
    quiz('e', 'What does <code>list.getLast()</code> replace?', ['list.get(list.size() - 1)', 'list.remove(0)', 'list.clear()', 'list.size()'], 0, 'Java 21.', 'Sequenced collections give every ordered collection getFirst and getLast.'),
    quiz('e', 'What do you need to compile code that uses a preview feature?', ['--enable-preview together with --release', 'Nothing special', 'A special JDK download', 'An annotation on the class'], 0, 'Opt in.', 'The same flag is needed again when running with java.'),
    quiz('m', 'What may a Java 25 constructor do before calling <code>super(...)</code>?', ['Check arguments and assign its own fields', 'Call instance methods of the object', 'Read fields of the parent class', 'Nothing, super must be first'], 0, 'JEP 513.', 'It may not use this before super, apart from assigning fields.'),
    quiz('m', 'Which algorithm in Java 24 agrees on a shared key in a quantum safe way?', ['ML-KEM', 'ML-DSA', 'RSA', 'SHA-256'], 0, 'KEM means key encapsulation.', 'ML-DSA is for signatures.'),
    quiz('m', 'What does the FFM API replace in most cases?', ['JNI glue code written in C', 'The garbage collector', 'JDBC drivers', 'The HttpClient'], 0, 'Native calls.', 'You describe the C function in Java and call it through a MethodHandle.'),
    quiz('m', 'How often does a new Java version come out?', ['Every six months, in March and September', 'Every year in January', 'Every three years', 'Whenever it is ready'], 0, 'The release train.', 'Java 26 came in March 2026 and Java 27 in September 2026.'),
    quiz('h', 'What does <code>X25519MLKEM768</code> in the TLS groups of Java 27 mean?', ['A hybrid key exchange that combines X25519 with ML-KEM', 'A new cipher for files', 'A certificate format', 'A random number generator'], 0, 'JEP 527.', 'The connection is safe as long as either part holds.'),
    quiz('h', 'How many times is the supplier of a LazyConstant called if get() is called five times?', ['Once', 'Five times', 'Never', 'Twice'], 0, 'Computed once.', 'After the first call the value is stored and trusted like a constant.'),
    quiz('h', 'What prints a warning in Java 22 to 25 when you call <code>Linker.downcallHandle</code> without extra flags?', ['It is a restricted method, so the JVM warns unless native access is enabled', 'The method is deprecated', 'The C library is missing', 'Nothing prints a warning'], 0, '--enable-native-access.', 'A future release will block restricted methods unless native access is enabled.'),
    quiz('x', 'What does this print?', ['c', 'a', '[c, b, a]', 'b'], 0, 'reversed is a view in the opposite order.', 'The first element of the reversed view is the last element, c.', code='System.out.println(List.of("a", "b", "c").reversed().getFirst());', run=True),
    quiz('x', 'What does this print?', ['3', '2', '0', 'Compile error'], 0, 'putFirst adds a new entry at the front.', 'The map now has three entries: z, x and y.', code='var m = new LinkedHashMap<String, Integer>();\nm.put("x", 1);\nm.put("y", 2);\nm.putFirst("z", 0);\nSystem.out.println(m.size());', run=True),
]

CALC = [
    calc('e', 'LTS releases come every two years. Java 25 came in 2025. In which year is the next LTS, Java 29, expected?', '2027', 'Two years later.', ['<span class="eq">2025 + 2 = 2027</span>']),
    calc('e', 'Java 26 came in March 2026. Releases are 6 months apart. How many months after Java 26 does Java 28 come?', '12', 'Two steps of six.', ['<span class="eq">2 × 6 = 12 months</span>']),
    calc('m', 'A team moves from Java 17 to Java 25. How many feature releases do they gain?', '8', 'Count 18 to 25.', ['<span class="eq">25 − 17 = 8</span>']),
    calc('m', 'What does this print?', 'pay', 'getLast of the list after addLast.', ['addLast puts pay at the end.'], code='var l = new ArrayList<>(List.of("login", "cart"));\nl.addLast("pay");\nSystem.out.println(l.getLast());', run=True),
    calc('h', 'An ML-KEM-768 exchange sends 1088 bytes. How many bytes do 1000 TLS handshakes send for it?', '1088000', 'Multiply.', ['<span class="eq">1088 × 1000 = 1,088,000 bytes</span>', 'That is about 1 MB, a small price for quantum safety.']),
    calc('h', 'Structured concurrency was first previewed in Java 21 and is in its seventh preview in Java 27. Counting both, in how many releases has it been a preview?', '7', 'From 21 to 27.', ['<span class="eq">27 − 21 + 1 = 7</span>']),
    calc('x', 'What does this print?', '12', 'strlen counts characters, without the hidden zero at the end.', ['"Hello from C" has 12 characters.'], code='System.out.println("Hello from C".length());', run=True),
]

T = {
    'slug': 'java-whats-new', 'title': 'What is new in Java: from Java 21 to Java 27', 'short': 'What is new up to Java 27', 'emoji': '🆕', 'module': MODULE, 'minutes': 25,
    'lead': 'Java moves fast: a release every six months and a long term support version every two years. This chapter walks through what changed from the Java 21 LTS to Java 27, runs every feature on a real JDK, and explains where each one helps at work, from sequenced collections and native calls to quantum safe cryptography and simpler programs.',
    'desc': 'What is new in Java 21 to 27: the release train, LTS and preview features, sequenced collections, the foreign function and memory API, multi file launch, Markdown docs, ML-KEM and ML-DSA, compact source files and IO, flexible constructor bodies, the KDF API, lazy constants, the PEM API, hybrid post quantum TLS, and how to plan an upgrade.',
    'summary': 'How releases and previews work, an upgrade planner from Java 8 to 27, sequenced collections, calling C with FFM, multi file programs, quantum safe key exchange and signatures, compact source files, constructors that check before super, key derivation, lazy constants and PEM previews, hybrid TLS by default, and a Java 17 to 25 upgrade checklist.',
    'keywords': ['Java 21', 'Java 22', 'Java 23', 'Java 24', 'Java 25', 'Java 26', 'Java 27', 'new features', 'LTS', 'preview', 'sequenced collections', 'FFM API', 'ML-KEM', 'compact source files', 'flexible constructor bodies', 'lazy constants', 'upgrade'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
