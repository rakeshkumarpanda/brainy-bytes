// expect: 5: CS0031: Constant value '40000' cannot be converted to a 'short'
using System;
class Program {
    static void NeverCalled() {
        short s = 40000;
    }
    static void Main() { Console.WriteLine("The program must not start"); }
}
