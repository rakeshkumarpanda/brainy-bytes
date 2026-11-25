// expect: 6: CS0131: The left-hand side of an assignment must be a variable, property or indexer
using System;
class Program {
    static void Main() {
        const int Days = 7;
        Days = 8;
        Console.WriteLine(Days);
    }
}
