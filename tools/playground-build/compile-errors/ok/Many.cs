using System;
using System.Collections.Generic;
using System.Linq;

interface IShape { double Area(); string Name { get; } }
abstract class Shape : IShape {
    public abstract double Area();
    public virtual string Name => "shape";
    protected int sides;
}
class Square : Shape {
    private readonly double side;
    public Square(double s) { side = s; sides = 4; }
    public override double Area() => side * side;
    public override string Name => "square";
}
record Point(int X, int Y);
struct Coin { public int Value; }
static class Tools {
    public const int Max = 10;
    public static int Twice(int n) => n * 2;
    public static bool TryHalf(int n, out int half) { half = n / 2; return n % 2 == 0; }
}
class Counter {
    public int Count { get; private set; }
    public void Add(int by = 1) { Count += by; }
}
class Program {
    static int total;
    static string Grade(int marks) {
        switch (marks / 10) {
            case 10: case 9: return "A";
            case 8: return "B";
            default: return "C";
        }
    }
    static int Sign(int n) {
        if (n > 0) return 1;
        else if (n < 0) return -1;
        else return 0;
    }
    static int Forever() { while (true) { return 5; } }
    static void Main(string[] args) {
        byte b = 10;
        b += 5;
        b++;
        short sh = 100;
        char c = 'A';
        int code = c;
        long big = code;
        double d = big;
        float f = 1.5f;
        decimal price = 9.99m;
        uint u = 5;
        ulong ul = u;
        const int Limit = 3;
        byte fromConst = Limit;
        sbyte sb = -5;
        int? maybe = null;
        var list = new List<int> { 3, 1, 2 };
        var dict = new Dictionary<string, int> { ["a"] = 1 };
        foreach (var kv in dict) Console.WriteLine($"{kv.Key}={kv.Value}");
        foreach (int x in list.OrderBy(x => x)) total += x;
        int half;
        if (Tools.TryHalf(8, out half)) Console.WriteLine(half);
        if (int.TryParse("12", out var parsed)) Console.WriteLine(parsed);
        Shape s = new Square(2);
        IShape i = s;
        Console.WriteLine($"{s.Name} {i.Area():F1} {Grade(95)} {Sign(-3)} {Forever()}");
        var p = new Point(1, 2);
        var (px, py) = (p.X, p.Y);
        Coin coin = new Coin(); coin.Value = 5;
        Counter ctr = new Counter(); ctr.Add(); ctr.Add(2);
        string word = "hello";
        int len = word.Length;
        char first = word[0];
        string kind = len switch { > 3 => "long", _ => "short" };
        Func<int, int> sq = n => n * n;
        int Local(int n) => n + total;
        object o = 5;
        if (o is int k && k > 2) Console.WriteLine(k);
        int[] arr = { 1, 2, 3 };
        double avg = arr.Average();
        Console.WriteLine($"{b} {sh} {code} {d} {f} {price} {ul} {fromConst} {sb} {maybe ?? 0} {px + py} {coin.Value} {ctr.Count} {first} {kind} {sq(3)} {Local(1)} {avg} {Tools.Twice(Tools.Max)}");
    }
}
