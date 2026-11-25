// expect: 6: CS0165: Use of unassigned local variable 'bonus'
using System;
class Program {
    static void Main(string[] args) {
        int bonus;
        if (args.Length > 5) Console.WriteLine(bonus);
    }
}
