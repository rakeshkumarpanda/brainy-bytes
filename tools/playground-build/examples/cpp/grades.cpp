#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

class Student {
public:
    string name;
    vector<int> marks;

    Student(string n, vector<int> m) : name(n), marks(m) {}

    double average() const {
        int sum = 0;
        for (int m : marks) sum += m;
        return (double)sum / marks.size();
    }
};

int main() {
    vector<Student> students = {
        Student("Asha", {88, 92, 79}),
        Student("Ravi", {65, 70, 81}),
        Student("Meera", {95, 89, 99})
    };
    sort(students.begin(), students.end(), [](const Student &a, const Student &b) {
        return a.average() > b.average();
    });
    int rank = 1;
    for (const Student &s : students) {
        cout << rank << " " << s.name << " " << fixed << setprecision(1) << s.average() << endl;
        rank++;
    }
    cout << "Top student: " << students[0].name << endl;
    return 0;
}
