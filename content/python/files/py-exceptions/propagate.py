# 5.1 Exceptions: try, except, else, finally and raise
# Example "propagate" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def average(marks):
    return sum(marks) / len(marks)       # raises for an empty list

def report(marks):
    return "Average: " + str(average(marks))   # does not handle it either

for group in [[70, 80, 90], []]:
    try:
        print(report(group))             # the caller decides what to do
    except ZeroDivisionError:
        print("No marks yet")
