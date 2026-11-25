// expect: 4: CS0161: 'Program.Grade(int)': not all code paths return a value
using System;
class Program {
    static string Grade(int marks) {
        if (marks >= 50) return "pass";
    }
    static void Main() {
        Console.WriteLine(Grade(70));
    }
}
