using System;

class Program
{
    static void Main()
    {
        string[] days = { "Mon", "Tue", "Wed" };
        for (int i = 0; i <= days.Length; i++)   // <= goes one step too far
        {
            Console.WriteLine(days[i]);
        }
    }
}
