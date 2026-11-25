// expect: 5: CS0266: Cannot implicitly convert type 'double' to 'int'. An explicit conversion exists (are you missing a cast?)
using System;
class Program {
    static void Main() {
        int price = 3.5;
        Console.WriteLine(price);
    }
}
