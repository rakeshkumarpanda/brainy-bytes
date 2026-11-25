#include <iostream>
#include <iomanip>
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <cctype>
#define SIZE 3
using namespace std;

template <typename T>
T biggest(const vector<T>& v) { T best = v[0]; for (const T& x : v) if (x > best) best = x; return best; }

struct Point { int x, y; };

class Shape {
public:
    virtual double area() const = 0;
    virtual ~Shape() {}
};
class Square : public Shape {
    double side;
public:
    Square(double s) : side(s) {}
    double area() const override { return side * side; }
};

int main() {
    vector<int> v = {5, 2, 9};
    sort(v.begin(), v.end(), greater<int>());
    cout << fixed << setprecision(2) << 3.14159 << endl;
    cout << setw(5) << left << v[0] << boolalpha << true << endl;
    map<string, int> age = {{"Ann", 9}};
    for (auto& [name, a] : age) cout << name << " " << a << "\n";
    string s = "hello";
    transform(s.begin(), s.end(), s.begin(), ::toupper);
    if (s.find("z") == string::npos) cout << s << endl;
    int big = 2147483647;
    long long total = 0;
    for (int i = 0; i < SIZE; i++) total += v[i];
    Point p{1, 2};
    char c{65};
    double d{2.5};
    int arr[] = {1, 2, 3};
    Square sq(2);
    Shape* sh = &sq;
    auto add = [&total](int k) { total += k; return total; };
    cout << biggest(v) << big << total << p.x << c << d << arr[1] << sh->area() << add(1) << endl;
    return 0;
}
