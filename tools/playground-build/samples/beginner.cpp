#include <iostream>
#include <string>
#include <vector>
using namespace std;

class BankAccount {
private:
    string owner;
    double balance;
public:
    BankAccount(const string &o, double b) : owner(o), balance(b) {}
    void deposit(double amt) { if (amt > 0) balance += amt; }
    bool withdraw(double amt) { if (amt > balance) return false; balance -= amt; return true; }
    double getBalance() const { return balance; }
    string getOwner() const { return owner; }
};

int main() {
    string full;
    cout << "Your full name: ";
    getline(cin, full);
    int n;
    cin >> n;
    vector<int> marks(n);
    for (int i = 0; i < n; i++) cin >> marks[i];
    int total = 0;
    for (int m : marks) total += m;
    double avg = (double)total / n;
    cout << full << " average " << avg << endl;
    BankAccount acc(full, 100.0);
    acc.deposit(50);
    cout << acc.withdraw(500) << " " << acc.withdraw(30) << " " << acc.getBalance() << endl;
    for (int i = 1; i <= 15; i++) {
        if (i % 15 == 0) cout << "FizzBuzz";
        else if (i % 3 == 0) cout << "Fizz";
        else if (i % 5 == 0) cout << "Buzz";
        else cout << i;
        cout << (i < 15 ? " " : "\n");
    }
    string s = "programming";
    int freq[26] = {0};
    for (char c : s) freq[c - 'a']++;
    for (int i = 0; i < 26; i++) if (freq[i] > 1) cout << char('a' + i) << freq[i] << " ";
    cout << endl;
    int *arr = new int[5];
    for (int i = 0; i < 5; i++) arr[i] = i * i;
    int *p = arr;
    cout << *(p + 2) << " " << p[4] << endl;
    delete[] arr;
    string a = "abc", b = a; b[0] = 'X'; cout << a << " " << b << " " << (a < b) << " " << a + b << endl;
    int x = 7, &r = x; r = 9; cout << x << endl;
    const double PI = 3.14159; cout << PI * 2 * 2 << endl;
    unsigned int u = 3; int neg = -5; cout << (neg < u) << endl;
    return 0;
}
