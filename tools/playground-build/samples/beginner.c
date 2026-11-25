#include <stdio.h>
#include <string.h>
#include <ctype.h>

int isPal(const char *s) { int i = 0, j = strlen(s) - 1; while (i < j) if (s[i++] != s[j--]) return 0; return 1; }
void rev(char *s) { int n = strlen(s); for (int i = 0; i < n / 2; i++) { char t = s[i]; s[i] = s[n - 1 - i]; s[n - 1 - i] = t; } }

int main() {
    char name[30];
    int age;
    printf("Name and age: ");
    scanf("%s %d", name, &age);
    printf("Hi %s, next year you will be %d\n", name, age + 1);
    int a[] = {9, 4, 7, 1, 8}, n = sizeof(a) / sizeof(a[0]);
    for (int i = 0; i < n - 1; i++) { int m = i; for (int j = i + 1; j < n; j++) if (a[j] < a[m]) m = j; int t = a[i]; a[i] = a[m]; a[m] = t; }
    for (int i = 0; i < n; i++) printf("%d%c", a[i], i == n - 1 ? '\n' : ' ');
    char w[] = "level"; printf("%s %d\n", w, isPal(w));
    char h[] = "hello"; rev(h); printf("%s\n", h);
    for (int i = 0; h[i]; i++) h[i] = toupper(h[i]);
    printf("%s\n", h);
    int fib[10] = {0, 1};
    for (int i = 2; i < 10; i++) fib[i] = fib[i - 1] + fib[i - 2];
    for (int i = 0; i < 10; i++) printf("%d ", fib[i]);
    printf("\n");
    int num = 12345, digits = 0, sum = 0;
    while (num > 0) { sum += num % 10; num /= 10; digits++; }
    printf("digits=%d sum=%d\n", digits, sum);
    for (int i = 1; i <= 3; i++) { for (int j = 1; j <= i; j++) printf("%d", j); printf("\n"); }
    float f = 1.1f; double d = 1.1; printf("%.10f %.10f %d\n", f, d, f == d);
    int x = 5; int *p = &x; *p = 20; printf("%d %d\n", x, *p == x);
    int arr2[3]; arr2[0] = 1;
    char line[100]; getchar(); fgets(line, sizeof line, stdin); line[strcspn(line, "\n")] = 0;
    printf("[%s] %zu\n", line, strlen(line));
    return 0;
}
