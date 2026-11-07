# 1.2 Variables, values, types and numeral systems
# Example "names" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

age = 25            # the name age now points to the int object 25
my_age = age        # a second name for the SAME object
print(age, my_age)
print(id(age) == id(my_age))   # True: one object, two names

age = age + 1       # a NEW object 26 is made, and age moves to it
print(age, my_age)  # my_age still points to 25
print(id(age) == id(my_age))   # False now
