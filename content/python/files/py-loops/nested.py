# 2.2 Loops: while, for, range, break and continue
# Example "nested" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# A small multiplication table: a loop inside a loop
for row in range(1, 4):
    for col in range(1, 6):
        print(f"{row * col:3}", end="")
    print()          # new line after each row

# A triangle of stars
for i in range(1, 5):
    print("*" * i)
