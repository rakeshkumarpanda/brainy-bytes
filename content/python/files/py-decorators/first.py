# 1.2 Extended arguments, closures and decorators
# Example "first" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def shout(text):
    return text.upper() + "!"


def whisper(text):
    return text.lower() + "..."


say = shout                              # a function is an object: give it another name
print(say("hi"), say.__name__)

actions = {"loud": shout, "soft": whisper}
print(actions["soft"]("HELLO"))          # store functions in a dict


def apply_twice(func, value):            # pass a function as an argument
    return func(func(value))


print(apply_twice(shout, "go"))


def make_greeter(greeting):              # return a new function
    def greet(name):
        return greeting + ", " + name
    return greet


hello = make_greeter("Hello")
namaste = make_greeter("Namaste")
print(hello("Asha"), "|", namaste("Ravi"))
print(namaste.__closure__[0].cell_contents)   # the value the closure remembers
