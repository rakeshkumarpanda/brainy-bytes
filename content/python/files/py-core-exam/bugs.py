# 7.1 Exam practice: PCEP and PCAP style papers
# Example "bugs" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Bug 1: changing a list while looping over it
nums = [2, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print("bug 1:", nums)
nums = [2, 4, 5, 6]
print("fix 1:", [n for n in nums if n % 2 != 0])

# Bug 2: a string method does not change the string
name = "asha"
name.upper()
print("bug 2:", name)
name = name.upper()
print("fix 2:", name)

# Bug 3: a function that forgets return
def area(w, h):
    w * h
print("bug 3:", area(3, 4))
def area(w, h):
    return w * h
print("fix 3:", area(3, 4))

# Bug 4: a broad except before a narrow one
def parse(text):
    try:
        return int(text)
    except Exception:
        return "something went wrong"
    except ValueError:                      # never reached
        return "not a number"
print("bug 4:", parse("x"))
def parse(text):
    try:
        return int(text)
    except ValueError:
        return "not a number"
print("fix 4:", parse("x"))

# Bug 5: input() always gives a str
typed = "7"                                 # what input() would return
print("bug 5:", typed * 2)
print("fix 5:", int(typed) * 2)

# Bug 6: a built in name used as a variable
list = [1, 2, 3]
try:
    list("abc")
except TypeError as err:
    print("bug 6:", err)
del list                                    # removes the shadow, the built in is back
print("fix 6:", list("abc"))
