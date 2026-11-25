#include <iostream>
#include <string>
#include <vector>
using namespace std;

int lineTotal(int price, int qty) {
    return price * qty;
}

int main() {
    vector<string> items = {"Notebook", "Pencil", "Water bottle"};
    vector<int> prices = {45, 10, 120};
    vector<int> qty = {3, 5, 1};
    int bill = 0;

    for (size_t i = 0; i < items.size(); i++) {
        int cost = lineTotal(prices[i], qty[i]);
        cout << items[i] << " x " << qty[i] << " = " << cost << endl;
        bill += cost;
    }
    if (bill > 200) {
        bill = bill - bill / 10;   // 10% off on big bills
    }
    cout << "You pay: " << bill << " rupees" << endl;
    return 0;
}
