// expect: 6: CS0019: Operator '<' cannot be applied to operands of type 'string' and 'string'
using System;
class Program {
    static void Main() {
        string a = "ant", b = "bee";
        if (a < b) Console.WriteLine("ant comes first");
    }
}
