#include <stdio.h>

int main(void) {
    char name[50];
    int age;
    printf("What is your name? ");
    scanf("%49s", name);
    printf("How old are you? ");
    scanf("%d", &age);
    printf("Hello, %s!\n", name);
    printf("In 5 years you will be %d\n", age + 5);
    if (age >= 13) {
        printf("You are a teenager or older.\n");
    } else {
        printf("You are a kid. Have fun!\n");
    }
    return 0;
}
