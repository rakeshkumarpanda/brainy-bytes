#include <stdio.h>

int lineTotal(int price, int qty) {
    return price * qty;
}

int main(void) {
    const char *items[] = {"Notebook", "Pencil", "Water bottle"};
    int prices[] = {45, 10, 120};
    int qty[] = {3, 5, 1};
    int bill = 0;

    for (int i = 0; i < 3; i++) {
        int cost = lineTotal(prices[i], qty[i]);
        printf("%s x %d = %d\n", items[i], qty[i], cost);
        bill += cost;
    }
    if (bill > 200) {
        bill = bill - bill / 10;   /* 10% off on big bills */
    }
    printf("You pay: %d rupees\n", bill);
    return 0;
}
