// expect: 6: CS0023: Operator '!' cannot be applied to operand of type 'int'
using System;
class Program {
    static void Main() {
        int lives = 3;
        if (!lives) Console.WriteLine("Game over");
    }
}
