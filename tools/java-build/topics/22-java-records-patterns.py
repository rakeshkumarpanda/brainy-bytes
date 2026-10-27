# Chapter 22: var, text blocks, switch expressions, records, sealed types, pattern matching for instanceof and switch, record patterns, unnamed variables and primitive patterns.
from kit import part, j, sh, show, say, quiz, calc, panel

MODULE = ('🚀', 'Modern Java', 'modern', 'Java 8 to Java 27: lambdas, streams, records, pattern matching, virtual threads, the JVM inside out, databases and HTTP, and every recent release explained with real work uses.')

CODES = {
    'var': j('''
import java.util.*;

class Main {
    public static void main(String[] args) {
        var browser = "chromium";                               // String
        var retries = 3;                                        // int
        var results = new HashMap<String, List<Integer>>();     // no need to repeat the long type
        results.computeIfAbsent("login", k -> new ArrayList<>()).add(420);

        for (var entry : results.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
        System.out.println(browser + " x" + retries);
        System.out.println(((Object) retries).getClass().getSimpleName());   // still a real, fixed type
    }
}
''', 'var lets the compiler write the type for you'),
    'var-bad': j('''
class Main {
    public static void main(String[] args) {
        var nothing;                     // needs an initial value
        var empty = null;                // null has no useful type
        var x = 10;
        x = "ten";                       // the type is fixed once chosen
    }
}
''', 'Where var is not allowed', expect='compile', note='Fields, method parameters and return types cannot use var either. It is only for local variables.'),
    'textblock': j('''
class Main {
    public static void main(String[] args) {
        String name = "Asha";
        int qty = 2;

        // Java 15: a text block keeps the layout, and quotes need no escaping
        String body = """
            {
              "customer": "%s",
              "items": [ { "sku": "TSHIRT-RED-M", "qty": %d } ],
              "note": "Ring the bell"
            }
            """.formatted(name, qty);
        System.out.print(body);

        String sql = """
            SELECT id, total
            FROM orders
            WHERE status = 'PAID' \\
            AND total > 500
            """;                                  // a backslash at the end of a line joins it with the next
        System.out.print(sql);
        System.out.println("""
            trailing space kept here:\\s|""");   // \\s keeps one space that would otherwise be trimmed
    }
}
''', 'Text blocks for JSON bodies and SQL'),
    'switch-old': j('''
class Main {
    public static void main(String[] args) {
        int status = 404;
        String kind;
        switch (status) {                    // old statement switch: easy to forget a break
            case 200:
            case 201:
                kind = "success";
            case 404:
                kind = "not found";
                break;
            default:
                kind = "other";
        }
        System.out.println(kind);
        status = 200;
        switch (status) { case 200: case 201: kind = "success"; case 404: kind = "not found"; break; default: kind = "other"; }
        System.out.println(kind + "   <- 200 fell through into the next case");
    }
}
''', 'The old switch and its fall through bug'),
    'switch-new': j('''
class Main {
    enum Env { DEV, QA, STAGING, PROD }

    public static void main(String[] args) {
        for (int status : new int[]{200, 201, 404, 503}) {
            String kind = switch (status) {          // Java 14: switch is an expression with a value
                case 200, 201, 204 -> "success";     // several labels, no fall through
                case 404 -> "not found";
                default -> {
                    String range = status >= 500 ? "server error" : "other";
                    yield range;                     // yield gives the value of a block
                }
            };
            System.out.println(status + " " + kind);
        }

        Env env = Env.QA;
        int workers = switch (env) {                 // no default needed: every enum constant is covered
            case DEV -> 1;
            case QA, STAGING -> 4;
            case PROD -> 16;
        };
        System.out.println(env + " workers=" + workers);
    }
}
''', 'Switch expressions: arrows, many labels, yield and exhaustive enums'),
    'record': j('''
import java.util.*;

class Main {
    // One line gives: private final fields, a constructor, accessors, equals, hashCode and toString
    record Product(String sku, String name, double price) {
        Product {                                         // compact constructor: validate the input
            if (price < 0) throw new IllegalArgumentException("price must not be negative: " + price);
            name = name.strip();                          // you may normalise parameters before they are stored
        }
        Product withPrice(double p) { return new Product(sku, name, p); }   // "withers" return a changed copy
        static Product free(String sku) { return new Product(sku, "Gift", 0); }
    }

    public static void main(String[] args) {
        Product a = new Product("TSHIRT-RED-M", "  Red T-shirt ", 499.0);
        Product b = new Product("TSHIRT-RED-M", "Red T-shirt", 499.0);
        System.out.println(a);
        System.out.println(a.name() + " costs " + a.price());
        System.out.println("equal by value: " + a.equals(b) + ", same object: " + (a == b));
        System.out.println(new HashSet<>(List.of(a, b)).size() + " product in the set");
        System.out.println(a.withPrice(399.0));
        System.out.println(Product.free("GIFT-01"));
        new Product("MUG", "Mug", -5);
    }
}
''', 'Records: data carriers with validation', expect='throw'),
    'record-shallow': j('''
import java.util.*;

class Main {
    record Order(String id, List<String> items) {
        Order {
            items = List.copyOf(items);       // defensive copy: callers cannot change the order later
        }
    }
    record Leaky(String id, List<String> items) {}

    public static void main(String[] args) {
        List<String> cart = new ArrayList<>(List.of("mug"));
        Order safe = new Order("ORD-1", cart);
        Leaky leaky = new Leaky("ORD-2", cart);
        cart.add("laptop");                    // the caller changes its own list afterwards
        System.out.println(safe);
        System.out.println(leaky + "   <- changed from outside");
    }
}
''', 'Records are only shallowly immutable'),
    'sealed': j('''
class Main {
    // Only these three may implement Payment. The compiler knows the full list.
    sealed interface Payment permits Card, Upi, Wallet {}
    record Card(String last4, double amount) implements Payment {}
    record Upi(String vpa, double amount) implements Payment {}
    record Wallet(String provider, double amount) implements Payment {}

    static double fee(Payment p) {
        return switch (p) {                     // no default: the switch is checked for completeness
            case Card c -> c.amount() * 0.02;
            case Upi u -> 0;
            case Wallet w -> w.amount() * 0.01;
        };
    }

    public static void main(String[] args) {
        System.out.println(fee(new Card("4242", 1000)));
        System.out.println(fee(new Upi("asha@okbank", 1000)));
        System.out.println(fee(new Wallet("PayFast", 1000)));
    }
}
''', 'Sealed interfaces list every allowed subtype'),
    'sealed-missing': j('''
class Main {
    sealed interface Payment permits Card, Upi, Wallet {}
    record Card(double amount) implements Payment {}
    record Upi(double amount) implements Payment {}
    record Wallet(double amount) implements Payment {}

    static double fee(Payment p) {
        return switch (p) {                     // Wallet was forgotten
            case Card c -> c.amount() * 0.02;
            case Upi u -> 0;
        };
    }

    public static void main(String[] args) { }
}
''', 'Forget a case and the compiler tells you', expect='compile'),
    'sealed-kinds': j('''
class Main {
    sealed abstract static class Account permits Savings, Current, Business {}
    static final class Savings extends Account {}          // final: no more subclasses
    static sealed class Current extends Account permits StudentCurrent {}   // sealed again, with its own list
    static final class StudentCurrent extends Current {}
    static non-sealed class Business extends Account {}    // open again: anyone may extend it
    static class StartupBusiness extends Business {}

    public static void main(String[] args) {
        Account[] all = { new Savings(), new StudentCurrent(), new StartupBusiness() };
        for (Account a : all) System.out.println(a.getClass().getSimpleName() + " is an Account");
        System.out.println(Account.class.isSealed() + " " + java.util.Arrays.toString(
            java.util.Arrays.stream(Account.class.getPermittedSubclasses()).map(Class::getSimpleName).toArray()));
    }
}
''', 'final, sealed and non-sealed subclasses'),
    'instanceof': j('''
class Main {
    static String describe(Object o) {
        // Old style: test, then cast
        if (o instanceof String) {
            String s = (String) o;
            return "old: text of length " + s.length();
        }
        // Java 16: test and bind a variable in one step
        if (o instanceof Integer n && n > 100) {           // n can be used right away in the same condition
            return "big number " + n;
        }
        if (!(o instanceof java.util.List<?> list)) {
            return "something else: " + o;
        }
        return "a list with " + list.size() + " items";    // list is in scope here because of the negation above
    }

    public static void main(String[] args) {
        System.out.println(describe("hello"));
        System.out.println(describe(500));
        System.out.println(describe(java.util.List.of(1, 2)));
        System.out.println(describe(7));
    }
}
''', 'Pattern matching for instanceof'),
    'switch-patterns': j('''
class Main {
    static String classify(Object o) {
        return switch (o) {
            case null -> "null, handled without a NullPointerException";
            case Integer i when i < 0 -> "negative int " + i;
            case Integer i -> "int " + i;
            case String s when s.isBlank() -> "blank text";
            case String s -> "text \\"" + s + "\\"";
            case int[] arr -> "int array of " + arr.length;
            default -> "other: " + o.getClass().getSimpleName();
        };
    }

    public static void main(String[] args) {
        Object[] inputs = { -4, 42, "   ", "PASS", new int[]{1, 2, 3}, 3.14, null };
        for (Object o : inputs) System.out.println(classify(o));
    }
}
''', 'Pattern matching for switch with guards and null'),
    'dominance': j('''
class Main {
    static String f(Object o) {
        return switch (o) {
            case CharSequence cs -> "chars";
            case String s -> "string";          // can never match: String is a CharSequence, and that case came first
            default -> "other";
        };
    }
    public static void main(String[] args) { }
}
''', 'Order matters: a case that can never match is an error', expect='compile'),
    'record-patterns': j('''
class Main {
    record Point(int x, int y) {}
    sealed interface Shape permits Circle, Rect {}
    record Circle(Point centre, int r) implements Shape {}
    record Rect(Point topLeft, Point bottomRight) implements Shape {}

    static int area(Shape s) {
        return switch (s) {
            case Circle(Point c, int r) -> (int) Math.round(Math.PI * r * r);
            // nested record pattern: pull the numbers straight out of both points
            case Rect(Point(var x1, var y1), Point(var x2, var y2)) -> Math.abs(x2 - x1) * Math.abs(y2 - y1);
        };
    }

    public static void main(String[] args) {
        System.out.println(area(new Circle(new Point(0, 0), 10)));
        System.out.println(area(new Rect(new Point(1, 1), new Point(4, 5))));

        Object o = new Point(3, 4);
        if (o instanceof Point(int x, int y) && x < y) {      // record patterns work with instanceof too
            System.out.println("point below the diagonal: " + x + "," + y);
        }
    }
}
''', 'Record patterns take a record apart'),
    'unnamed': j('''
import java.util.*;

class Main {
    record Order(String id, String customer, double total) {}

    public static void main(String[] args) {
        List<Order> orders = List.of(new Order("A1", "asha", 900), new Order("A2", "ravi", 120));

        int count = 0;
        for (Order _ : orders) count++;                          // Java 22: the variable is not needed
        System.out.println(count + " orders");

        for (Order o : orders) {
            if (o instanceof Order(_, var who, var total) && total > 500) {   // ignore the id
                System.out.println("big order from " + who);
            }
        }
        try {
            Integer.parseInt("12a");
        } catch (NumberFormatException _) {                      // the exception itself is not used
            System.out.println("not a number");
        }
        Map<String, Integer> hits = new TreeMap<>();
        List.of("x", "y", "x").forEach(k -> hits.merge(k, 1, (a, _) -> a + 1));
        System.out.println(hits);
    }
}
''', 'Unnamed variables and patterns with _ (Java 22)'),
    'primitive-patterns': j('''
void main() {
    // Java 27 preview (JEP 532): patterns over primitive types
    int[] codes = {200, 302, 404, 503, 1000};
    for (int code : codes) {
        String text = switch (code) {
            case int c when c >= 200 && c < 300 -> "success";
            case int c when c >= 300 && c < 400 -> "redirect";
            case int c when c >= 400 && c < 500 -> "client error";
            case int c when c >= 500 && c < 600 -> "server error";
            case int c -> "not an HTTP status: " + c;
        };
        IO.println(code + " " + text);
    }

    // instanceof with a primitive type checks that the value fits without losing information
    long big = 3_000_000_000L, small = 42;
    IO.println((big instanceof int) + " " + (small instanceof int));
    double d = 2.5;
    IO.println(d instanceof int i ? "whole number " + i : "has a fraction: " + d);
}
''', 'Primitive types in patterns (preview in Java 27)', jdk=27, preview=True),
    'scenario': j('''
import java.util.*;

class Main {
    // How a test framework can model every possible API outcome
    sealed interface ApiResult<T> permits Ok, ClientError, ServerError, NetworkError {}
    record Ok<T>(int status, T body) implements ApiResult<T> {}
    record ClientError<T>(int status, String message) implements ApiResult<T> {}
    record ServerError<T>(int status) implements ApiResult<T> {}
    record NetworkError<T>(String reason) implements ApiResult<T> {}

    record Order(String id, double total) {}

    static String report(ApiResult<Order> r) {
        return switch (r) {
            case Ok(int s, Order(var id, var total)) when total == 0 -> "WARN " + s + " order " + id + " has a zero total";
            case Ok(var s, Order(var id, var total)) -> "PASS " + s + " order " + id + " total " + total;
            case ClientError(var s, var msg) -> "FAIL " + s + " client error: " + msg;
            case ServerError(var s) when s == 503 -> "RETRY service unavailable";
            case ServerError(var s) -> "FAIL " + s + " server error";
            case NetworkError(var why) -> "RETRY network: " + why;
        };
    }

    public static void main(String[] args) {
        List<ApiResult<Order>> results = List.of(
            new Ok<>(201, new Order("ORD-7", 1499.0)), new Ok<>(200, new Order("ORD-8", 0)),
            new ClientError<>(422, "qty must be at least 1"), new ServerError<>(503), new ServerError<>(500),
            new NetworkError<>("connection reset"));
        results.forEach(r -> System.out.println(report(r)));
    }
}
''', 'Real world: every API outcome as a sealed type'),
}

DG = {
    'dop': {'t': 'Data oriented programming in three steps', 'w': 900, 'h': 230, 'mw': 640,
        'n': [['rec', 30, 60, 240, 100, 'record', {'c': 1, 'sub': 'model the data:\nfields, equals, toString'}],
              ['sea', 330, 60, 240, 100, 'sealed interface', {'c': 3, 'sub': 'list every\npossible kind'}],
              ['sw', 630, 60, 240, 100, 'switch with patterns', {'c': 2, 'sub': 'handle each kind,\nchecked for completeness'}]],
        'e': [['rec', 'sea', {'t': 'implements'}], ['sea', 'sw', {'t': 'is switched on'}]],
        'tx': [[450, 200, 'Add a new kind later, and every switch that forgot it stops compiling.', {'c': 6, 'b': 1}]],
        'st': [[['rec'], 'Records hold plain data with no boilerplate.'],
               [['sea', 'rec>sea'], 'A sealed interface says exactly which records exist, for example Ok, ClientError and ServerError.'],
               [['sw', 'sea>sw'], 'A switch with type and record patterns handles each one. Because the list is closed, the compiler can check that none is missing.']]},
}

PARTS = [
    part('var', '🏷️', 'var: let the compiler write the type', '''
<p><code>var</code> (Java 10) asks the compiler to work out the type of a <b>local variable</b> from the value on the right. The variable still has one fixed type. It is not like JavaScript, where a variable can hold anything.</p>
[[var]]
[[var-bad]]
<div class="tip">Use <code>var</code> when the type is obvious from the right side, such as <code>var users = new ArrayList&lt;User&gt;()</code>. Keep the type when it helps the reader, such as <code>int timeoutMs = config.get("timeout")</code>.</div>
''', kw=['var', 'local variable type inference', 'Java 10', 'type inference', 'cannot infer type']),
    part('text-blocks', '📜', 'Text blocks', '''
<p>A <b>text block</b> (Java 15) is a string that spans several lines between triple quotes. Indentation shared by all lines is removed, line breaks are kept, and double quotes need no escaping. It is perfect for JSON request bodies, SQL and expected HTML in tests.</p>
[[textblock]]
<div class="note">Two escapes exist only for text blocks: a backslash at the end of a line joins it with the next line, and <code>\\s</code> keeps a space that would otherwise be trimmed. <code>formatted(...)</code> fills in <code>%s</code> and <code>%d</code> placeholders.</div>
''', kw=['text block', 'triple quotes', 'multi-line string', 'Java 15', 'formatted', 'JSON body', 'stripIndent', 'escape']),
    part('switch', '🔀', 'Switch expressions', '''
<p>The old <code>switch</code> statement falls through to the next case unless you remember <code>break</code>. That single missing word has caused many real bugs.</p>
[[switch-old]]
<p>Java 14 made <code>switch</code> an <b>expression</b>: it produces a value, the arrow form never falls through, one case can list several labels, and <code>yield</code> returns a value from a block. Over an enum, covering every constant means no <code>default</code> is needed, and the compiler complains when a new constant is added.</p>
[[switch-new]]
''', kw=['switch expression', 'arrow case', 'yield', 'fall through', 'break', 'multiple case labels', 'exhaustive switch', 'enum switch', 'Java 14']),
    part('records', '📇', 'Records', '''
<p>A <b>record</b> (Java 16) is a class whose job is to carry data. From one line, Java writes the private final fields, the constructor, an accessor per field (named <code>name()</code>, not <code>getName()</code>), and <code>equals</code>, <code>hashCode</code> and <code>toString</code> based on all fields.</p>
[[record]]
<p>The <b>compact constructor</b> (no parameter list) is where you validate and normalise. Records are final, cannot extend another class, and cannot add instance fields, but they can implement interfaces and have methods.</p>
[[record-shallow]]
<div class="tip">Records are ideal for API test models: request bodies, expected responses, test data rows. Jackson 2.12 and later can read JSON straight into records, and two records with the same values are equal, which makes assertions simple.</div>
''', kw=['record', 'Java 16', 'compact constructor', 'canonical constructor', 'accessor', 'equals', 'hashCode', 'toString', 'immutable', 'defensive copy', 'List.copyOf', 'DTO', 'wither']),
    part('sealed', '🔒', 'Sealed classes and interfaces', '''
<p>A <b>sealed</b> type (Java 17) lists exactly which classes may extend or implement it, using <code>permits</code>. It is the middle ground between <code>final</code> (nobody) and a normal class (anybody). Because the compiler knows the full list, a switch over a sealed type can be checked for completeness.</p>
[[sealed]]
[[sealed-missing]]
<p>Every permitted subclass must say what happens next: <code>final</code> stops there, <code>sealed</code> gives its own list, and <code>non-sealed</code> opens the hierarchy again.</p>
[[sealed-kinds]]
''', kw=['sealed', 'permits', 'non-sealed', 'final', 'Java 17', 'closed hierarchy', 'exhaustiveness', 'getPermittedSubclasses', 'algebraic data type']),
    part('instanceof', '🔍', 'Pattern matching for instanceof', '''
<p>The old pattern was test, then cast, then use. Since Java 16, <code>o instanceof String s</code> does all three: if the test passes, <code>s</code> is a String variable ready to use. The variable is only in scope where the test is known to be true, a rule called <b>flow scoping</b>.</p>
[[instanceof]]
''', kw=['pattern matching', 'instanceof', 'type pattern', 'binding variable', 'flow scoping', 'Java 16', 'cast']),
    part('switch-patterns', '🎯', 'Pattern matching for switch', '''
<p>Since Java 21, a switch can test the <b>type</b> of a value, add a condition with <code>when</code> (a <b>guard</b>), and even handle <code>null</code> as a case. Cases are checked from top to bottom and the first match wins.</p>
[[switch-patterns]]
<div class="viz" data-viz="jswitch"></div>
[[dominance]]
''', kw=['pattern matching for switch', 'Java 21', 'case null', 'guard', 'when', 'type pattern', 'dominance', 'first match wins', 'MatchException']),
    part('record-patterns', '🪆', 'Record patterns and unnamed variables', '''
<p>A <b>record pattern</b> (Java 21) matches a record and pulls its fields out into variables in the same step, and patterns can be nested. Combined with sealed types and switch, this style is called <b>data oriented programming</b>.</p>
[[record-patterns]]
<div class="viz" data-viz="flow" data-k="dop"></div>
<p>Java 22 added the <b>unnamed variable</b> <code>_</code> for things you must declare but never use: a loop variable, a caught exception, a lambda parameter or a record field you do not care about.</p>
[[unnamed]]
''', kw=['record pattern', 'deconstruction', 'nested pattern', 'data oriented programming', 'unnamed variable', 'underscore', '_', 'Java 21', 'Java 22']),
    part('primitive-patterns', '🧪', 'Primitive patterns (preview in Java 27)', '''
<p>Patterns so far only worked with objects. <b>Primitive types in patterns, instanceof and switch</b> (JEP 532, fifth preview in Java 27) lets you write <code>case int c when c &gt;= 500</code> and ask <code>big instanceof int</code>, which is true only when the value fits into an int without losing anything.</p>
[[primitive-patterns]]
<div class="warn">Preview features can still change. They need <code>--enable-preview</code> to compile and run, so keep them out of production code and use them to try ideas early.</div>
''', kw=['primitive patterns', 'JEP 532', 'preview feature', '--enable-preview', 'Java 27', 'instanceof int', 'exact conversion']),
    part('scenario', '🎬', 'Real world scenario: modelling API outcomes', '''
<div class="scenario"><b>The situation</b>An API test client returned either a body or null, and errors were thrown as exceptions. Tests forgot to handle 503s and network resets, so failures in the nightly run were hard to read.</div>
[[scenario]]
<p>Every possible outcome is now a record that implements one sealed interface. The report switch must handle them all, guards pick out special cases such as a zero total or a 503, and nested record patterns read the order fields directly. When someone adds a <code>Timeout</code> outcome, every switch that ignores it stops compiling.</p>
''', kw=['API result', 'sealed interface', 'record pattern', 'error handling', 'test client', 'retry', 'exhaustive switch']),
]

INFO = {'title': 'Say what the data is, then ask what it is', 'panels': [
    panel([['e', '📇'], ['t', 'record Order(String id, double total)', {'b': 1, 'size': 10}]], 'Records', 'Data without boilerplate.', 'equals, hashCode and toString come free.'),
    panel([['e', '🔒'], ['t', 'sealed ... permits Ok, Error', {'b': 1, 'size': 11}]], 'Sealed', 'A closed list of kinds.', 'The compiler knows every option.'),
    panel([['e', '🎯'], ['t', 'case Ok(var s, var body) ->', {'b': 1, 'size': 11}]], 'Patterns', 'Test and take apart at once.', 'Guards with when, null as a case.'),
    panel([['e', '📜'], ['t', '""" { "qty": 2 } """', {'b': 1, 'size': 11}]], 'Text blocks', 'JSON as it really looks.', 'No escaped quotes.')],
    'remember': 'Model data with records, list the possible kinds with a sealed interface, and handle them with a switch over patterns. The compiler then checks that every case is covered.'}

REAL = [
    ['💳', 'A payments team', 'Models every payment method as a record under a sealed interface. Adding a new wallet showed the 4 places in the code that had to learn about it.'],
    ['🧪', 'An API test suite', 'Keeps expected JSON bodies in text blocks, so they can be copied straight from the API documentation.'],
    ['📦', 'A logistics app', 'Replaced 300 lines of getters, equals and hashCode in shipment classes with 12 record declarations.'],
]

SAY = [
    say('top', 'Welcome', 'Welcome to modern Java syntax: var, text blocks, switch expressions, records, sealed types and pattern matching.',
        'आधुनिक Java syntax में आपका स्वागत है: var, text blocks, switch expressions, records, sealed types और pattern matching।',
        'ಆಧುನಿಕ Java syntax ಗೆ ಸ್ವಾಗತ: var, text blocks, switch expressions, records, sealed types ಮತ್ತು pattern matching.',
        'ଆଧୁନିକ Java syntax କୁ ସ୍ୱାଗତ: var, text blocks, switch expressions, records, sealed types ଓ pattern matching।',
        'مرحبًا بك في صياغة Java الحديثة: var والكتل النصية وتعابير switch والسجلات والأنواع المختومة ومطابقة الأنماط.',
        'Willkommen bei moderner Java-Syntax: var, Textblöcke, Switch-Ausdrücke, Records, versiegelte Typen und Pattern Matching.'),
    say('var', 'var', 'var lets the compiler infer the type of a local variable. The type is still fixed and cannot change later.',
        'var compiler को local variable का type निकालने देता है। Type फिर भी तय रहता है और बाद में नहीं बदलता।',
        'var compiler ಗೆ local variable type ಊಹಿಸಲು ಬಿಡುತ್ತದೆ. Type ಸ್ಥಿರ, ನಂತರ ಬದಲಾಗದು.',
        'var compiler କୁ local variable type ଅନୁମାନ କରିବାକୁ ଦିଏ। Type ସ୍ଥିର, ପରେ ବଦଳେ ନାହିଁ।',
        'يتيح var للمترجم استنتاج نوع المتغير المحلي، ويبقى النوع ثابتًا لا يتغير لاحقًا.',
        'Mit var leitet der Compiler den Typ einer lokalen Variable ab. Der Typ bleibt fest.'),
    say('text-blocks', 'Text blocks', 'Text blocks span several lines between triple quotes, keep the layout and need no escaped quotes. Great for JSON and SQL.',
        'Text blocks तीन quotes के बीच कई lines में होते हैं, layout रखते हैं और quotes escape नहीं करने पड़ते। JSON और SQL के लिए बढ़िया।',
        'Text blocks ಮೂರು quotes ನಡುವೆ ಹಲವು lines, layout ಉಳಿಸುತ್ತವೆ. JSON ಮತ್ತು SQL ಗೆ ಉತ್ತಮ.',
        'Text blocks ତିନି quotes ମଧ୍ୟରେ ଅନେକ lines, layout ରଖନ୍ତି। JSON ଓ SQL ପାଇଁ ଭଲ।',
        'تمتد الكتل النصية على عدة أسطر بين ثلاث علامات اقتباس وتحافظ على التنسيق دون تهريب. ممتازة لـ JSON وSQL.',
        'Textblöcke stehen zwischen dreifachen Anführungszeichen, behalten das Layout und brauchen kein Escaping. Ideal für JSON und SQL.'),
    say('switch', 'Switch expressions', 'A switch expression gives a value, the arrow form never falls through, and yield returns a value from a block.',
        'Switch expression एक value देता है, arrow form कभी fall through नहीं करता, और yield block से value लौटाता है।',
        'Switch expression value ಕೊಡುತ್ತದೆ, arrow form fall through ಆಗುವುದಿಲ್ಲ, yield block ನಿಂದ value ಕೊಡುತ್ತದೆ.',
        'Switch expression value ଦିଏ, arrow form fall through ହୁଏ ନାହିଁ, yield block ରୁ value ଦିଏ।',
        'يعطي تعبير switch قيمة، ولا يسقط شكل السهم إلى الحالة التالية، وتعيد yield قيمة من كتلة.',
        'Ein Switch-Ausdruck liefert einen Wert, die Pfeilform fällt nie durch, und yield gibt einen Wert aus einem Block zurück.'),
    say('records', 'Records', 'A record carries data. Java writes the fields, constructor, accessors, equals, hashCode and toString. Validate in the compact constructor.',
        'Record data ले जाता है। Java fields, constructor, accessors, equals, hashCode और toString लिखता है। Compact constructor में जाँच करें।',
        'Record data ಹೊತ್ತೊಯ್ಯುತ್ತದೆ. Java fields, constructor, equals, toString ಬರೆಯುತ್ತದೆ.',
        'Record data ବହନ କରେ। Java fields, constructor, equals, toString ଲେଖେ।',
        'السجل يحمل البيانات، ويكتب Java الحقول والمنشئ والدوال وequals وhashCode وtoString. تحقق من المدخلات في المنشئ المختصر.',
        'Ein Record trägt Daten. Java schreibt Felder, Konstruktor, Zugriffsmethoden, equals, hashCode und toString. Prüfe im kompakten Konstruktor.'),
    say('sealed', 'Sealed types', 'A sealed type lists exactly which classes may extend it, so a switch over it can be checked for completeness.',
        'Sealed type बताता है कि कौन सी classes उसे extend कर सकती हैं, इसलिए switch की पूर्णता जाँची जा सकती है।',
        'Sealed type ಯಾವ classes extend ಮಾಡಬಹುದು ಎಂದು ಪಟ್ಟಿ ಮಾಡುತ್ತದೆ.',
        'Sealed type କେଉଁ classes extend କରିପାରିବେ ତାହା ତାଲିକା କରେ।',
        'يسرد النوع المختوم الأصناف المسموح لها بتوسيعه، فيمكن التحقق من اكتمال switch عليه.',
        'Ein versiegelter Typ nennt genau die erlaubten Unterklassen, daher kann ein switch auf Vollständigkeit geprüft werden.'),
    say('instanceof', 'instanceof patterns', 'instanceof with a variable name tests, casts and binds in one step. The variable exists only where the test is true.',
        'Variable नाम के साथ instanceof एक ही कदम में जाँचता, cast करता और bind करता है।',
        'instanceof ಒಂದೇ ಹಂತದಲ್ಲಿ ಪರೀಕ್ಷೆ, cast ಮತ್ತು bind ಮಾಡುತ್ತದೆ.',
        'instanceof ଗୋଟିଏ ପଦକ୍ଷେପରେ ଯାଞ୍ଚ, cast ଓ bind କରେ।',
        'يختبر instanceof مع اسم متغير ويحول ويربط في خطوة واحدة، والمتغير موجود فقط حيث يكون الاختبار صحيحًا.',
        'instanceof mit Variablenname prüft, castet und bindet in einem Schritt. Die Variable gilt nur, wo der Test wahr ist.'),
    say('switch-patterns', 'Switch patterns', 'A switch can test types, add guards with when, and handle null. The first matching case wins.',
        'Switch types जाँच सकता है, when से guards जोड़ सकता है और null संभाल सकता है। पहला मिलने वाला case जीतता है।',
        'Switch types ಪರೀಕ್ಷಿಸಿ when guards ಮತ್ತು null ನಿಭಾಯಿಸುತ್ತದೆ. ಮೊದಲ case ಗೆಲ್ಲುತ್ತದೆ.',
        'Switch types ଯାଞ୍ଚ କରି when guards ଓ null ସମ୍ଭାଳେ। ପ୍ରଥମ case ଜିତେ।',
        'يستطيع switch اختبار الأنواع وإضافة شروط بـ when ومعالجة null، وأول حالة مطابقة تفوز.',
        'Ein switch prüft Typen, kennt Guards mit when und behandelt null. Der erste passende Fall gewinnt.'),
    say('record-patterns', 'Record patterns', 'A record pattern matches a record and pulls out its fields. The underscore marks variables you do not need.',
        'Record pattern record से मेल खाता है और उसके fields निकालता है। Underscore उन variables के लिए है जिनकी ज़रूरत नहीं।',
        'Record pattern record ಹೊಂದಿಸಿ fields ತೆಗೆಯುತ್ತದೆ. Underscore ಬೇಡದ variables ಗೆ.',
        'Record pattern record ମେଳାଇ fields ବାହାର କରେ। Underscore ଅଦରକାରୀ variables ପାଇଁ।',
        'يطابق نمط السجل سجلًا ويستخرج حقوله، وتشير الشرطة السفلية إلى متغيرات لا تحتاجها.',
        'Ein Record-Muster passt auf einen Record und holt seine Felder heraus. Der Unterstrich steht für unnötige Variablen.'),
    say('primitive-patterns', 'Primitive patterns', 'In the Java 27 preview, patterns also work with int, long and double, and instanceof int checks that a value fits.',
        'Java 27 preview में patterns int, long और double के साथ भी काम करते हैं, और instanceof int जाँचता है कि value फिट होती है।',
        'Java 27 preview ನಲ್ಲಿ patterns int, long, double ಜೊತೆಗೂ ಕೆಲಸ ಮಾಡುತ್ತವೆ.',
        'Java 27 preview ରେ patterns int, long, double ସହ ମଧ୍ୟ କାମ କରେ।',
        'في معاينة Java 27 تعمل الأنماط مع int وlong وdouble، ويتحقق instanceof int من أن القيمة تتسع.',
        'In der Vorschau von Java 27 funktionieren Muster auch mit int, long und double, und instanceof int prüft, ob ein Wert passt.'),
    say('scenario', 'Scenario', 'Every API outcome becomes a record under one sealed interface, and the report switch must handle every one of them.',
        'हर API परिणाम एक sealed interface के तहत record बनता है, और report switch को हर एक संभालना होता है।',
        'ಪ್ರತಿ API ಫಲಿತಾಂಶ sealed interface ಅಡಿ record ಆಗುತ್ತದೆ.',
        'ପ୍ରତ୍ୟେକ API ଫଳାଫଳ sealed interface ତଳେ record ହୁଏ।',
        'يصبح كل ناتج من الواجهة البرمجية سجلًا تحت واجهة مختومة واحدة، ويجب أن يعالجها switch التقرير كلها.',
        'Jedes API-Ergebnis wird ein Record unter einem versiegelten Interface, und der Bericht muss jedes behandeln.'),
]

QUIZ = [
    quiz('e', 'Which accessor does <code>record User(String name)</code> create?', ['name()', 'getName()', 'getname()', 'user.name field only'], 0, 'Records use the field name.', 'Record accessors have the same name as the component, without get.'),
    quiz('e', 'What does this print?', ['success', 'not found', 'other', 'Compile error'], 0, 'Several labels on one case.', '201 is one of the labels of the first case.', code='int s = 201;\nSystem.out.println(switch (s) { case 200, 201 -> "success"; case 404 -> "not found"; default -> "other"; });', run=True),
    quiz('e', 'Where can <code>var</code> be used?', ['Local variables with an initial value', 'Fields', 'Method return types', 'Method parameters'], 0, 'Local only.', 'var is local variable type inference. Lambda parameters are the one extra place.'),
    quiz('m', 'What does this print?', ['true', 'false', 'Compile error', 'It depends on the JVM'], 0, 'Records compare by value.', 'equals compares every component, and both have the same sku and price.', code='record P(String sku, double price) {}\nSystem.out.println(new P("A", 1.0).equals(new P("A", 1.0)));', run=True),
    quiz('m', 'Why does a switch over a sealed interface need no default?', ['The compiler knows every permitted subtype and checks they are all covered', 'Defaults are not allowed in switch', 'Sealed types cannot be null', 'Java adds a hidden default that returns null'], 0, 'Closed list.', 'If a subtype is missing, it is a compile error. The hidden default throws MatchException only for classes changed after compiling.'),
    quiz('m', 'What does this print?', ['int 7', 'big 7', 'other', 'Compile error'], 0, 'The guard is checked.', '7 is not above 100, so the first case is skipped and the plain Integer case matches.', code='Object o = 7;\nSystem.out.println(switch (o) { case Integer i when i > 100 -> "big " + i; case Integer i -> "int " + i; default -> "other"; });', run=True),
    quiz('m', 'What does a text block do with the indentation that all lines share?', ['Removes it', 'Keeps it', 'Turns it into tabs', 'Throws an error'], 0, 'Incidental whitespace.', 'Only the indentation relative to the least indented line (or the closing quotes) stays.'),
    quiz('h', 'A permitted subclass of a sealed class must be declared as what?', ['final, sealed or non-sealed', 'abstract', 'static', 'public'], 0, 'It must say what comes next.', 'final stops the hierarchy, sealed continues with its own list, and non-sealed opens it again.'),
    quiz('h', 'What does this print?', ['7', '12', '3', 'Compile error'], 0, 'A nested record pattern pulls out the numbers.', 'x is 3 and y is 4, so 3 + 4 is 7.', code='record Pt(int x, int y) {}\nrecord Box(Pt p) {}\nObject o = new Box(new Pt(3, 4));\nif (o instanceof Box(Pt(var x, var y))) System.out.println(x + y);', run=True),
    quiz('h', 'Why is <code>case CharSequence cs -&gt; ...</code> followed by <code>case String s -&gt; ...</code> a compile error?', ['The String case can never be reached, it is dominated', 'String is not a CharSequence', 'Two cases cannot use types', 'Patterns need a default first'], 0, 'Top to bottom.', 'Every String is a CharSequence, so the first case always wins. Put the more specific case first.'),
    quiz('x', 'Are records deeply immutable?', ['No, a record holding a mutable list can still see that list change', 'Yes, always', 'Only if all fields are primitives and you mark the record final', 'Yes, Java copies every field'], 0, 'final fields hold references.', 'The reference cannot change, but the object it points to can. Copy with List.copyOf in the compact constructor.'),
    quiz('x', 'What does this print with Java 21 or later?', ['no value', 'null', 'NullPointerException', 'Compile error'], 0, 'case null is allowed in a pattern switch.', 'Without case null, a switch on null throws NullPointerException.', code='Object o = null;\nSystem.out.println(switch (o) { case null -> "no value"; case String s -> s; default -> "other"; });', run=True),
]

CALC = [
    calc('e', 'What does this print?', '4', 'QA uses 4 workers.', ['The enum constant QA shares a case with STAGING.', 'That case gives 4.'], code='enum Env { DEV, QA, PROD }\nEnv e = Env.QA;\nSystem.out.println(switch (e) { case DEV -> 1; case QA -> 4; case PROD -> 16; });', run=True),
    calc('e', 'What does this print?', '20.0', 'Card fee is 2 percent.', ['<span class="eq">1000 × 0.02 = 20.0</span>'], code='record Card(double amount) {}\nSystem.out.println(new Card(1000).amount() * 0.02);', run=True),
    calc('m', 'What does this print?', '12', 'Width times height of the rectangle.', ['<span class="eq">|4 − 1| × |5 − 1| = 3 × 4 = 12</span>'], code='record Pt(int x, int y) {}\nrecord Rect(Pt a, Pt b) {}\nObject o = new Rect(new Pt(1, 1), new Pt(4, 5));\nif (o instanceof Rect(Pt(var x1, var y1), Pt(var x2, var y2))) System.out.println(Math.abs(x2 - x1) * Math.abs(y2 - y1));', run=True),
    calc('m', 'What does this print?', '1', 'Equal records count once in a set.', ['Both records have the same components.', 'equals and hashCode agree, so the set keeps one.'], code='record P(String sku) {}\nSystem.out.println(new HashSet<>(List.of(new P("A"), new P("A"))).size());', run=True),
    calc('m', 'A sealed interface permits 4 records and a switch handles 3 of them with no default. How many compile errors does javac report for that switch?', '1', 'One switch, one error.', ['javac reports that the switch expression does not cover all possible input values.']),
    calc('h', 'What does this print?', '314', 'Round the circle area.', ['<span class="eq">π × 10 × 10 ≈ 314.16</span>', 'Math.round gives 314.'], code='record Circle(int r) {}\nObject o = new Circle(10);\nif (o instanceof Circle(int r)) System.out.println(Math.round(Math.PI * r * r));', run=True),
    calc('h', 'With the old switch, status 200 falls through case 200, case 201 and into case 404 before break. How many assignments to kind run?', '2', 'Count the assignments passed.', ['kind = "success" runs.', 'Then kind = "not found" runs and break stops.', 'So 2 assignments, and the value is wrong.']),
    calc('x', 'What does this print?', '2', 'Count the orders above 500 using an unnamed pattern.', ['900 and 700 are above 500.', 'So 2.'], code='record O(String id, double total) {}\nvar list = List.of(new O("a", 900), new O("b", 120), new O("c", 700));\nint n = 0;\nfor (var o : list) if (o instanceof O(_, var t) && t > 500) n++;\nSystem.out.println(n);', run=True),
]

T = {
    'slug': 'java-records-patterns', 'title': 'Records, sealed types and pattern matching', 'short': 'Records and patterns', 'emoji': '📇', 'module': MODULE, 'minutes': 25,
    'lead': 'Modern Java writes far less code to say far more. This chapter covers var, text blocks for JSON and SQL, switch expressions, records, sealed classes, pattern matching for instanceof and switch, record patterns, the unnamed variable and the primitive patterns previewed in Java 27, ending with API results modelled as data.',
    'desc': 'Modern Java syntax: var, text blocks, switch expressions, records, compact constructors, sealed classes and interfaces, pattern matching for instanceof and switch, guards, record patterns, unnamed variables and primitive patterns (Java 27 preview).',
    'summary': 'var and its limits, text blocks for JSON bodies and SQL, switch expressions with yield, records with validation and their shallow immutability, sealed classes and exhaustive switches, pattern matching for instanceof and switch with guards and null, record patterns and data oriented programming, unnamed variables, primitive patterns in the Java 27 preview, and an API client that models every outcome as a sealed type.',
    'keywords': ['var', 'text block', 'switch expression', 'yield', 'record', 'sealed', 'permits', 'pattern matching', 'instanceof', 'record pattern', 'guard', 'when', 'unnamed variable', 'data oriented programming', 'Java 17', 'Java 21'],
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC,
}
