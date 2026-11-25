// expect: 6: CS1503: Argument 1: cannot convert from 'string' to 'int'
using System;
class Program {
    static int Twice(int n) { return n * 2; }
    static void Main() {
        Console.WriteLine(Twice("4"));
    }
}
