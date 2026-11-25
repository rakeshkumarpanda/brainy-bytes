// expect: 5: CS0815: Cannot assign <null> to an implicitly-typed variable
using System;
class Program {
    static void Main() {
        var nothing = null;
        Console.WriteLine(nothing);
    }
}
