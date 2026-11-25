#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define N 5
#define SQ(x) ((x) * (x))

typedef struct {
    char name[20];
    int age;
    double score;
} Student;

struct Node { int val; struct Node *next; };

int sum(int *a, int n) { int s = 0; for (int i = 0; i < n; i++) s += a[i]; return s; }
void swap(int *x, int *y) { int t = *x; *x = *y; *y = t; }
int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }

struct Node *push(struct Node *head, int v) {
    struct Node *n = malloc(sizeof(struct Node));
    n->val = v; n->next = head; return n;
}

int main(void) {
    int a[N] = {4, 1, 3};
    printf("sum=%d sq=%d\n", sum(a, N), SQ(3 + 1));
    int x = 3, y = 9; swap(&x, &y); printf("x=%d y=%d\n", x, y);
    printf("fact(10)=%d %ld\n", fact(10), (long)fact(12));
    Student s; strcpy(s.name, "Asha"); s.age = 12; s.score = 91.256;
    printf("%s is %d, score %.1f|%8.3f|%-6d|%05d|%x|%X|%o|%e|%g\n", s.name, s.age, s.score, s.score, s.age, s.age, 255, 255, 8, 12345.678, 0.0001234);
    Student list[2] = {{"Bo", 10, 70.5}, {"Cy", 11, 88.0}};
    for (int i = 0; i < 2; i++) printf("%s:%d:%.2f\n", list[i].name, list[i].age, list[i].score);
    struct Node *head = NULL;
    for (int i = 1; i <= 4; i++) head = push(head, i * 10);
    for (struct Node *p = head; p != NULL; p = p->next) printf("%d ", p->val);
    printf("\n");
    char word[] = "hello";
    printf("%zu %zu %c %d\n", strlen(word), sizeof(word), word[1] - 32, word[0]);
    char buf[50]; sprintf(buf, "%s-%d", word, 42); printf("%s %d\n", buf, strcmp("abc", "abd") < 0);
    strcat(buf, "!"); printf("%s\n", buf);
    int *dyn = (int *)malloc(3 * sizeof(int));
    for (int i = 0; i < 3; i++) *(dyn + i) = i * i;
    printf("%d %d %d\n", dyn[0], dyn[1], dyn[2]); free(dyn);
    unsigned int u = 0; u--; printf("%u\n", u);
    int big = 2147483647; printf("%d\n", big + 1);
    printf("%d %d %d %d\n", 7 / 2, -7 / 2, 7 % 3, -7 % 3);
    printf("%.4f %.2f %.0f %.0f %.0f\n", sqrt(2.0), pow(2, 0.5), 2.5, 3.5, 0.5);
    printf("%d %d %d\n", 5 & 3, 5 | 3, 5 ^ 3);
    printf("%d %d\n", 1 << 4, -16 >> 2);
    char c = 'A'; c += 2; printf("%c %d\n", c, c);
    double d = 10 / 4; printf("%f %f\n", d, 10 / 4.0);
    int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int t = 0; for (int i = 0; i < 2; i++) for (int j = 0; j < 3; j++) t += m[i][j] * (i + 1);
    printf("t=%d\n", t);
    int i = 0; while (1) { if (++i > 3) break; if (i == 2) continue; printf("i%d ", i); }
    printf("\n");
    int k = 10; do { k -= 3; } while (k > 0); printf("k=%d\n", k);
    switch (k) { case -2: printf("minus two\n"); case 0: printf("fall\n"); break; default: printf("other\n"); }
    int n; long total = 0;
    while (scanf("%d", &n) == 1) total += n;
    printf("total=%ld\n", total);
    printf("%5.1f%%\n", 12.345);
    puts("done");
    return 0;
}
