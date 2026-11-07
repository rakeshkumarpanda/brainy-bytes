# 2.1 Making decisions: if, elif, else and match
# Example "ternary" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

n = 7
kind = "even" if n % 2 == 0 else "odd"     # conditional expression
print(n, "is", kind)
fee = 0 if n < 5 else 50 if n < 10 else 100
print("fee:", fee)
print(abs(-4), max(3, 9), min(3, 9))        # built ins that hide an if
