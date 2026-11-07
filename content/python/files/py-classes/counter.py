# 6.1 Classes and objects: attributes, methods, self and encapsulation
# Example "counter" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Student:
    count = 0                          # how many students were made

    def __init__(self, name):
        self.name = name
        Student.count += 1             # change the CLASS attribute
        self.number = Student.count    # each student gets its own number


s1 = Student("Asha")
s2 = Student("Ravi")
s3 = Student("Meera")
print(Student.count, s1.number, s3.number)
print(s1.count)                        # read through an instance: still the class value
