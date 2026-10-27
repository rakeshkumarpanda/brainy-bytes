import com.sun.jdi.*;
import com.sun.jdi.connect.*;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/**
 * Records one real run of a small Java program line by line, for the "Run line by line" viewer.
 *
 * Usage: java Tracer.java <classes dir> <main class> <out.json> [max steps] [extra JVM options...]
 *
 * The program is started in a second JVM under the debugger interface. Each time the main thread reaches a new
 * line of Main.java the tracer stores the line, the call stack when it changed, the variables that changed and the
 * text printed since the last step. The JSON has the shape the viewer reads: {steps: [{l, s, d, o}], end: {o, t}}.
 * Local variables are keyed "L.name", fields of this "L.this.name" and static fields "G.name".
 */
public class Tracer {
    static final Set<String> SKIP = Set.of("java.", "javax.", "jdk.", "sun.", "com.sun.", "Boot");
    static StepRequest step;
    static String mainClass;
    static Event pending;
    static InputStream out;
    static final ByteArrayOutputStream printed = new ByteArrayOutputStream();

    public static void main(String[] args) throws Exception {
        String dir = args[0], main = args[1], dest = args[2];
        mainClass = main;
        int max = args.length > 3 ? Integer.parseInt(args[3]) : 400;
        String extra = args.length > 4 ? String.join(" ", Arrays.copyOfRange(args, 4, args.length)) : "";

        LaunchingConnector lc = Bootstrap.virtualMachineManager().defaultConnector();
        Map<String, Connector.Argument> ca = lc.defaultArguments();
        ca.get("options").setValue("-cp " + dir + " " + extra);
        ca.get("main").setValue("Boot " + main);
        VirtualMachine vm = lc.launch(ca);
        out = vm.process().getInputStream();
        InputStream err = vm.process().getErrorStream();

        EventRequestManager erm = vm.eventRequestManager();
        MethodEntryRequest entry = erm.createMethodEntryRequest();
        entry.addClassFilter(main);
        entry.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        entry.enable();

        List<Map<String, Object>> steps = new ArrayList<>();
        Map<String, String> last = new LinkedHashMap<>();
        List<String> lastStack = new ArrayList<>();
        boolean truncated = false, done = false;
        EventQueue q = vm.eventQueue();
        while (!done) {
            EventSet set = q.remove();
            for (Event ev : set) {
                if (ev instanceof VMDeathEvent || ev instanceof VMDisconnectEvent) { done = true; break; }
                if (ev instanceof MethodEntryEvent me) {
                    if (step == null && me.method().name().equals("main")) {
                        entry.disable();
                        step = erm.createStepRequest(me.thread(), StepRequest.STEP_LINE, StepRequest.STEP_INTO);
                        for (String s : SKIP) step.addClassExclusionFilter(s + "*");
                        step.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
                        step.enable();
                        pending = me;
                    }
                }
                if (ev instanceof StepEvent || ev == pending) {
                    LocatableEvent se = (LocatableEvent) ev;
                    pending = null;
                    Location loc = se.location();
                    String src;
                    try { src = loc.sourceName(); } catch (AbsentInformationException e) { src = ""; }
                    if (!src.equals(main + ".java") || loc.lineNumber() < 1 || generated(loc.method())) continue;
                    if (steps.size() >= max) {
                        truncated = true;
                        done = true;
                        break;
                    }
                    ThreadReference th = se.thread();
                    Map<String, Object> s = new LinkedHashMap<>();
                    s.put("l", loc.lineNumber());
                    List<String> stack = stack(th);
                    if (!stack.equals(lastStack)) { s.put("s", stack); lastStack = stack; }
                    Map<String, String> vars = vars(th);
                    Map<String, String> d = new LinkedHashMap<>();
                    for (var e : vars.entrySet()) if (!e.getValue().equals(last.get(e.getKey()))) d.put(e.getKey(), e.getValue());
                    for (String k : last.keySet()) if (!vars.containsKey(k)) d.put(k, null);
                    if (!d.isEmpty()) s.put("d", d);
                    last = vars;
                    String o = drain();
                    if (!o.isEmpty()) s.put("o", o);
                    if (s.size() == 1 && !steps.isEmpty() && steps.get(steps.size() - 1).get("l").equals(s.get("l"))) continue;
                    steps.add(s);
                }
            }
            if (!done) set.resume();
        }
        String rest;
        if (truncated) {
            rest = drain();
            try { vm.exit(0); } catch (Exception e) { /* already gone */ }
        } else {
            vm.process().waitFor();
            rest = drain() + new String(out.readAllBytes(), StandardCharsets.UTF_8);
        }
        String errText = new String(err.readAllBytes(), StandardCharsets.UTF_8);
        Map<String, Object> end = new LinkedHashMap<>();
        end.put("o", rest + errText);
        end.put("t", truncated);
        Map<String, Object> res = new LinkedHashMap<>();
        res.put("steps", steps);
        res.put("end", end);
        Files.writeString(Path.of(dest), json(res));
    }

    static String drain() throws IOException {
        int n = out.available();
        if (n <= 0) return "";
        byte[] b = out.readNBytes(n);
        return new String(b, StandardCharsets.UTF_8);
    }

    static boolean user(ReferenceType t) {
        String n = t.name();
        if (n.contains("$$Lambda")) return false;
        for (String s : SKIP) if (n.startsWith(s)) return false;
        return true;
    }

    /** Record accessors and other one line methods the compiler writes for a record are left out of the story. */
    static boolean generated(Method m) {
        if (m.isBridge() || (m.isSynthetic() && !m.name().startsWith("lambda$"))) return true;
        try {
            if (!(m.declaringType() instanceof ClassType ct) || ct.superclass() == null || !ct.superclass().name().equals("java.lang.Record")) return false;
            return m.allLineLocations().stream().map(Location::lineNumber).distinct().count() <= 1;
        } catch (AbsentInformationException e) {
            return true;
        }
    }

    static List<String> stack(ThreadReference th) throws IncompatibleThreadStateException {
        List<String> names = new ArrayList<>();
        for (StackFrame f : th.frames()) {
            Method m = f.location().method();
            if (!user(m.declaringType()) || generated(m)) continue;
            names.add(frameName(m));
        }
        Collections.reverse(names);
        return names;
    }

    static String frameName(Method m) {
        String cls = m.declaringType().name();
        cls = cls.substring(cls.lastIndexOf('$') + 1).substring(cls.lastIndexOf('.') + 1);
        if (cls.contains("$")) cls = cls.substring(cls.lastIndexOf('$') + 1);
        String n = m.name();
        if (n.equals("<init>")) return simple(m.declaringType().name()) + "()";
        if (n.equals("<clinit>")) return "static init of " + simple(m.declaringType().name());
        if (n.startsWith("lambda$")) return "lambda in " + n.split("\\$")[1] + "()";
        return n + "()";
    }

    static String simple(String n) {
        n = n.substring(n.lastIndexOf('.') + 1);
        return n.substring(n.lastIndexOf('$') + 1);
    }

    static Map<String, String> vars(ThreadReference th) throws Exception {
        Map<String, String> v = new LinkedHashMap<>();
        StackFrame f = th.frame(0);
        Map<String, Value> locals = new LinkedHashMap<>();
        try {
            for (LocalVariable lv : f.visibleVariables()) {
                if (lv.name().startsWith("this$") || lv.name().contains("$")) continue;
                locals.put(lv.name(), f.getValue(lv));
            }
        } catch (AbsentInformationException e) { /* compiled without -g */ }
        ObjectReference self = f.thisObject();
        ReferenceType type = th.virtualMachine().classesByName(mainClass).get(0);
        // read every value first, because describing one may run code and invalidate the frame
        Map<String, Value> fields = new LinkedHashMap<>();
        if (self != null && !(self.referenceType().name().contains("$$Lambda"))) {
            for (Field fd : self.referenceType().allFields()) {
                if (fd.isStatic() || fd.isSynthetic() || fd.name().startsWith("this$")) continue;
                fields.put(fd.name(), self.getValue(fd));
            }
        }
        Map<String, Value> statics = new LinkedHashMap<>();
        for (Field fd : type.fields()) {
            if (!fd.isStatic() || fd.isSynthetic() || fd.name().startsWith("$")) continue;
            statics.put(fd.name(), type.getValue(fd));
        }
        for (var e : locals.entrySet()) v.put("L." + e.getKey(), show(e.getValue(), th, 0));
        for (var e : fields.entrySet()) v.put("L.this." + e.getKey(), show(e.getValue(), th, 0));
        for (var e : statics.entrySet()) v.put("G." + e.getKey(), show(e.getValue(), th, 0));
        return v;
    }

    static String show(Value val, ThreadReference th, int depth) {
        if (val == null) return "null";
        if (val instanceof StringReference s) return quote(s.value());
        if (val instanceof CharValue c) return "'" + c.value() + "'";
        if (val instanceof PrimitiveValue p) return p.toString();
        if (val instanceof ArrayReference a) {
            List<String> items = new ArrayList<>();
            int n = a.length();
            for (int i = 0; i < Math.min(n, 12); i++) items.add(show(a.getValue(i), th, depth + 1));
            if (n > 12) items.add("…");
            return "[" + String.join(", ", items) + "]";
        }
        ObjectReference o = (ObjectReference) val;
        String name = o.referenceType().name();
        if (name.contains("$$Lambda") || name.contains("$Lambda")) return "(lambda)";
        String text = callToString(o, th);
        if (text == null || text.matches(".*@[0-9a-f]+$")) {
            if (depth > 1) return simple(name) + "{…}";
            List<String> parts = new ArrayList<>();
            for (Field fd : o.referenceType().allFields()) {
                if (fd.isStatic() || fd.isSynthetic() || fd.name().startsWith("this$")) continue;
                parts.add(fd.name() + "=" + show(o.getValue(fd), th, depth + 1));
            }
            text = simple(name) + "{" + String.join(", ", parts) + "}";
        }
        return text.length() > 120 ? text.substring(0, 119) + "…" : text;
    }

    static String callToString(ObjectReference o, ThreadReference th) {
        try {
            Method m = o.referenceType().methodsByName("toString", "()Ljava/lang/String;").get(0);
            step.disable();
            try {
                Value r = o.invokeMethod(th, m, List.of(), ObjectReference.INVOKE_SINGLE_THREADED);
                return r == null ? "null" : ((StringReference) r).value();
            } finally {
                step.enable();
            }
        } catch (Exception e) {
            return null;
        }
    }

    static String quote(String s) {
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\"";
    }

    static String json(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) {
            StringBuilder b = new StringBuilder("\"");
            for (char c : s.toCharArray()) {
                switch (c) {
                    case '"' -> b.append("\\\"");
                    case '\\' -> b.append("\\\\");
                    case '\n' -> b.append("\\n");
                    case '\r' -> b.append("\\r");
                    case '\t' -> b.append("\\t");
                    default -> { if (c < 0x20) b.append(String.format("\\u%04x", (int) c)); else b.append(c); }
                }
            }
            return b.append('"').toString();
        }
        if (o instanceof Number || o instanceof Boolean) return o.toString();
        if (o instanceof Map<?, ?> m) {
            List<String> p = new ArrayList<>();
            for (var e : m.entrySet()) p.add(json(String.valueOf(e.getKey())) + ":" + json(e.getValue()));
            return "{" + String.join(",", p) + "}";
        }
        if (o instanceof List<?> l) {
            List<String> p = new ArrayList<>();
            for (Object x : l) p.add(json(x));
            return "[" + String.join(",", p) + "]";
        }
        return json(o.toString());
    }
}
