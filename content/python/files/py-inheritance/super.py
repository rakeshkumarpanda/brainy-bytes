# 6.2 Inheritance: super(), overriding, polymorphism and the MRO
# Example "super" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary // 12       # monthly pay


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary) # let the parent set name and salary
        self.bonus = bonus             # then add what is new

    def pay(self):
        return super().pay() + self.bonus   # extend the parent method, do not copy it


ravi = Employee("Ravi", 24000)
asha = Manager("Asha", 36000, 500)
print(ravi.pay(), asha.pay())
print(asha.__dict__)
