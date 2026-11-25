public class Main {
    public static void main(String[] args) {
        boolean big = args.length > 0;
        byte size = big ? 1 : 2;
        System.out.println(size);
    }
}
