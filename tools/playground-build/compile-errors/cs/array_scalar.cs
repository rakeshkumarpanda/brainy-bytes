// expect: 6: CS0029: Cannot implicitly convert type 'int' to 'int[]'
using System;
class Program {
    static void Main() {
        int[] scores = new int[3];
        scores = 5;
        Console.WriteLine(scores[0]);
    }
}
