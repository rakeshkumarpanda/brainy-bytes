using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

interface IShape { double Area(); }

abstract class Shape : IShape {
    public string Name { get; set; }
    protected Shape(string name) { Name = name; }
    public abstract double Area();
    public override string ToString() => $"{Name} {Area():F2}";
}

class Circle : Shape {
    public double R { get; }
    public Circle(double r) : base("circle") { R = r; }
    public override double Area() => Math.PI * R * R;
}

class Sq : Shape {
    int side;
    public Sq(int s) : base("square") { side = s; }
    public override double Area() { return side * side; }
}

enum Level { Low, Mid, High }

record Person(string Name, int Age);

struct Pt { public int X; public int Y; public Pt(int x, int y) { X = x; Y = y; } }

class Program {
    static int Fib(int n) => n < 2 ? n : Fib(n - 1) + Fib(n - 2);
    static void Bump(ref int x) { x += 10; }
    static bool TryHalf(int n, out int half) { half = n / 2; return n % 2 == 0; }

    static void Main(string[] args) {
        Console.WriteLine("Fib(15) = " + Fib(15));
        var shapes = new List<Shape> { new Circle(2), new Sq(3) };
        foreach (var s in shapes) Console.WriteLine(s);
        Console.WriteLine(shapes.Sum(s => s.Area()).ToString("F3"));
        int v = 5; Bump(ref v); Console.WriteLine(v);
        if (TryHalf(8, out int h)) Console.WriteLine($"half {h}");
        var nums = new List<int> { 5, 3, 9, 1, 7 };
        nums.Sort();
        Console.WriteLine(string.Join(", ", nums));
        var evens = nums.Where(x => x > 3).Select(x => x * 10).ToList();
        Console.WriteLine(string.Join(" ", evens) + " count=" + evens.Count + " max=" + nums.Max() + " avg=" + nums.Average());
        var dict = new Dictionary<string, int>();
        foreach (var w in "a b a c b a".Split(' ')) { if (dict.ContainsKey(w)) dict[w]++; else dict[w] = 1; }
        foreach (var kv in dict) Console.Write($"{kv.Key}={kv.Value} ");
        Console.WriteLine();
        Console.WriteLine(dict.TryGetValue("z", out int z) + " " + z);
        Level lv = Level.Mid;
        Console.WriteLine(lv + " " + (int)lv + " " + (lv == Level.Mid));
        var p = new Person("Ana", 30);
        Console.WriteLine(p);
        Console.WriteLine(p with { Age = 31 });
        Pt a = new Pt(1, 2); Pt b = a; b.X = 9; Console.WriteLine(a.X + " " + b.X);
        int[] arr = { 4, 2, 6 };
        Array.Sort(arr);
        Console.WriteLine(string.Join(",", arr) + " " + arr.Length);
        int[,] grid = new int[2, 3];
        grid[1, 2] = 7; Console.WriteLine(grid[1, 2] + " " + grid.GetLength(1));
        var sb = new StringBuilder();
        for (int i = 0; i < 3; i++) sb.Append(i).Append('-');
        Console.WriteLine(sb.ToString());
        string str = "Hello World";
        Console.WriteLine(str.ToUpper() + " " + str.Substring(6) + " " + str.IndexOf("o") + " " + str.Length + " " + str.Contains("World") + " " + str.Replace("l", "L"));
        Console.WriteLine(10 / 3 + " " + 10 % 3 + " " + 10.0 / 3 + " " + 1.0 + " " + 0.1 + 0.2 + " " + (0.1 + 0.2) + " " + 1e20 + " " + 2.5f);
        Console.WriteLine($"{3.14159:F2} {42,5}|{42,-5}| {255:X} {1234567:N0} {0.25:P0}");
        Console.WriteLine(Math.Round(2.5) + " " + Math.Round(3.5) + " " + Math.Max(3, 8) + " " + Math.Sqrt(16) + " " + Math.Pow(2, 8));
        string? maybe = null;
        Console.WriteLine(maybe ?? "none");
        Console.WriteLine(maybe?.Length);
        var stack = new Stack<int>(); stack.Push(1); stack.Push(2); Console.WriteLine(stack.Pop() + " " + stack.Count);
        var q = new Queue<string>(); q.Enqueue("x"); q.Enqueue("y"); Console.WriteLine(q.Dequeue() + q.Peek());
        var words = new[] { "pear", "fig", "banana" };
        foreach (var w in words.OrderBy(w => w.Length)) Console.Write(w + " ");
        Console.WriteLine();
        string res = lv switch { Level.Low => "low", Level.Mid => "mid", _ => "high" };
        Console.WriteLine(res);
        object o = 42;
        if (o is int n && n > 40) Console.WriteLine("big int " + n);
        char c = 'A'; c++; Console.WriteLine(c + " " + (int)c + " " + (char)(c + 1));
        long big = int.MaxValue; big++; Console.WriteLine(big);
        int ov = int.MaxValue; ov++; Console.WriteLine(ov);
        Console.WriteLine(int.Parse("12") + 1);
        string line = Console.ReadLine();
        int num = int.Parse(Console.ReadLine());
        Console.WriteLine($"Hi {line}, {num * 3}");
        try { int[] t = new int[2]; t[3] = 1; }
        catch (IndexOutOfRangeException e) { Console.WriteLine("caught: " + e.Message); }
        finally { Console.WriteLine("done"); }
        throw new InvalidOperationException("stop here");
    }
}
