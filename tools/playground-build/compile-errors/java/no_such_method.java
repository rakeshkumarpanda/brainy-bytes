class Animal { }
class Dog extends Animal { void bark() { System.out.println("Woof"); } }
public class Main {
    public static void main(String[] args) {
        Animal a = new Dog();
        a.bark();
    }
}
