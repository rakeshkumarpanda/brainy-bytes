# 1.4 Exceptions in depth, copying and serialisation
# Example "groups" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def check(user):
    problems = []
    if not user.get("name"):
        problems.append(ValueError("name is empty"))
    if user.get("age", 0) < 0:
        problems.append(ValueError("age is negative"))
    if "@" not in user.get("email", ""):
        problems.append(TypeError("email has no @"))
    if problems:
        raise ExceptionGroup("the form has errors", problems)   # report them ALL at once
    return "ok"


try:
    check({"name": "", "age": -1, "email": "asha.example.com"})
except* ValueError as group:                   # except* handles part of a group
    for err in group.exceptions:
        print("value problem:", err)
except* TypeError as group:
    for err in group.exceptions:
        print("type problem:", err)

print(check({"name": "Asha", "age": 30, "email": "a@b.in"}))
