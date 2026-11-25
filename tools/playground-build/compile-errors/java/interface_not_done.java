interface Animal {
    String sound();
    String name();
}
class Dog implements Animal {
    public String sound() { return "Woof"; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(new Dog().sound());
    }
}
