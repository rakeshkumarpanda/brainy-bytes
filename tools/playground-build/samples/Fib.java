import java.util.*;

public class Main {
    static int fib(int n) {
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);
    }
    public static void main(String[] args) {
        int[] nums = {5, 3, 8, 1};
        List<Integer> list = new ArrayList<>();
        Map<String, Integer> m = new HashMap<>();
        for (int x : nums) list.add(x * 2);
        Collections.sort(list);
        m.put("apple", 3); m.put("banana", 5); m.put("cherry", 7);
        System.out.println("fib(10) = " + fib(10));
        System.out.println(list + " " + m);
        double avg = (double) (5 + 3) / 3;
        System.out.printf("avg=%.3f%n", avg);
        StringBuilder sb = new StringBuilder();
        for (char c = 'a'; c <= 'e'; c++) sb.append(c);
        System.out.println(sb.reverse().toString() + 'x' + 1 + 2);
        long big = 1L << 40;
        System.out.println(big + " " + (Integer.MAX_VALUE + 1) + " " + 7 / 2 + " " + 7.0 / 2 + " " + 1.0 + " " + 1e10);
    }
}
