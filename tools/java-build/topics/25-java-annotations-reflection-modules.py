# Chapter 25: annotations, reflection, dynamic proxies, the module system (JPMS), jlink, module import declarations (Java 25)
# and the Java 26 and 27 warnings about changing final fields with reflection.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

HASH = [(r'@[0-9a-f]{6,8}\b', '@5a07e868'), (r'\(file:[^)]*\)', '(file:/app/)')]

CORE_INFO = '''
module com.shop.core {
    exports com.shop.core.api;      // other modules may use this package
    // com.shop.core.internal is not exported, so it stays private to this module
}
'''
PRICES = '''
package com.shop.core.api;

import com.shop.core.internal.TaxTable;

public class Prices {
    public static double withTax(double amount) {
        return amount + amount * TaxTable.rate();
    }
}
'''
TAX = '''
package com.shop.core.internal;

public class TaxTable {
    public static double rate() { return 0.18; }
}
'''
APP_INFO = '''
module com.shop.app {
    requires com.shop.core;
}
'''

CODES = {
    'override': j('''
class Main {
    static class Product {
        String name = "pen";
        @Override
        public String toString() { return "Product " + name; }

        @Override
        public boolean equal(Object o) { return o == this; }     // typo: equals is spelled wrong
    }

    public static void main(String[] args) {
        System.out.println(new Product());
    }
}
''', '@Override catches a misspelled method', expect='compile'),
    'deprecated': j('''
class Main {
    static class Payments {
        /** @deprecated use {@link #pay(String, long)} with the amount in paise */
        @Deprecated(since = "2.0", forRemoval = true)
        static void pay(String user, double rupees) { pay(user, Math.round(rupees * 100)); }

        static void pay(String user, long paise) { System.out.println(user + " paid " + paise + " paise"); }
    }

    @SuppressWarnings("removal")
    public static void main(String[] args) {
        Payments.pay("asha", 49.5);          // old call, warning silenced on purpose
        Payments.pay("ravi", 4950L);
        System.out.println("@FunctionalInterface on Runnable? " + Runnable.class.isAnnotationPresent(FunctionalInterface.class));
    }
}
''', 'Deprecated, SuppressWarnings and FunctionalInterface'),
    'custom': j('''
import java.lang.annotation.*;
import java.lang.reflect.*;

class Main {
    @Retention(RetentionPolicy.RUNTIME)      // keep it in the class file and visible to reflection
    @Target(ElementType.METHOD)              // only allowed on methods
    @interface Test {
        String name() default "";
        boolean skip() default false;
    }

    static class CartTests {
        @Test(name = "empty cart has total 0")
        void emptyCart() { check(0 == 0); }

        @Test
        void addItem() { check(2 + 2 == 4); }

        @Test(name = "discount above 100 percent", skip = true)
        void hugeDiscount() { check(false); }

        @Test(name = "tax is added")
        void tax() { check(100 * 1.18 == 118); }

        void helper() { }                       // no @Test, so the runner ignores it

        static void check(boolean ok) { if (!ok) throw new AssertionError("check failed"); }
    }

    public static void main(String[] args) throws Exception {
        CartTests suite = new CartTests();
        int pass = 0, fail = 0, skip = 0;
        Method[] methods = CartTests.class.getDeclaredMethods();
        java.util.Arrays.sort(methods, java.util.Comparator.comparing(Method::getName));
        for (Method m : methods) {
            Test t = m.getAnnotation(Test.class);
            if (t == null) continue;
            String name = t.name().isEmpty() ? m.getName() : t.name();
            if (t.skip()) { System.out.println("SKIP " + name); skip++; continue; }
            try {
                m.invoke(suite);
                System.out.println("PASS " + name); pass++;
            } catch (InvocationTargetException e) {
                System.out.println("FAIL " + name + ": " + e.getCause().getMessage()); fail++;
            }
        }
        System.out.println(pass + " passed, " + fail + " failed, " + skip + " skipped");
    }
}
''', 'A tiny test runner built from a custom annotation', trace=False),
    'reflect': j('''
import java.lang.reflect.*;
import java.util.*;

class Main {
    record Order(String id, int qty, double price) {
        double total() { return qty * price; }
    }

    public static void main(String[] args) throws Exception {
        Class<?> c = Order.class;                          // or Class.forName("Main$Order")
        System.out.println("name: " + c.getSimpleName() + ", record? " + c.isRecord());

        for (RecordComponent rc : c.getRecordComponents()) {
            System.out.println("component " + rc.getName() + " : " + rc.getType().getSimpleName());
        }

        Order o = (Order) c.getDeclaredConstructor(String.class, int.class, double.class).newInstance("A-1", 3, 49.5);
        Method total = c.getDeclaredMethod("total");
        System.out.println("total() called by name: " + total.invoke(o));

        Field qty = c.getDeclaredField("qty");
        System.out.println("field qty is " + Modifier.toString(qty.getModifiers()));
    }
}
''', 'Looking inside a class at run time', trace=False),
    'final': sh({'Main.java': '''
import java.lang.reflect.Field;

class Main {
    static class Config {
        private final String env = new String("prod");
    }

    public static void main(String[] args) throws Exception {
        Config c = new Config();
        Field f = Config.class.getDeclaredField("env");
        f.setAccessible(true);
        f.set(c, "test");                     // changing a final field
        System.out.println("env is now " + f.get(c));
    }
}
'''}, 'javac Main.java && echo "--- Java 27, default ---" && java Main 2>&1 && echo "--- Java 27, --illegal-final-field-mutation=deny ---" && java --illegal-final-field-mutation=deny Main 2>&1 | head -1',
        'Java 26 and 27 warn when reflection changes a final field (JEP 500)', jdk=27,
        shown='$ java Main\n$ java --illegal-final-field-mutation=deny Main', replace=HASH),
    'opens': j('''
import java.lang.reflect.Field;

class Main {
    public static void main(String[] args) throws Exception {
        Field value = String.class.getDeclaredField("value");
        System.out.println("found the private field: " + value.getName());
        value.setAccessible(true);            // java.base does not open java.lang to us
        System.out.println("never printed");
    }
}
''', 'Strong encapsulation: the JDK keeps its private parts private', expect='throw', trace=False, replace=HASH),
    'proxy': j('''
import java.lang.reflect.*;
import java.util.*;

class Main {
    interface PaymentService {
        String pay(String user, int amount);
        int balance(String user);
    }

    static class RealPayments implements PaymentService {
        public String pay(String user, int amount) { return "paid " + amount + " for " + user; }
        public int balance(String user) { return 500; }
    }

    @SuppressWarnings("unchecked")
    static <T> T logged(T target, Class<T> type) {
        InvocationHandler h = (proxy, method, args) -> {
            System.out.println("-> " + method.getName() + Arrays.toString(args));
            Object result = method.invoke(target, args);
            System.out.println("<- " + result);
            return result;
        };
        return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] { type }, h);
    }

    public static void main(String[] args) {
        PaymentService svc = logged(new RealPayments(), PaymentService.class);
        svc.pay("asha", 120);
        svc.balance("asha");
        System.out.println("is a proxy: " + Proxy.isProxyClass(svc.getClass()));
    }
}
''', 'A dynamic proxy that logs every call', trace=False),
    'modules': sh({'src/com.shop.core/module-info.java': CORE_INFO, 'src/com.shop.core/com/shop/core/api/Prices.java': PRICES,
                   'src/com.shop.core/com/shop/core/internal/TaxTable.java': TAX, 'src/com.shop.app/module-info.java': APP_INFO,
                   'src/com.shop.app/com/shop/app/Main.java': '''
package com.shop.app;

import com.shop.core.api.Prices;

public class Main {
    public static void main(String[] args) {
        System.out.println("100 with tax = " + Prices.withTax(100));
        System.out.println("running in module " + Main.class.getModule().getName());
    }
}
'''}, 'javac -d out --module-source-path src -m com.shop.app && java -p out -m com.shop.app/com.shop.app.Main && echo "--- what depends on what (jdeps) ---" && jdeps --module-path out -s -m com.shop.app',
        'Two modules: a core library and an app',
        shown='$ javac -d out --module-source-path src -m com.shop.app\n$ java -p out -m com.shop.app/com.shop.app.Main     # -p is the module path\n$ jdeps --module-path out -s -m com.shop.app'),
    'notexported': sh({'src/com.shop.core/module-info.java': CORE_INFO, 'src/com.shop.core/com/shop/core/api/Prices.java': PRICES,
                       'src/com.shop.core/com/shop/core/internal/TaxTable.java': TAX, 'src/com.shop.app/module-info.java': APP_INFO,
                       'src/com.shop.app/com/shop/app/Main.java': '''
package com.shop.app;

import com.shop.core.internal.TaxTable;     // not exported by com.shop.core

public class Main {
    public static void main(String[] args) {
        System.out.println(TaxTable.rate());
    }
}
'''}, 'javac -d out --module-source-path src -m com.shop.app 2>&1 | head -1',
        'Using a package that is not exported', keep=['src/com.shop.app/com/shop/app/Main.java'],
        shown='$ javac -d out --module-source-path src -m com.shop.app'),
    'jlink': sh({'src/com.shop.core/module-info.java': CORE_INFO, 'src/com.shop.core/com/shop/core/api/Prices.java': PRICES,
                 'src/com.shop.core/com/shop/core/internal/TaxTable.java': TAX, 'src/com.shop.app/module-info.java': APP_INFO,
                 'src/com.shop.app/com/shop/app/Main.java': '''
package com.shop.app;

public class Main {
    public static void main(String[] args) {
        System.out.println("hello from a custom runtime: " + com.shop.core.api.Prices.withTax(100));
    }
}
'''}, 'javac -d out --module-source-path src -m com.shop.app && jlink -p out --add-modules com.shop.app --strip-debug --no-header-files --no-man-pages --output shopjre && ./shopjre/bin/java --list-modules && ./shopjre/bin/java -m com.shop.app/com.shop.app.Main && echo "size of the custom runtime: $(du -sm shopjre | cut -f1) MB" && echo "size of the full JDK: $(du -sm $(dirname $(dirname $(command -v java))) | cut -f1) MB"',
        'jlink builds a small runtime with only the modules you need', keep=['src/com.shop.app/module-info.java', 'src/com.shop.app/com/shop/app/Main.java'],
        shown='$ jlink -p out --add-modules com.shop.app --strip-debug --no-header-files --no-man-pages --output shopjre\n$ ./shopjre/bin/java --list-modules\n$ ./shopjre/bin/java -m com.shop.app/com.shop.app.Main\n$ du -sm shopjre'),
    'importmodule': j('''
import module java.sql;            // Java 25: every exported package of java.sql, plus java.xml and java.logging

void main() throws Exception {
    // Connection, DriverManager and SQLException come from java.sql
    // List and Map come from java.base, which compact source files import automatically
    List<String> drivers = DriverManager.drivers().map(d -> d.getClass().getSimpleName()).toList();
    System.out.println("JDBC drivers on the classpath: " + drivers.size());
    Map<String, Class<?>> types = Map.of("Connection", Connection.class, "SQLException", SQLException.class);
    types.forEach((k, v) -> System.out.println(k + " lives in " + v.getPackageName()));
}
''', 'import module brings in a whole module at once', trace=False),
    'ambiguous': j('''
import module java.sql;

void main() {
    Date today = new Date(0);       // java.util.Date or java.sql.Date?
    System.out.println(today);
}
''', 'Two modules export a class with the same name', expect='compile'),
    'fixambiguous': j('''
import module java.sql;
import java.sql.Date;               // a single type import wins over module imports

void main() {
    Date day = Date.valueOf("2026-10-24");
    System.out.println(day + " is a " + day.getClass().getName());
}
''', 'A single type import settles it'),
    'scenario': j('''
import java.lang.annotation.*;
import java.lang.reflect.*;
import java.util.*;

class Main {
    @Retention(RetentionPolicy.RUNTIME) @Target(ElementType.RECORD_COMPONENT) @interface NotBlank { }
    @Retention(RetentionPolicy.RUNTIME) @Target(ElementType.RECORD_COMPONENT) @interface Range { int min(); int max(); }

    record SignUp(@NotBlank String name, @NotBlank String email, @Range(min = 13, max = 120) int age) { }

    static List<String> validate(Record r) throws Exception {
        List<String> errors = new ArrayList<>();
        for (RecordComponent rc : r.getClass().getRecordComponents()) {
            Object value = rc.getAccessor().invoke(r);
            if (rc.isAnnotationPresent(NotBlank.class) && (value == null || value.toString().isBlank())) {
                errors.add(rc.getName() + " must not be blank");
            }
            Range range = rc.getAnnotation(Range.class);
            if (range != null && ((int) value < range.min() || (int) value > range.max())) {
                errors.add(rc.getName() + " must be between " + range.min() + " and " + range.max());
            }
        }
        return errors;
    }

    public static void main(String[] args) throws Exception {
        System.out.println(validate(new SignUp("Asha", "asha@shop.test", 29)));
        System.out.println(validate(new SignUp(" ", "ravi@shop.test", 9)));
    }
}
''', 'A validator in 30 lines, the idea behind Bean Validation', trace=False),
}

DG = {
    'reflect': {'t': 'How a framework uses annotations and reflection', 'w': 900, 'h': 280, 'mw': 640,
        'n': [['src', 30, 40, 200, 60, '@Test void addItem()', {'c': 1, 'sub': 'you write this'}],
              ['cls', 30, 170, 200, 60, 'CartTests.class', {'c': 2, 'sub': 'annotation kept (RUNTIME)'}],
              ['scan', 340, 40, 220, 60, 'getDeclaredMethods()', {'c': 3, 'sub': 'the framework looks around'}],
              ['ann', 340, 170, 220, 60, 'getAnnotation(Test)', {'c': 3, 'sub': 'is this a test?'}],
              ['inv', 660, 40, 210, 60, 'method.invoke(obj)', {'c': 4, 'sub': 'call it by name'}],
              ['rep', 660, 170, 210, 60, 'PASS or FAIL', {'c': 5, 'sub': 'the report'}]],
        'e': [['src', 'cls', {'t': 'javac', 'id': 'a1'}], ['cls', 'scan', {'t': 'load', 'id': 'a2'}], ['scan', 'ann', {'id': 'a3'}],
              ['ann', 'inv', {'t': 'yes', 'id': 'a4'}], ['inv', 'rep', {'id': 'a5'}]],
        'st': [[['src'], 'You only add an annotation. It does nothing by itself, it is a label.'],
               [['cls', 'a1'], 'javac stores the label in the class file because the annotation has RUNTIME retention.'],
               [['scan', 'a2'], 'At run time the framework, such as JUnit, Spring or Jackson, asks the Class object for its methods or fields.'],
               [['ann', 'a3'], 'For each method it asks: does this have @Test? Methods without the label are ignored.'],
               [['inv', 'a4'], 'It calls the labelled method by name with Method.invoke, without your code ever calling it.'],
               [['rep', 'a5'], 'Exceptions thrown inside are caught and turned into a report. This is the whole trick behind most Java frameworks.']]},
    'modules': {'t': 'Modules decide what other code may see', 'w': 900, 'h': 300, 'mw': 640,
        'g': [[20, 20, 380, 260, 'module com.shop.core', 2], [500, 20, 380, 260, 'module com.shop.app', 1]],
        'n': [['api', 50, 60, 320, 60, 'com.shop.core.api', {'c': 4, 'sub': 'exported'}],
              ['int', 50, 180, 320, 60, 'com.shop.core.internal', {'c': 5, 'sub': 'not exported'}],
              ['main', 530, 60, 320, 60, 'com.shop.app.Main', {'c': 1, 'sub': 'requires com.shop.core'}],
              ['bad', 530, 180, 320, 60, 'import ...internal.TaxTable', {'c': 5, 'sub': 'compile error: package does not exist'}]],
        'e': [['main', 'api', {'t': 'allowed', 'id': 'ok'}], ['api', 'int', {'t': 'inside the module', 'id': 'in'}], ['bad', 'int', {'t': 'not visible', 'id': 'no', 'd': 1}]],
        'st': [[['api', 'int'], 'A module is a group of packages with a name and a module-info.java file.'],
               [['main', 'api', 'ok'], 'com.shop.app says requires com.shop.core, and core exports its api package, so Main can use Prices.'],
               [['api', 'int', 'in'], 'Inside its own module, Prices may use the internal package freely.'],
               [['bad', 'int', 'no'], 'Outside the module, the internal package does not exist, even though TaxTable is public. public no longer means public to the whole world.']]},
}

PARTS = [
    part('builtin', '🏷️', 'Annotations: labels the compiler and tools can read', '''
<p>An <b>annotation</b> is a label that starts with <code>@</code>. It does not change what your code does by itself. The compiler, build tools or frameworks read the label and act on it, like a "fragile" sticker on a parcel that tells the courier how to handle it.</p>
[[override]]
<p>Without <code>@Override</code> that typo would compile and silently create a new method that nothing ever calls. With it, the compiler catches the mistake at once.</p>
[[deprecated]]
<div class="tw"><table class="jt"><tr><th>Annotation</th><th>What it tells the compiler</th></tr>
<tr><td><code>@Override</code></td><td>this must override or implement a method, or fail</td></tr>
<tr><td><code>@Deprecated(since, forRemoval)</code></td><td>warn everyone who still uses this</td></tr>
<tr><td><code>@SuppressWarnings("...")</code></td><td>I know, stop warning me about this here</td></tr>
<tr><td><code>@FunctionalInterface</code></td><td>this interface must have exactly one abstract method</td></tr>
<tr><td><code>@SafeVarargs</code></td><td>this generic varargs method does not misuse its array</td></tr></table></div>
''', kw=['annotation', '@Override', '@Deprecated', 'forRemoval', '@SuppressWarnings', '@FunctionalInterface', '@SafeVarargs', 'metadata']),
    part('custom', '🧪', 'Writing your own annotation', '''
<p>You declare an annotation with <code>@interface</code>. Two meta annotations decide how it behaves. <code>@Retention</code> says how long it lives: only in the source (SOURCE), in the class file (CLASS, the default), or also at run time (RUNTIME). <code>@Target</code> says where it may be written, such as on methods, fields, classes or record components.</p>
[[custom]]
<div class="viz" data-viz="flow" data-k="reflect"></div>
<div class="note">JUnit 5's <code>@Test</code>, <code>@DisplayName</code> and <code>@Disabled</code> work exactly like this, with many more features. So do Spring's <code>@GetMapping</code> and Jackson's <code>@JsonProperty</code>.</div>
''', kw=['@interface', 'custom annotation', '@Retention', 'RetentionPolicy.RUNTIME', '@Target', 'ElementType', 'annotation elements', 'default values', 'test runner', 'JUnit']),
    part('reflection', '🔍', 'Reflection: looking at classes while the program runs', '''
<p><b>Reflection</b> lets code examine and use classes it did not know about when it was compiled. Every loaded class has a <code>Class</code> object that lists its fields, methods, constructors and, for records, its components. Frameworks use it to create objects, fill fields from JSON and call methods by name.</p>
[[reflect]]
<p>Reflection is powerful but has a cost. Calls are checked at run time instead of compile time, so a typo in a method name becomes a <code>NoSuchMethodException</code>, and the code is harder to read. Use it in libraries and tools, not in everyday business logic.</p>
<p>Since Java 9 the JDK protects its own internals. Reflection may not open private parts of a module that does not allow it.</p>
[[opens]]
<p>Changing a <code>final</code> field with reflection still works in your own code, but Java 26 started warning about it (JEP 500, "prepare to make final mean final"). A future release will block it unless you allow it with <code>--enable-final-field-mutation</code>. The JVM can then trust that final fields never change and optimise better.</p>
[[final]]
''', kw=['reflection', 'Class object', 'getDeclaredMethods', 'getDeclaredField', 'Method.invoke', 'getRecordComponents', 'setAccessible', 'InaccessibleObjectException', 'final field mutation', 'JEP 500', '--enable-final-field-mutation']),
    part('proxy', '🪞', 'Dynamic proxies: how mocks and frameworks wrap your objects', '''
<p>A <b>dynamic proxy</b> is an object the JVM creates at run time that implements one or more interfaces. Every call on it goes to one handler method, which can log, time, check permissions or forward the call. Spring uses proxies for <code>@Transactional</code>, and older mocking libraries used them for mocks.</p>
[[proxy]]
<div class="tip">java.lang.reflect.Proxy only works with interfaces. Libraries such as Mockito and Spring generate subclasses with bytecode tools when they need to wrap plain classes, which is one reason the Class-File API (final in Java 24) was added to the JDK.</div>
''', kw=['dynamic proxy', 'Proxy.newProxyInstance', 'InvocationHandler', 'AOP', 'logging wrapper', 'Mockito', 'Spring', '@Transactional', 'Class-File API']),
    part('modules', '📦', 'The module system (Java 9)', '''
<p>Before Java 9, a <code>public</code> class in any JAR could be used by any other JAR. Big programs ended up depending on each other's internals. A <b>module</b> fixes this. It is a named group of packages with a <code>module-info.java</code> file that says which packages it <b>exports</b> and which modules it <b>requires</b>.</p>
<div class="viz" data-viz="flow" data-k="modules"></div>
[[modules]]
[[notexported]]
<div class="tw"><table class="jt"><tr><th>module-info line</th><th>Meaning</th></tr>
<tr><td><code>requires m;</code></td><td>I use module m</td></tr>
<tr><td><code>requires transitive m;</code></td><td>I use m, and so does anyone who requires me</td></tr>
<tr><td><code>exports p;</code></td><td>other modules may use package p at compile and run time</td></tr>
<tr><td><code>opens p;</code></td><td>frameworks may use deep reflection on p, for example JSON mapping</td></tr>
<tr><td><code>uses S;</code> and <code>provides S with Impl;</code></td><td>plug in implementations with ServiceLoader</td></tr></table></div>
<p>The JDK itself is split into about 70 modules. That lets <b>jlink</b> build a runtime with only the modules an app needs, which makes container images much smaller.</p>
[[jlink]]
''', kw=['JPMS', 'module system', 'module-info.java', 'requires', 'exports', 'opens', 'requires transitive', 'module path', 'jdeps', 'jlink', 'custom runtime', 'ServiceLoader', 'strong encapsulation']),
    part('importmodule', '📥', 'Module import declarations (Java 25)', '''
<p>A long list of imports at the top of a file is noise, especially for beginners and small scripts. Java 25 made <b>module import declarations</b> final (JEP 511). <code>import module java.sql;</code> imports every public type from every package that the java.sql module exports, and from the modules it requires transitively. Compact source files, the ones with a bare <code>void main()</code>, import <code>java.base</code> this way automatically.</p>
[[importmodule]]
<p>If two imported modules export a class with the same simple name, using that name is an error. The fix is one ordinary import, which always beats a module import.</p>
[[ambiguous]]
[[fixambiguous]]
<div class="note">Your code does not need to be a module to use <code>import module</code>. It works in ordinary classes on the classpath too.</div>
''', kw=['import module', 'module import declaration', 'JEP 511', 'Java 25', 'java.base', 'ambiguous import', 'single type import', 'compact source files']),
    part('scenario', '🎬', 'Real world scenario: validating a sign up form', '''
<div class="scenario"><b>The situation</b>A sign up API receives a name, an email and an age. Every endpoint repeats the same if statements to check them, and the rules drift apart.</div>
[[scenario]]
<p>The rules now live next to the data as annotations, and one generic method checks any record. This is the same idea as Jakarta Bean Validation (<code>@NotBlank</code>, <code>@Min</code>, <code>@Max</code>), which Spring runs automatically on request bodies.</p>
''', kw=['validation', 'Bean Validation', 'Jakarta Validation', '@NotBlank', 'record component annotations', 'form validation', 'API input checks']),
]

INFO = {'title': 'Labels, mirrors and fences', 'panels': [
    panel([['e', '🏷️'], ['t', '@Override', {'b': 1}]], 'Annotations', 'Labels that tools read.', 'RUNTIME retention keeps them for reflection.'),
    panel([['e', '🔍'], ['t', 'm.invoke(obj)', {'b': 1}]], 'Reflection', 'Look inside classes while running.', 'This is how frameworks find your code.'),
    panel([['e', '📦'], ['t', 'exports com.shop.api', {'b': 1, 'size': 11}]], 'Modules', 'Only exported packages are visible.', 'jlink builds a smaller runtime.'),
    panel([['e', '📥'], ['t', 'import module java.sql;', {'b': 1, 'size': 11}]], 'Java 25', 'One line imports a whole module.', 'A single type import settles name clashes.')],
    'remember': 'Annotations are labels, reflection reads them at run time, proxies wrap interfaces, and modules decide which packages other code may see. Java 25 adds import module, and Java 26 warns before final fields can be changed by reflection.'}

REAL = [
    ['🧪', 'JUnit', 'Finds your tests by scanning classes for <code>@Test</code> with reflection, then calls each method by name and reports the result.'],
    ['🌱', 'Spring Boot', 'Reads <code>@RestController</code> and <code>@GetMapping</code> to build its routes, and wraps <code>@Transactional</code> beans in proxies that start and commit transactions.'],
    ['🐳', 'A team shipping containers', 'Used jdeps and jlink to build a runtime with only six modules, so their image shrank by more than half.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to annotations, reflection, dynamic proxies and the module system, including module imports from Java 25.',
        'Annotations, reflection, dynamic proxies और module system में स्वागत है, Java 25 के module imports सहित।',
        'Annotations, reflection, proxies ಮತ್ತು module system ಗೆ ಸ್ವಾಗತ.',
        'Annotations, reflection, proxies ଏବଂ module system କୁ ସ୍ୱାଗତ।',
        'مرحبًا بك في التعليقات التوضيحية والانعكاس والوكلاء الديناميكيين ونظام الوحدات، ومنها استيراد الوحدات في Java 25.',
        'Willkommen zu Annotationen, Reflection, dynamischen Proxys und dem Modulsystem, einschließlich Modul-Importen aus Java 25.'),
    say('builtin', 'Annotations', 'An annotation is a label. Override makes the compiler check that a method really overrides one, and Deprecated warns users of old code.',
        'Annotation एक label है। Override से compiler जाँचता है कि method सच में override करता है, और Deprecated पुराने code के users को चेतावनी देता है।',
        'Annotation ಒಂದು label. Override compiler ಪರಿಶೀಲನೆ ಮಾಡಿಸುತ್ತದೆ, Deprecated ಎಚ್ಚರಿಸುತ್ತದೆ.',
        'Annotation ଏକ label। Override compiler ଯାଞ୍ଚ କରାଏ, Deprecated ଚେତାବନୀ ଦିଏ।',
        'التعليق التوضيحي ملصق، فيجعل Override المترجم يتحقق من أن الدالة تتجاوز فعلًا، ويحذر Deprecated مستخدمي الشيفرة القديمة.',
        'Eine Annotation ist ein Etikett. Override lässt den Compiler prüfen, ob wirklich überschrieben wird, und Deprecated warnt Nutzer alten Codes.'),
    say('custom', 'Custom annotations', 'Declare your own with at interface. Retention RUNTIME keeps it for reflection, and Target says where it may be used.',
        'at interface से अपना annotation बनाएँ। Retention RUNTIME उसे reflection के लिए रखता है, और Target बताता है कि कहाँ लगाया जा सकता है।',
        'at interface ಮೂಲಕ ನಿಮ್ಮದೇ annotation. Retention RUNTIME reflection ಗೆ ಉಳಿಸುತ್ತದೆ.',
        'at interface ଦ୍ୱାରା ନିଜ annotation। Retention RUNTIME reflection ପାଇଁ ରଖେ।',
        'عرّف تعليقك الخاص باستخدام @interface، فيبقيه Retention RUNTIME للانعكاس، ويحدد Target أماكن استخدامه.',
        'Eigene Annotationen deklarierst du mit @interface. Retention RUNTIME behält sie für Reflection, Target legt fest, wo sie stehen dürfen.'),
    say('reflection', 'Reflection', 'Reflection reads fields and methods at run time and can call a method by name. The JDK blocks access to its own private parts, and Java 26 warns when final fields are changed.',
        'Reflection run time पर fields और methods पढ़ता है और नाम से method बुला सकता है। JDK अपने private हिस्से बंद रखता है, और Java 26 final fields बदलने पर चेतावनी देता है।',
        'Reflection run time ನಲ್ಲಿ fields, methods ಓದುತ್ತದೆ. Java 26 final fields ಬದಲಾದರೆ ಎಚ್ಚರಿಸುತ್ತದೆ.',
        'Reflection run time ରେ fields, methods ପଢ଼େ। Java 26 final fields ବଦଳିଲେ ଚେତାବନୀ ଦିଏ।',
        'يقرأ الانعكاس الحقول والدوال وقت التشغيل ويستدعي دالة باسمها، وتمنع JDK الوصول إلى أجزائها الخاصة، وتحذر Java 26 عند تغيير الحقول النهائية.',
        'Reflection liest Felder und Methoden zur Laufzeit und ruft Methoden per Name auf. Das JDK schützt seine Interna, und Java 26 warnt beim Ändern finaler Felder.'),
    say('proxy', 'Dynamic proxies', 'A dynamic proxy implements an interface at run time and sends every call to one handler, which is how logging and transactions are added around your code.',
        'Dynamic proxy run time पर interface implement करता है और हर call एक handler को भेजता है, ऐसे ही logging और transactions जोड़े जाते हैं।',
        'Dynamic proxy run time ನಲ್ಲಿ interface implement ಮಾಡಿ ಪ್ರತಿ call ಒಂದು handler ಗೆ ಕಳುಹಿಸುತ್ತದೆ.',
        'Dynamic proxy run time ରେ interface implement କରି ପ୍ରତି call ଗୋଟିଏ handler କୁ ପଠାଏ।',
        'الوكيل الديناميكي ينفذ واجهة وقت التشغيل ويرسل كل استدعاء إلى معالج واحد، وهكذا تُضاف السجلات والمعاملات حول شيفرتك.',
        'Ein dynamischer Proxy implementiert zur Laufzeit ein Interface und leitet jeden Aufruf an einen Handler, so kommen Logging und Transaktionen dazu.'),
    say('modules', 'Modules', 'A module lists the packages it exports and the modules it requires. Packages that are not exported cannot be used from outside, even if their classes are public.',
        'Module बताता है कि वह कौन से packages export करता है और किन modules को require करता है। जो export नहीं हैं, वे बाहर से इस्तेमाल नहीं हो सकते।',
        'Module exports ಮತ್ತು requires ಪಟ್ಟಿ ಮಾಡುತ್ತದೆ. Export ಆಗದ packages ಹೊರಗಿನಿಂದ ಬಳಸಲಾಗದು.',
        'Module exports ଏବଂ requires ତାଲିକା କରେ। Export ନଥିବା packages ବାହାରୁ ବ୍ୟବହାର ହୁଏ ନାହିଁ।',
        'تذكر الوحدة الحزم التي تصدّرها والوحدات التي تحتاجها، ولا يمكن استخدام الحزم غير المصدّرة من الخارج حتى لو كانت أصنافها عامة.',
        'Ein Modul nennt die exportierten Pakete und benötigten Module. Nicht exportierte Pakete sind von außen unbenutzbar, auch wenn ihre Klassen public sind.'),
    say('importmodule', 'Module imports', 'In Java 25, import module java dot sql imports every exported type of that module. If two names clash, one normal import decides.',
        'Java 25 में import module java dot sql उस module के सभी exported types import करता है। नाम टकराएँ तो एक सामान्य import तय करता है।',
        'Java 25 ನಲ್ಲಿ import module ಒಂದೇ ಸಾಲಿನಲ್ಲಿ module ಅನ್ನು import ಮಾಡುತ್ತದೆ.',
        'Java 25 ରେ import module ଗୋଟିଏ ଧାଡ଼ିରେ module import କରେ।',
        'في Java 25 يستورد import module java.sql كل الأنواع المصدّرة من تلك الوحدة، وإذا تعارض اسمان يحسم الأمر استيراد عادي واحد.',
        'In Java 25 importiert import module java.sql alle exportierten Typen des Moduls. Bei Namenskonflikten entscheidet ein normaler Import.'),
    say('scenario', 'Scenario', 'Validation rules are written as annotations on a record, and one method checks any record with reflection.',
        'Validation के नियम record पर annotations के रूप में लिखे जाते हैं, और एक method reflection से किसी भी record को जाँचता है।',
        'Validation ನಿಯಮಗಳು record ಮೇಲೆ annotations ಆಗಿ, ಒಂದು method reflection ನಿಂದ ಪರಿಶೀಲಿಸುತ್ತದೆ.',
        'Validation ନିୟମ record ଉପରେ annotations ଭାବେ, ଗୋଟିଏ method reflection ଦ୍ୱାରା ଯାଞ୍ଚ କରେ।',
        'تُكتب قواعد التحقق تعليقات على السجل، وتفحص دالة واحدة أي سجل بالانعكاس.',
        'Validierungsregeln stehen als Annotationen am Record, und eine Methode prüft jeden Record per Reflection.'),
]

QUIZ = [
    quiz('e', 'What does <code>@Override</code> do?', ['Makes the compiler fail if the method does not really override one', 'Makes the method run faster', 'Hides the parent method at run time', 'Makes the method final'], 0, 'A safety check.', 'It turns a silent typo into a compile error.'),
    quiz('e', 'Which retention keeps an annotation available to reflection?', ['RetentionPolicy.RUNTIME', 'RetentionPolicy.SOURCE', 'RetentionPolicy.CLASS', 'No retention is needed'], 0, 'How long it lives.', 'CLASS is the default and is not visible through reflection.'),
    quiz('e', 'Which file declares a Java module?', ['module-info.java', 'pom.xml', 'MANIFEST.MF', 'package-info.java'], 0, 'At the root of the module source.', 'It lists requires, exports, opens, uses and provides.'),
    quiz('m', 'Module core exports <code>core.api</code> but not <code>core.internal</code>. What happens when another module imports a public class from core.internal?', ['A compile error, because the package cannot be seen from outside', 'It works because the class is public', 'It works but prints a warning', 'It fails only at run time'], 0, 'Exports decide.', 'public now means public inside the module, plus whatever is exported.'),
    quiz('m', 'What does <code>import module java.sql;</code> import?', ['Every public type in every package exported by java.sql and the modules it requires transitively', 'Only java.sql.Connection', 'Every class in the JDK', 'Nothing, it is a comment'], 0, 'JEP 511.', 'java.sql requires java.xml and java.logging transitively, so those come too.'),
    quiz('m', 'Why can java.lang.reflect.Proxy not wrap a plain class without an interface?', ['It creates a class that implements interfaces, it cannot extend a given class', 'Classes are final by default', 'Reflection cannot see classes', 'It can, there is no limit'], 0, 'Proxy implements interfaces.', 'Libraries generate subclasses with bytecode tools for that case.'),
    quiz('m', 'Why does <code>String.class.getDeclaredField("value").setAccessible(true)</code> fail?', ['java.base does not open java.lang to your code', 'The field does not exist', 'Strings are immutable', 'setAccessible was removed'], 0, 'Strong encapsulation.', 'Only --add-opens on the command line could allow it, and that should be a last resort.'),
    quiz('h', 'What changes in Java 26 when reflection sets a final field?', ['It still works but prints a warning, as a step before blocking it', 'It is blocked with an exception by default', 'Nothing changes', 'The field becomes non final'], 0, 'JEP 500.', 'Use --enable-final-field-mutation to allow it without warnings, or --illegal-final-field-mutation=deny to try the future behaviour.'),
    quiz('h', 'Two module imports both export a class named Date. How do you use java.sql.Date?', ['Add <code>import java.sql.Date;</code>, which beats module imports', 'Remove one of the module imports, nothing else works', 'Rename the class', 'Use import static'], 0, 'Single type imports win.', 'That is the rule in JEP 511.'),
    quiz('h', 'What does jlink produce?', ['A runtime image with only the modules your app needs', 'A native executable without a JVM', 'A fat JAR', 'A Docker image'], 0, 'Smaller runtime.', 'The image still contains a JVM, but only the listed modules.'),
    quiz('x', 'What does this print?', ['2', '3', '0', '1'], 0, 'Count methods with the annotation.', 'Only a and c carry @Deprecated, which has RUNTIME retention.', code='class Api {\n    @Deprecated void a() { }\n    void b() { }\n    @Deprecated void c() { }\n}\n\nvoid main() {\n    long n = java.util.Arrays.stream(Api.class.getDeclaredMethods()).filter(m -> m.isAnnotationPresent(Deprecated.class)).count();\n    System.out.println(n);\n}', run=True),
    quiz('x', 'What does this print?', ['java.base', 'java.lang', 'unnamed', 'null'], 0, 'Which module holds String?', 'Every core class lives in a named module of the JDK.', code='System.out.println(String.class.getModule().getName());', run=True),
]

CALC = [
    calc('e', 'A class has 3 methods marked @Test, one of them with skip = true. How many tests run?', '2', 'Skipped tests do not run.', ['<span class="eq">3 − 1 = 2</span>']),
    calc('e', 'How many record components does <code>record SignUp(String name, String email, int age)</code> have?', '3', 'Count the parameters in the header.', ['name, email and age.']),
    calc('m', 'A full JDK is 380 MB and a jlink runtime is 50 MB. What percent of the size is saved, to the nearest whole number?', '87', 'Saved divided by the original.', ['<span class="eq"><span class="fr"><i>380 − 50</i><i>380</i></span> = <span class="fr"><i>330</i><i>380</i></span> ≈ 0.868</span>', 'That is about 87 percent.']),
    calc('m', 'What does this print?', '3', 'Count the components with reflection.', ['RecordComponent[] has one entry per component.'], code='record Point3(int x, int y, int z) { }\n\nvoid main() {\n    System.out.println(Point3.class.getRecordComponents().length);\n}', run=True),
    calc('h', 'A logging proxy prints 2 lines per call. A test makes 15 calls. How many log lines appear?', '30', 'Two per call.', ['<span class="eq">15 × 2 = 30</span>']),
    calc('h', 'What does this print?', 'pay', 'The handler sees the method name.', ['The proxy sends the call to the handler, which returns the name of the method that was called.'], code='interface Svc { String pay(); }\n\nvoid main() {\n    Svc s = (Svc) java.lang.reflect.Proxy.newProxyInstance(Svc.class.getClassLoader(), new Class<?>[] { Svc.class }, (p, m, a) -> m.getName());\n    System.out.println(s.pay());\n}', run=True),
    calc('x', 'What does this print?', 'true', 'Which module are you in?', ['Code on the classpath belongs to the unnamed module, which has no name.'], code='System.out.println(getClass().getModule().getName() == null);', run=True),
]

T = {
    'slug': 'java-annotations-modules', 'title': 'Annotations, reflection and modules', 'short': 'Annotations and modules', 'emoji': '🏷️', 'module': MODULE, 'minutes': 24,
    'lead': 'Frameworks such as JUnit and Spring seem to call your code by magic. This chapter shows the real mechanism: annotations as labels, reflection to read them, and proxies to wrap objects. Then it covers the module system that protects code from misuse, jlink for small runtimes, module imports from Java 25, and the Java 26 warning about changing final fields.',
    'desc': 'Java annotations, custom annotations with Retention and Target, reflection, Method.invoke, record components, strong encapsulation, final field mutation warnings (JEP 500), dynamic proxies, the module system with module-info, exports and requires, jdeps, jlink and module import declarations (JEP 511).',
    'summary': 'Built in annotations, writing a custom @Test and a tiny test runner, reflection on records, InaccessibleObjectException, Java 26 and 27 final field warnings, a logging dynamic proxy, two real modules with exports, jdeps and jlink, import module in Java 25 and name clashes, and an annotation based validator.',
    'keywords': ['annotations', 'custom annotation', 'reflection', 'dynamic proxy', 'JPMS', 'module-info', 'jlink', 'jdeps', 'import module', 'JEP 511', 'JEP 500', 'Bean Validation', 'Java 25', 'Java 26'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
