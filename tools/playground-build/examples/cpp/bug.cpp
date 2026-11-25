#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<int> scores = {12, 7, 15};
    int total = 0;
    for (int i = 0; i <= 3; i++) {   // <= goes one step too far
        total += scores.at(i);
    }
    cout << "Total: " << total << endl;
    return 0;
}
