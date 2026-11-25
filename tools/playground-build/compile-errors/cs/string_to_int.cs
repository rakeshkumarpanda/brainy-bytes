// expect: 5: CS0029: Cannot implicitly convert type 'string' to 'int'
using System;
class Program {
    static void Main() {
        int age = "12";
        Console.WriteLine(age);
    }
}
