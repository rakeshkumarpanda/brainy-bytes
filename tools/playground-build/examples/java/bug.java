public class Main {
    public static void main(String[] args) {
        int[] scores = {12, 7, 15};
        int total = 0;
        for (int i = 0; i < 4; i++) {   // the array has only 3 items
            total += scores[i];
        }
        System.out.println("Total: " + total);
    }
}
