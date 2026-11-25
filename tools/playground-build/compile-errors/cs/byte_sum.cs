// expect: 6: CS0266: Cannot implicitly convert type 'int' to 'byte'. An explicit conversion exists (are you missing a cast?)
using System;
class Program {
    static void Main() {
        byte b1 = 10, b2 = 20;
        byte b3 = b1 + b2;
        Console.WriteLine(b3);
    }
}
