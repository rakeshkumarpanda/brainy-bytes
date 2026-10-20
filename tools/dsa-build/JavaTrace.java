// Run one compiled Java program under JDI and record it line by line for the step viewer.
// Usage: java JavaTrace.java <classpath> <MainClass>  ->  prints {"trace": {...}, "out": "..."} as JSON.
import com.sun.jdi.*;
import com.sun.jdi.connect.*;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;
import java.io.*;
import java.util.*;

public class JavaTrace {
    static final int MAX_STEPS = 1500;
    static String main;
    static StepRequest stepReq;
    static ThreadReference thread;

    public static void main(String[] args) throws Exception {
        String cp = args[0];
        main = args[1];
        LaunchingConnector lc = Bootstrap.virtualMachineManager().defaultConnector();
        Map<String, Connector.Argument> ca = lc.defaultArguments();
        ca.get("main").setValue(main);
        ca.get("options").setValue("-cp " + cp + " -Xint");
        VirtualMachine vm = lc.launch(ca);
        Process proc = vm.process();
        InputStream pout = proc.getInputStream();
        new Thread(() -> { try { proc.getErrorStream().transferTo(OutputStream.nullOutputStream()); } catch (IOException e) { } }).start();
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        int olen = 0;

        ClassPrepareRequest cpr = vm.eventRequestManager().createClassPrepareRequest();
        cpr.addClassFilter(main);
        cpr.enable();

        List<Map<String, Object>> steps = new ArrayList<>();
        Map<String, String> prevVars = new LinkedHashMap<>();
        List<String> prevStack = null;
        boolean trunc = false;
        EventQueue q = vm.eventQueue();
        boolean done = false;
        while (!done) {
            EventSet es;
            try { es = q.remove(); } catch (VMDisconnectedException e) { break; }
            for (Event ev : es) {
                if (ev instanceof ClassPrepareEvent cpe) {
                    ReferenceType rt = cpe.referenceType();
                    Method m = rt.methodsByName("main").get(0);
                    BreakpointRequest br = vm.eventRequestManager().createBreakpointRequest(m.location());
                    br.enable();
                } else if (ev instanceof BreakpointEvent be) {
                    thread = be.thread();
                    stepReq = vm.eventRequestManager().createStepRequest(thread, StepRequest.STEP_LINE, StepRequest.STEP_INTO);
                    for (String ex : new String[]{"java.*", "javax.*", "sun.*", "jdk.*", "com.sun.*"}) stepReq.addClassExclusionFilter(ex);
                    stepReq.enable();
                    be.request().disable();
                    lastLine.put(1, be.location().lineNumber());
                    record(be.location(), steps, prevVars, null);
                    prevStack = lastStack;
                    olen = drain(pout, out, olen, steps);
                } else if (ev instanceof StepEvent se) {
                    if (steps.size() >= MAX_STEPS) { trunc = true; done = true; break; }
                    Location loc = se.location();
                    if (!loc.declaringType().name().startsWith(main)) continue;
                    if (loc.method().name().equals("<clinit>")) continue;
                    int depth = userDepth();
                    Integer ll = lastLine.get(depth);
                    boolean back = ll != null && ll == loc.lineNumber() && depth < lastDepth;
                    lastDepth = depth;
                    if (back) continue;
                    lastLine.put(depth, loc.lineNumber());
                    lastLine.keySet().removeIf(k -> k > depth);
                    record(loc, steps, prevVars, prevStack);
                    prevStack = lastStack;
                    olen = drain(pout, out, olen, steps);
                } else if (ev instanceof VMDeathEvent || ev instanceof VMDisconnectEvent) {
                    done = true;
                }
            }
            if (!done) try { es.resume(); } catch (VMDisconnectedException e) { break; }
        }
        if (trunc) { try { vm.exit(0); } catch (Exception e) { } }
        try { proc.waitFor(); } catch (Exception e) { }
        out.write(pout.readAllBytes());
        String all = out.toString("UTF-8");
        String endO = all.substring(Math.min(olenChars(all, olen), all.length()));
        StringBuilder sb = new StringBuilder();
        sb.append("{\"trace\":{\"steps\":[");
        for (int i = 0; i < steps.size(); i++) { if (i > 0) sb.append(','); json(sb, steps.get(i)); }
        sb.append("],\"end\":{\"o\":"); str(sb, endO); sb.append(",\"t\":").append(trunc).append("}},\"out\":"); str(sb, all); sb.append('}');
        System.out.print(sb);
    }

    static int olenChars(String all, int bytes) {
        try { return new String(Arrays.copyOf(all.getBytes("UTF-8"), bytes), "UTF-8").length(); } catch (Exception e) { return 0; }
    }

    static int drain(InputStream in, ByteArrayOutputStream out, int olen, List<Map<String, Object>> steps) throws IOException {
        // the program is suspended, so whatever it printed so far is already in the pipe
        try { Thread.sleep(2); } catch (InterruptedException e) { }
        int n = in.available();
        if (n > 0) out.write(in.readNBytes(n));
        byte[] b = out.toByteArray();
        if (b.length > olen && !steps.isEmpty()) {
            // text printed while running the previous line belongs to this step
            steps.get(steps.size() - 1).put("o", new String(b, olen, b.length - olen, "UTF-8"));
        }
        return b.length;
    }

    static List<String> lastStack;
    static Map<Integer, Integer> lastLine = new HashMap<>();
    static int lastDepth = 1;

    static int userDepth() {
        try {
            int n = 0;
            for (StackFrame f : thread.frames()) if (f.location().declaringType().name().startsWith(main)) n++;
            return n;
        } catch (IncompatibleThreadStateException e) { return 0; }
    }

    static void record(Location loc, List<Map<String, Object>> steps, Map<String, String> prevVars, List<String> prevStack) {
        Map<String, Object> st = new LinkedHashMap<>();
        st.put("l", loc.lineNumber());
        Map<String, String> cur = new LinkedHashMap<>();
        List<String> stack = new ArrayList<>();
        try {
            List<StackFrame> frames = thread.frames();
            for (int i = frames.size() - 1; i >= 0; i--) {
                Location fl = frames.get(i).location();
                if (!fl.declaringType().name().startsWith(main)) continue;
                String mn = fl.method().name();
                String cls = fl.declaringType().name();
                cls = cls.substring(cls.lastIndexOf('$') + 1);
                if (cls.contains(".")) cls = cls.substring(cls.lastIndexOf('.') + 1);
                stack.add(mn.equals("<init>") ? cls + " constructor" : mn + "()");
            }
            StackFrame top = frames.get(0);
            // read every raw value first: formatting may run toString in the program, which invalidates frames
            Map<String, Value> raw = new LinkedHashMap<>();
            Map<String, Integer> depthOf = new HashMap<>();
            try {
                for (LocalVariable lv : top.visibleVariables()) {
                    if (lv.name().equals("args")) continue;
                    raw.put("L." + lv.name(), top.getValue(lv));
                }
            } catch (AbsentInformationException e) { }
            ObjectReference self = top.thisObject();
            if (self != null) {
                for (Field f : self.referenceType().allFields()) {
                    if (f.isStatic() || f.isSynthetic()) continue;
                    raw.put("L.this." + f.name(), self.getValue(f));
                    depthOf.put("L.this." + f.name(), 1);
                }
            }
            for (Field f : loc.declaringType().allFields()) {
                if (!f.isStatic() || f.isSynthetic()) continue;
                if (f.isFinal() && (isPrim(f.typeName()) || f.typeName().equals("java.lang.String"))) continue;
                raw.put("G." + f.name(), loc.declaringType().getValue(f));
            }
            Map<String, String> g = new LinkedHashMap<>(), l = new LinkedHashMap<>();
            for (Map.Entry<String, Value> e : raw.entrySet()) {
                String f = fmt(e.getValue(), depthOf.getOrDefault(e.getKey(), 0));
                (e.getKey().startsWith("G.") ? g : l).put(e.getKey(), f);
            }
            cur.putAll(g);
            cur.putAll(l);
        } catch (IncompatibleThreadStateException e) { }
        if (prevStack == null || !prevStack.equals(stack)) st.put("s", stack);
        lastStack = stack;
        Map<String, String> d = new LinkedHashMap<>();
        for (Map.Entry<String, String> e : cur.entrySet()) if (!e.getValue().equals(prevVars.get(e.getKey()))) d.put(e.getKey(), e.getValue());
        for (String k : prevVars.keySet()) if (!cur.containsKey(k)) d.put(k, null);
        if (!d.isEmpty()) st.put("d", d);
        prevVars.clear();
        prevVars.putAll(cur);
        steps.add(st);
    }

    static boolean isPrim(String t) { return Set.of("int", "long", "short", "byte", "char", "boolean", "double", "float").contains(t); }

    static String clip(String s) { return s.length() > 90 ? s.substring(0, 89) + "…" : s; }

    static String fmt(Value v, int depth) {
        if (v == null) return "null";
        if (v instanceof CharValue c) return "'" + c.value() + "'";
        if (v instanceof PrimitiveValue) return v.toString();
        if (v instanceof StringReference s) return clip("\"" + s.value() + "\"");
        if (v instanceof ArrayReference a) {
            if (depth >= 3) return "[…]";
            StringBuilder sb = new StringBuilder("[");
            int n = a.length();
            for (int i = 0; i < Math.min(n, 12); i++) { if (i > 0) sb.append(", "); sb.append(fmt(a.getValue(i), depth + 1)); }
            if (n > 12) sb.append(", … +").append(n - 12);
            return clip(sb.append(']').toString());
        }
        ObjectReference o = (ObjectReference) v;
        String tn = o.referenceType().name();
        if (tn.startsWith(main)) {
            String simple = tn.substring(tn.lastIndexOf('$') + 1);
            if (depth >= 2) return simple;
            StringBuilder sb = new StringBuilder(simple).append('{');
            boolean first = true;
            for (Field f : o.referenceType().allFields()) {
                if (f.isStatic() || f.isSynthetic()) continue;
                if (!first) sb.append(", ");
                first = false;
                sb.append(f.name()).append('=').append(fmt(o.getValue(f), depth + 1));
            }
            return clip(sb.append('}').toString());
        }
        // library objects (StringBuilder, ArrayList, HashMap, ArrayDeque, boxed numbers) print with their own toString
        try {
            stepReq.disable();
            Method m = o.referenceType().methodsByName("toString", "()Ljava/lang/String;").get(0);
            Value r = o.invokeMethod(thread, m, List.of(), ObjectReference.INVOKE_SINGLE_THREADED);
            stepReq.enable();
            return clip(r == null ? "null" : ((StringReference) r).value());
        } catch (Exception e) {
            try { stepReq.enable(); } catch (Exception e2) { }
            return tn.substring(tn.lastIndexOf('.') + 1);
        }
    }

    static void str(StringBuilder sb, String s) {
        sb.append('"');
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> { if (c < 0x20) sb.append(String.format("\\u%04x", (int) c)); else sb.append(c); }
            }
        }
        sb.append('"');
    }

    @SuppressWarnings("unchecked")
    static void json(StringBuilder sb, Object o) {
        if (o == null) sb.append("null");
        else if (o instanceof String s) str(sb, s);
        else if (o instanceof Integer i) sb.append(i);
        else if (o instanceof List<?> l) { sb.append('['); for (int i = 0; i < l.size(); i++) { if (i > 0) sb.append(','); json(sb, l.get(i)); } sb.append(']'); }
        else if (o instanceof Map<?, ?> m) {
            sb.append('{');
            boolean first = true;
            for (Map.Entry<?, ?> e : m.entrySet()) { if (!first) sb.append(','); first = false; str(sb, (String) e.getKey()); sb.append(':'); json(sb, e.getValue()); }
            sb.append('}');
        }
    }
}
