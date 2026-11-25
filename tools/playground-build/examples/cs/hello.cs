using System;

class Program
{
    static void Main()
    {
        Console.Write("What is your name? ");
        string name = Console.ReadLine();
        Console.Write("How old are you? ");
        int age = int.Parse(Console.ReadLine());
        Console.WriteLine("Hello, " + name + "!");
        Console.WriteLine("In 5 years you will be " + (age + 5));
        if (age >= 13)
        {
            Console.WriteLine("You are a teenager or older.");
        }
        else
        {
            Console.WriteLine("You are a kid. Have fun!");
        }
    }
}
