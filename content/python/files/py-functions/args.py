# 4.1 Functions: def, return and every kind of argument
# Example "args" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def describe(name, age, city="Pune"):
    print(f"{name} is {age} and lives in {city}")

describe("Asha", 21)                       # positional, city uses its default
describe("Ravi", 23, "Delhi")              # all positional
describe(age=30, name="Meera")             # keyword: any order
describe("John", city="Goa", age=40)       # positional first, then keyword
# describe(name="Sara", 25) would be a SyntaxError: the whole file would not run
