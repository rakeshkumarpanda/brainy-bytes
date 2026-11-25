// expect: 6: CS0029: Cannot implicitly convert type 'int' to 'bool'
using System;
class Program {
    static void Main() {
        int apples = 3;
        if (apples) Console.WriteLine("We have apples");
    }
}
