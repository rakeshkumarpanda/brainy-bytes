#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <string>
#include <algorithm>
#include <stack>
#include <queue>
#include <iomanip>
#include <sstream>
#include <numeric>
#include <unordered_map>
using namespace std;

class Animal {
protected:
    string name;
public:
    Animal(string n) : name(n) {}
    virtual string sound() const { return "..."; }
    virtual ~Animal() {}
    string describe() const { return name + " says " + sound(); }
};

class Dog : public Animal {
public:
    Dog(string n) : Animal(n) {}
    string sound() const override { return "woof"; }
};

struct Point {
    int x, y;
    Point(int x = 0, int y = 0) : x(x), y(y) {}
    Point operator+(const Point &o) const { return Point(x + o.x, y + o.y); }
    bool operator<(const Point &o) const { return x < o.x || (x == o.x && y < o.y); }
};

ostream &operator<<(ostream &os, const Point &p) { return os << "(" << p.x << "," << p.y << ")"; }

template <typename T>
T biggest(const vector<T> &v) { T b = v[0]; for (const T &x : v) if (x > b) b = x; return b; }

void addOne(int &r) { r++; }
int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }

int main() {
    vector<int> v = {5, 3, 8, 1, 9, 2};
    sort(v.begin(), v.end());
    for (int x : v) cout << x << " ";
    cout << endl;
    sort(v.begin(), v.end(), greater<int>());
    cout << v[0] << " " << v.size() << " " << v.back() << endl;
    v.push_back(7); v.erase(v.begin());
    cout << accumulate(v.begin(), v.end(), 0) << " " << *max_element(v.begin(), v.end()) << " " << count(v.begin(), v.end(), 7) << endl;
    auto it = find(v.begin(), v.end(), 3);
    cout << (it != v.end() ? "found at " + to_string(it - v.begin()) : "missing") << endl;
    reverse(v.begin(), v.end());
    for (size_t i = 0; i < v.size(); i++) cout << v[i] << (i + 1 < v.size() ? "," : "\n");
    map<string, int> age;
    age["zed"] = 30; age["amy"] = 25; age["bob"] = 41;
    for (auto &p : age) cout << p.first << ":" << p.second << " ";
    cout << age.count("amy") << " " << age.size() << endl;
    for (const auto &[k, val] : age) cout << k << val;
    cout << "\n";
    set<int> s = {4, 1, 4, 2};
    s.insert(3);
    for (int x : s) cout << x;
    cout << " " << s.count(4) << endl;
    stack<int> st; st.push(1); st.push(2); cout << st.top() << " "; st.pop(); cout << st.size() << endl;
    queue<string> q; q.push("a"); q.push("b"); cout << q.front() << q.back() << endl;
    priority_queue<int> pq; for (int x : {3, 1, 4, 1, 5}) pq.push(x);
    while (!pq.empty()) { cout << pq.top() << " "; pq.pop(); }
    cout << endl;
    Dog d("Rex");
    Animal *a = &d;
    cout << a->describe() << endl;
    vector<Animal *> zoo = {new Dog("Fido"), new Animal("Fish")};
    for (auto z : zoo) cout << z->describe() << "; ";
    cout << endl;
    Point p1(1, 2), p2(3, 4);
    cout << p1 + p2 << " " << (p1 < p2) << endl;
    vector<Point> pts = {Point(3, 1), Point(1, 5), Point(1, 2)};
    sort(pts.begin(), pts.end());
    for (auto &p : pts) cout << p;
    cout << endl;
    cout << biggest(vector<int>{4, 9, 2}) << " " << biggest(vector<string>{"pear", "zoo", "apple"}) << endl;
    int n = 5; addOne(n); cout << n << " " << gcd(48, 18) << endl;
    string str = "Hello World";
    cout << str.length() << " " << str.substr(6) << " " << str.find("World") << " " << str[0] << endl;
    transform(str.begin(), str.end(), str.begin(), ::toupper);
    cout << str << endl;
    cout << fixed << setprecision(3) << 3.14159 << " " << 2.0 / 3 << endl;
    cout.unsetf(ios::fixed); cout << setprecision(6);
    cout << 1.0 / 3 << " " << 100.0 << " " << 1e20 << " " << 0.1 + 0.2 << endl;
    cout << setw(5) << 42 << "|" << left << setw(5) << 7 << "|" << endl;
    stringstream ss("10 20 30"); int t, tot = 0; while (ss >> t) tot += t; cout << tot << endl;
    auto sq = [](int x) { return x * x; };
    int base = 10;
    auto addb = [&](int x) { return x + base; };
    cout << sq(7) << " " << addb(5) << endl;
    unordered_map<int, int> cnt;
    for (int x : {1, 2, 1, 3, 1}) cnt[x]++;
    cout << cnt[1] << " " << cnt.size() << endl;
    pair<int, string> pr = make_pair(1, "one");
    cout << pr.first << pr.second << endl;
    int arr[] = {3, 1, 2};
    sort(arr, arr + 3);
    cout << arr[0] << arr[1] << arr[2] << " " << sizeof(arr) / sizeof(arr[0]) << endl;
    int *ptr = new int(42); cout << *ptr << endl; delete ptr;
    string name; int num;
    cin >> name >> num;
    cout << "Hi " << name << ", " << num * 2 << endl;
    char c = 'a'; cout << c << " " << (int)c << " " << char(c + 1) << " " << c + 1 << endl;
    cout << 7 / 2 << " " << 7.0 / 2 << " " << (true ? "yes" : "no") << " " << true << endl;
    long long big = 1LL << 40; cout << big << endl;
    vector<vector<int>> grid(2, vector<int>(3, 0));
    grid[1][2] = 5; cout << grid[1][2] << grid.size() << grid[0].size() << endl;
    try { throw runtime_error("boom"); } catch (const exception &e) { cout << "caught " << e.what() << endl; }
    vector<int> e2;
    cout << v.at(100) << endl;
    return 0;
}
