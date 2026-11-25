// expect: 5: CS0029: Cannot implicitly convert type 'int' to 'string'
using System;
class Program {
    static void Main() {
        string name = 5;
        Console.WriteLine(name);
    }
}
