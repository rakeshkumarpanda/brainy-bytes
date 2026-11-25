// expect: 6: CS0127: Since 'Program.Show(int)' returns void, a return keyword must not be followed by an object expression
using System;
class Program {
    static void Show(int n) {
        Console.WriteLine(n);
        return n;
    }
    static void Main() { Show(3); }
}
