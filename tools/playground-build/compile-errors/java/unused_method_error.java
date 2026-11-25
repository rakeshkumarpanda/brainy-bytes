public class Main {
    static void neverCalled() {
        short s = 40000;
    }
    public static void main(String[] args) {
        System.out.println("This line runs, but the program must not start");
    }
}
