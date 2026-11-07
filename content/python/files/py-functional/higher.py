# 4.3 lambda, map, filter and comprehensions
# Example "higher" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import partial

def make_greeter(greeting):          # a function that returns a function
    return lambda name: f"{greeting}, {name}!"

hello = make_greeter("Hello")
namaste = make_greeter("Namaste")
print(hello("Asha"), namaste("Ravi"))

def compose(f, g):                   # (f o g)(x) = f(g(x))
    return lambda x: f(g(x))

shout_len = compose(len, str.upper)
print(shout_len("python"))

base2 = partial(int, base=2)         # fix some arguments of an existing function
print(base2("1011"), base2("11111111"))

pipeline = [str.strip, str.lower, lambda s: s.replace(" ", "-")]
text = "  Hello World Python "
for step in pipeline:
    text = step(text)
print(text)
