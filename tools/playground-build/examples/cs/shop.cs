using System;

class Program
{
    static int LineTotal(int price, int qty)
    {
        return price * qty;
    }

    static void Main()
    {
        string[] items = { "Notebook", "Pencil", "Water bottle" };
        int[] prices = { 45, 10, 120 };
        int[] qty = { 3, 5, 1 };
        int bill = 0;

        for (int i = 0; i < items.Length; i++)
        {
            int cost = LineTotal(prices[i], qty[i]);
            Console.WriteLine($"{items[i]} x {qty[i]} = {cost}");
            bill += cost;
        }
        if (bill > 200)
        {
            bill = bill - bill / 10;   // 10% off on big bills
        }
        Console.WriteLine($"You pay: {bill} rupees");
    }
}
