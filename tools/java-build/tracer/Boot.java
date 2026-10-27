import java.io.*;
import java.lang.reflect.*;

/** Starts the traced program with an unbuffered System.out, so every print reaches the tracer before the next line runs. */
public class Boot {
    public static void main(String[] args) throws Throwable {
        System.setOut(new PrintStream(new FileOutputStream(FileDescriptor.out), true, "UTF-8"));
        Class<?> c = Class.forName(args[0]);
        try {
            Method m = find(c);
            m.setAccessible(true);
            Object target = Modifier.isStatic(m.getModifiers()) ? null : newInstance(c);
            if (m.getParameterCount() == 1) m.invoke(target, (Object) new String[0]); else m.invoke(target);
        } catch (InvocationTargetException e) {
            Throwable t = e.getCause();
            System.out.flush();
            System.err.print("Exception in thread \"main\" ");
            t.printStackTrace();
            System.exit(1);
        }
    }

    static Method find(Class<?> c) throws NoSuchMethodException {
        try { return c.getDeclaredMethod("main", String[].class); } catch (NoSuchMethodException e) { return c.getDeclaredMethod("main"); }
    }

    static Object newInstance(Class<?> c) throws Exception {
        Constructor<?> k = c.getDeclaredConstructor();
        k.setAccessible(true);
        return k.newInstance();
    }
}
