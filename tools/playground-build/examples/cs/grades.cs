using System;
using System.Collections.Generic;
using System.Linq;

class Student
{
    public string Name { get; }
    public int[] Marks { get; }

    public Student(string name, int[] marks)
    {
        Name = name;
        Marks = marks;
    }

    public double Average() => Marks.Average();
}

class Program
{
    static void Main()
    {
        var students = new List<Student>
        {
            new Student("Asha", new[] { 88, 92, 79 }),
            new Student("Ravi", new[] { 65, 70, 81 }),
            new Student("Meera", new[] { 95, 89, 99 })
        };
        var ranked = students.OrderByDescending(s => s.Average()).ToList();
        for (int i = 0; i < ranked.Count; i++)
        {
            Console.WriteLine($"{i + 1} {ranked[i].Name} {ranked[i].Average():F1}");
        }
        Console.WriteLine("Top student: " + ranked[0].Name);
    }
}
