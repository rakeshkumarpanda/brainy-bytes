#include <stdio.h>

struct Student {
    char name[20];
    int marks[3];
};

double average(struct Student s) {
    int sum = 0;
    for (int i = 0; i < 3; i++) sum += s.marks[i];
    return sum / 3.0;
}

int main(void) {
    struct Student students[3] = {
        {"Asha", {88, 92, 79}},
        {"Ravi", {65, 70, 81}},
        {"Meera", {95, 89, 99}}
    };
    /* sort from best to worst average (bubble sort) */
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2 - i; j++) {
            if (average(students[j]) < average(students[j + 1])) {
                struct Student t = students[j];
                students[j] = students[j + 1];
                students[j + 1] = t;
            }
        }
    }
    for (int i = 0; i < 3; i++) {
        printf("%d %s %.1f\n", i + 1, students[i].name, average(students[i]));
    }
    printf("Top student: %s\n", students[0].name);
    return 0;
}
