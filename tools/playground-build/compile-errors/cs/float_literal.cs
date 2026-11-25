// expect: 5: CS0664: Literal of type double cannot be implicitly converted to type 'float'; use an 'F' suffix to create a literal of this type
using System;
class Program {
    static void Main() {
        float rate = 1.5;
        Console.WriteLine(rate);
    }
}
