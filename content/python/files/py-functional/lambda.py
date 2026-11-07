# 4.3 lambda, map, filter and comprehensions
# Example "lambda" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

square = lambda x: x * x        # a tiny function without a def
print(square(7))

add = lambda a, b=10: a + b     # parameters and defaults work as usual
print(add(1), add(1, 2))

def square_def(x):              # the same thing with def
    return x * x
print(square_def(7), square.__name__, square_def.__name__)

print((lambda word: word[::-1])("level"))    # called at once
