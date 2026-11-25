// expect: 6: CS1955: Non-invocable member 'string.Length' cannot be used like a method.
using System;
class Program {
    static void Main() {
        string word = "hello";
        Console.WriteLine(word.Length());
    }
}
