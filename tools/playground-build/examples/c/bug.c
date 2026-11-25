#include <stdio.h>

int main(void) {
    int a = 10, b = 0;
    printf("Sharing %d sweets among %d friends\n", a, b);
    int each = a / b;   /* nobody to share with! */
    printf("Each friend gets %d\n", each);
    return 0;
}
