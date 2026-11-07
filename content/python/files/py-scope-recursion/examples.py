# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "examples" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def total(items):
    if not items:                       # empty list: sum is 0
        return 0
    return items[0] + total(items[1:])  # first item + sum of the rest

def reverse(text):
    if len(text) <= 1:
        return text
    return reverse(text[1:]) + text[0]

def power(base, exp):                   # fast power: halve the exponent
    if exp == 0:
        return 1
    half = power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

def hanoi(n, start, spare, goal, moves):
    if n == 0:
        return
    hanoi(n - 1, start, goal, spare, moves)   # move n - 1 discs out of the way
    moves.append((start, goal))               # move the biggest disc
    hanoi(n - 1, spare, start, goal, moves)   # put the n - 1 discs back on top

print(total([4, 8, 15, 16, 23, 42]))
print(reverse("recursion"))
print(power(2, 10), power(3, 5))
moves = []
hanoi(3, "A", "B", "C", moves)
print(len(moves), "moves:", moves)
