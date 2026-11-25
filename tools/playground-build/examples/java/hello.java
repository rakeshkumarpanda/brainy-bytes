import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        System.out.print("What is your name? ");
        String name = in.nextLine();
        System.out.print("How old are you? ");
        int age = in.nextInt();
        System.out.println("Hello, " + name + "!");
        System.out.println("In 5 years you will be " + (age + 5));
        if (age >= 13) {
            System.out.println("You are a teenager or older.");
        } else {
            System.out.println("You are a kid. Have fun!");
        }
    }
}
