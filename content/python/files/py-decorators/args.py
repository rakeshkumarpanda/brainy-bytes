# 1.2 Extended arguments, closures and decorators
# Example "args" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def describe(name, /, age, *hobbies, city="Pune", **extra):
    #        ^ positional only  ^ any number   ^ keyword only   ^ any other keywords
    return f"{name} {age} {hobbies} {city} {extra}"


print(describe("Asha", 30))
print(describe("Asha", age=30, city="Delhi"))
print(describe("Ravi", 25, "chess", "music", lang="hi"))

try:
    describe(name="Asha", age=30)
except TypeError as err:
    print("TypeError:", err)

values = ["Meera", 41, "yoga"]
options = {"city": "Goa", "pet": "cat"}
print(describe(*values, **options))      # * and ** unpack at the call


def forward(*args, **kwargs):            # pass everything on, unchanged
    return describe(*args, **kwargs)


print(forward("Ali", 19, city="Agra"))
