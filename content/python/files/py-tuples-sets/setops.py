# 3.3 Tuples and sets: fixed records and unique items
# Example "setops" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

python_class = {"Asha", "Ravi", "Meera", "John"}
java_class = {"Ravi", "John", "Sara"}

print(python_class | java_class)      # union: in either class
print(python_class & java_class)      # intersection: in both
print(python_class - java_class)      # difference: only Python
print(python_class ^ java_class)      # symmetric difference: in exactly one

print({"Ravi", "John"} <= java_class)            # subset
print(python_class >= {"Asha"})                  # superset
print(python_class.isdisjoint({"Zara", "Leo"}))  # nothing in common
print(python_class.union(["Leo"]))               # the methods take any iterable
