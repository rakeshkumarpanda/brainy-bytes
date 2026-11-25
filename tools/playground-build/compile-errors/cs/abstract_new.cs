// expect: 8: CS0144: Cannot create an instance of the abstract type or interface 'Shape'
using System;
abstract class Shape {
    public abstract double Area();
}
class Program {
    static void Main() {
        Shape s = new Shape();
    }
}
