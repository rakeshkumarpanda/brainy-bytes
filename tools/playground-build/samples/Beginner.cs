using System;
using System.Collections.Generic;

Console.Write("Name: ");
string name = Console.ReadLine();
Console.Write("Age: ");
int age = Convert.ToInt32(Console.ReadLine());
Console.WriteLine($"Hello {name}, in 5 years you will be {age + 5}.");

int[] scores = { 88, 92, 75 };
int best = scores[0];
foreach (int s in scores) if (s > best) best = s;
Console.WriteLine("Best: " + best);

for (int i = 1; i <= 3; i++)
{
    Console.WriteLine(new string('*', i));
}

var shop = new Dictionary<string, double> { ["apple"] = 0.5, ["bread"] = 2.25 };
double bill = 0;
foreach (var item in shop) bill += item.Value * 2;
Console.WriteLine($"Bill: {bill:F2}");

int Square(int x) => x * x;
Console.WriteLine(Square(9));

string word = "Level";
char[] chars = word.ToLower().ToCharArray();
Array.Reverse(chars);
Console.WriteLine(new string(chars) == word.ToLower() ? "palindrome" : "not");
double d = 7 / 2;
Console.WriteLine(d + " " + 7 / 2.0 + " " + (7 % 2 == 1));
int k = 0;
while (k < 3) { k++; if (k == 2) continue; Console.Write(k); }
Console.WriteLine();
List<string> names = new List<string>();
names.Add("Zoe"); names.Add("Adam"); names.Insert(0, "Mo");
names.Sort();
Console.WriteLine(string.Join("|", names) + " " + names.Count + " " + names.Contains("Adam") + " " + names.IndexOf("Zoe"));
