import java.util.ArrayList;
import java.util.List;

class Student {
    String name;
    int[] marks;

    Student(String name, int[] marks) {
        this.name = name;
        this.marks = marks;
    }

    double average() {
        int sum = 0;
        for (int m : marks) sum += m;
        return (double) sum / marks.length;
    }
}

public class Main {
    public static void main(String[] args) {
        List<Student> students = new ArrayList<>();
        students.add(new Student("Asha", new int[]{88, 92, 79}));
        students.add(new Student("Ravi", new int[]{65, 70, 81}));
        students.add(new Student("Meera", new int[]{95, 89, 99}));
        students.sort((a, b) -> Double.compare(b.average(), a.average()));
        int rank = 1;
        for (Student s : students) {
            System.out.printf("%d %s %.1f%n", rank, s.name, s.average());
            rank++;
        }
        System.out.println("Top student: " + students.get(0).name);
    }
}
