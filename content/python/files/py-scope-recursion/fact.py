# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "fact" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def factorial(n):
    if n <= 1:                    # base case: stops the recursion
        return 1
    return n * factorial(n - 1)   # recursive case: a smaller problem

for n in range(6):
    print(n, factorial(n))

def countdown(n):
    if n == 0:
        print("Lift off!")
        return
    print(n)
    countdown(n - 1)

countdown(3)
