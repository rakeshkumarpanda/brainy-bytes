import java.util.Scanner;
import java.util.Arrays;

public class Main {
    static boolean isPrime(int n) {
        if (n < 2) return false;
        for (int i = 2; i * i <= n; i++) if (n % i == 0) return false;
        return true;
    }
    static int binarySearch(int[] a, int key) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (a[mid] == key) return mid;
            else if (a[mid] < key) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter your name: ");
        String name = sc.nextLine();
        System.out.print("How many numbers? ");
        int n = sc.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = sc.nextInt();
        for (int i = 0; i < n - 1; i++)
            for (int j = 0; j < n - 1 - i; j++)
                if (a[j] > a[j + 1]) { int t = a[j]; a[j] = a[j + 1]; a[j + 1] = t; }
        System.out.println("Hello " + name + ", sorted: " + Arrays.toString(a));
        System.out.println("index of 7: " + binarySearch(a, 7));
        for (int i = 1; i <= 20; i++) if (isPrime(i)) System.out.print(i + " ");
        System.out.println();
        for (int i = 1; i <= 4; i++) {
            for (int j = 0; j < 4 - i; j++) System.out.print(" ");
            for (int j = 0; j < 2 * i - 1; j++) System.out.print("*");
            System.out.println();
        }
        String w = "racecar";
        String rev = new StringBuilder(w).reverse().toString();
        System.out.println(w + (w.equals(rev) ? " is" : " is not") + " a palindrome");
        int[][] A = {{1, 2}, {3, 4}}, B = {{5, 6}, {7, 8}};
        int[][] C = new int[2][2];
        for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) for (int k = 0; k < 2; k++) C[i][j] += A[i][k] * B[k][j];
        System.out.println(Arrays.deepToString(C));
        int count = 0; String s = "Hello World"; for (char ch : s.toLowerCase().toCharArray()) if ("aeiou".indexOf(ch) >= 0) count++;
        System.out.println("vowels " + count);
        double c = 37.5; System.out.printf("%.1f C = %.1f F%n", c, c * 9 / 5 + 32);
        int x = 10; x += x++ + ++x; System.out.println(x);
        System.out.println(5 + 3 + "x" + 5 + 3);
        char grade = 'B';
        switch (grade) { case 'A': System.out.println("top"); break; case 'B': case 'C': System.out.println("good"); break; default: System.out.println("?"); }
    }
}
