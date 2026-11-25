// expect: 7: CS0535: 'Dog' does not implement interface member 'IAnimal.Name()'
using System;
interface IAnimal {
    string Sound();
    string Name();
}
class Dog : IAnimal {
    public string Sound() { return "Woof"; }
}
class Program {
    static void Main() { Console.WriteLine(new Dog().Sound()); }
}
