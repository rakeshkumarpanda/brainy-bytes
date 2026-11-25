class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)

students = [Student("Asha", [88, 92, 79]), Student("Ravi", [65, 70, 81]), Student("Meera", [95, 89, 99])]
students.sort(key=lambda s: s.average(), reverse=True)
for rank, s in enumerate(students, start=1):
    print(rank, s.name, round(s.average(), 1))
print("Top student:", students[0].name)
