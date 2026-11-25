// expect: 6: CS1501: No overload for method 'Add' takes 3 arguments
using System;
class Program {
    static int Add(int a, int b) { return a + b; }
    static void Main() {
        Console.WriteLine(Add(1, 2, 3));
    }
}
