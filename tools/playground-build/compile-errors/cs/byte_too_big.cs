// expect: 5: CS0031: Constant value '300' cannot be converted to a 'byte'
using System;
class Program {
    static void Main() {
        byte small = 300;
        Console.WriteLine(small);
    }
}
