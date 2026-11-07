# 2.2 Loops: while, for, range, break and continue
# Example "breakcont" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# break: stop the whole loop. continue: skip to the next turn.
for n in range(1, 11):
    if n % 2 == 0:
        continue          # skip even numbers
    if n > 7:
        break             # stop completely
    print(n, end=" ")
print()

# else on a loop runs only when there was no break
for n in [3, 7, 11]:
    if n % 2 == 0:
        print("found an even number")
        break
else:
    print("no even number in the list")
