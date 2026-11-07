# 2.1 Making decisions: if, elif, else and match
# Example "grade" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def grade(score):
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "F"

for s in [95, 90, 82, 50, 49, 0]:
    print(s, grade(s))
