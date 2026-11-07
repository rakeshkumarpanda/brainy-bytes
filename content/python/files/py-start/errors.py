# 1.1 What a program is and your first Python program
# Example "errors" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# compile() checks the grammar of some code without running it.
# We use it here so that this program itself does not stop.
good = 'print("Hi")'
bad = 'print("Hi"'

for source in [good, bad]:
    try:
        compile(source, "test.py", "exec")
        print(source, " -> the grammar is fine")
    except SyntaxError as error:
        print(source, " -> SyntaxError:", error.msg)

# A runtime error only happens when the line runs
try:
    print(10 / 0)
except ZeroDivisionError as error:
    print("Runtime error:", error)
