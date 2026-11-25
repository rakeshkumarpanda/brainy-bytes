public class Main {
    static String day(int d) {
        switch (d) {
            case 1: return "Monday";
                    break;
            default: return "Other";
        }
    }
    public static void main(String[] args) {
        System.out.println(day(1));
    }
}
