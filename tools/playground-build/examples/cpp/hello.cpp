#include <iostream>
#include <string>
using namespace std;

int main() {
    string name;
    int age;
    cout << "What is your name? ";
    cin >> name;
    cout << "How old are you? ";
    cin >> age;
    cout << "Hello, " << name << "!" << endl;
    cout << "In 5 years you will be " << age + 5 << endl;
    if (age >= 13) {
        cout << "You are a teenager or older." << endl;
    } else {
        cout << "You are a kid. Have fun!" << endl;
    }
    return 0;
}
