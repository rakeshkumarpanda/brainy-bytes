// expect: 5: CS0030: Cannot convert type 'string' to 'int'
using System;
class Program {
    static void Main() {
        int n = (int) "5";
        Console.WriteLine(n);
    }
}
