public class Main {
    static int lineTotal(int price, int qty) {
        return price * qty;
    }

    public static void main(String[] args) {
        String[] items = {"Notebook", "Pencil", "Water bottle"};
        int[] prices = {45, 10, 120};
        int[] qty = {3, 5, 1};

        int bill = 0;
        for (int i = 0; i < items.length; i++) {
            int cost = lineTotal(prices[i], qty[i]);
            System.out.println(items[i] + " x " + qty[i] + " = " + cost);
            bill += cost;
        }
        if (bill > 200) {
            bill = bill - bill / 10;   // 10% off on big bills
        }
        System.out.println("You pay: " + bill + " rupees");
    }
}
