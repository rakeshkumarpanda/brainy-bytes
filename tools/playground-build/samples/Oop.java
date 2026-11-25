import java.util.*;

interface Shape { double area(); default String name() { return "shape"; } }

abstract class Base implements Shape {
    protected String label;
    Base(String label) { this.label = label; }
    public String toString() { return label + "(" + String.format("%.2f", area()) + ")"; }
}

class Circle extends Base {
    double r;
    Circle(double r) { super("circle"); this.r = r; }
    public double area() { return Math.PI * r * r; }
    @Override public String name() { return "round"; }
}

class Rect extends Base {
    int w, h;
    Rect(int w, int h) { super("rect"); this.w = w; this.h = h; }
    public double area() { return w * h; }
}

enum Color { RED, GREEN, BLUE; Color next() { return values()[(ordinal() + 1) % values().length]; } }

record Point(int x, int y) { int dist() { return Math.abs(x) + Math.abs(y); } }

public class Main {
    static int counter = 0;
    static <T extends Comparable<T>> T max(List<T> xs) {
        T best = xs.get(0);
        for (T x : xs) if (x.compareTo(best) > 0) best = x;
        return best;
    }
    static int divide(int a, int b) { return a / b; }
    public static void main(String[] args) {
        List<Shape> shapes = new ArrayList<>(List.of(new Circle(1.5), new Rect(3, 4)));
        for (Shape s : shapes) System.out.println(s + " " + s.name());
        Color c = Color.BLUE;
        System.out.println(c + " -> " + c.next() + " " + Color.valueOf("GREEN").ordinal());
        Point p = new Point(3, -4);
        System.out.println(p + " " + p.dist() + " " + p.equals(new Point(3, -4)));
        System.out.println(max(Arrays.asList(4, 9, 2)) + " " + max(List.of("pear", "apple", "zoo")));
        try {
            divide(5, 0);
        } catch (ArithmeticException e) {
            System.out.println("caught: " + e.getMessage());
        } finally {
            System.out.println("finally");
        }
        int[][] grid = new int[3][4];
        for (int i = 0; i < 3; i++) for (int j = 0; j < 4; j++) grid[i][j] = i * j;
        System.out.println(Arrays.toString(grid[2]) + " " + Arrays.deepToString(grid));
        String s = "Hello, World";
        System.out.println(s.toUpperCase() + " " + s.substring(7) + " " + s.indexOf('o') + " " + s.charAt(4) + " " + s.length() + " " + s.replace("l", "L") + " " + s.contains("World"));
        System.out.println(String.join("-", s.split(", ")) + " " + "  trim  ".trim() + "|");
        switch (c) {
            case RED -> System.out.println("r");
            case BLUE -> System.out.println("b");
            default -> System.out.println("?");
        }
        Map<String, Integer> freq = new TreeMap<>();
        for (String w : "the cat and the hat and the bat".split(" ")) freq.put(w, freq.getOrDefault(w, 0) + 1);
        System.out.println(freq);
        for (Map.Entry<String, Integer> e : freq.entrySet()) if (e.getValue() > 1) System.out.print(e.getKey() + "=" + e.getValue() + ";");
        System.out.println();
        Map<Integer, String> hm = new HashMap<>();
        for (int i = 20; i > 0; i -= 3) hm.put(i * 7, "v" + i);
        System.out.println(hm);
        Set<String> hs = new HashSet<>(List.of("delta", "alpha", "charlie", "bravo", "echo"));
        System.out.println(hs);
        Deque<Integer> st = new ArrayDeque<>();
        st.push(1); st.push(2); st.push(3);
        System.out.println(st.pop() + " " + st.peek() + " " + st);
        Queue<Integer> q = new LinkedList<>();
        q.offer(5); q.offer(6); System.out.println(q.poll() + " " + q);
        PriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.reverseOrder());
        pq.addAll(List.of(3, 1, 4, 1, 5, 9, 2, 6));
        StringBuilder out = new StringBuilder();
        while (!pq.isEmpty()) out.append(pq.poll()).append(' ');
        System.out.println(out.toString().trim());
        List<String> names = new ArrayList<>(List.of("bob", "alice", "carol", "dave"));
        names.sort((a, b) -> b.length() - a.length());
        System.out.println(names);
        System.out.println(names.stream().filter(n -> n.length() > 3).map(String::toUpperCase).toList());
        int sum = java.util.stream.IntStream.rangeClosed(1, 10).sum();
        System.out.println(sum + " " + Integer.toBinaryString(10) + " " + Integer.parseInt("42") + " " + Character.isDigit('7') + " " + (char)('a' + 2) + " " + (int) 'A');
        Object o = shapes.get(0);
        if (o instanceof Circle cc) System.out.println("radius " + cc.r);
        String text = """
            Hi
              there""";
        System.out.println(text);
        long f = 1; for (int i = 1; i <= 20; i++) f *= i; System.out.println(f);
        System.out.println(10 % 3 + " " + (-7 % 3) + " " + (-7 / 2) + " " + Math.floorMod(-7, 3) + " " + Math.sqrt(2) + " " + Math.pow(2, 10) + " " + 0.1 + 0.2 + " " + (0.1 + 0.2) + " " + 100.0 / 3);
        int[] arr = {5, 2, 8, 1}; Arrays.sort(arr); System.out.println(Arrays.toString(arr) + Arrays.stream(arr).max().getAsInt());
        Integer a1 = 127, a2 = 127; System.out.println(a1.equals(a2) + " " + Objects.hash(1, 2));
        int[] none = new int[2];
        System.out.println(none[5]);
    }
}
