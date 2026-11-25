// expect: 6: CS0120: An object reference is required for the non-static field, method, or property 'Program.Greet(string)'
using System;
class Program {
    void Greet(string who) { Console.WriteLine("Hi " + who); }
    static void Main() {
        Greet("Asha");
    }
}
