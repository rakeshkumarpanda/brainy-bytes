# 2.1 Operating systems: users, permissions, processes and logs
# Example "octal_perms" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Turn an octal mode such as 754 into the rwx letters that ls -l shows
def letters(digit):
    out = ""
    out = out + ("r" if digit & 4 else "-")    # read is worth 4
    out = out + ("w" if digit & 2 else "-")    # write is worth 2
    out = out + ("x" if digit & 1 else "-")    # execute is worth 1
    return out

for mode in ["754", "644", "600", "777"]:
    text = ""
    for ch in mode:
        text = text + letters(int(ch))
    print(mode, "->", text)

# And back: rwxr-xr-- to octal
def to_octal(text):
    value = {"r": 4, "w": 2, "x": 1, "-": 0}
    result = ""
    for start in [0, 3, 6]:
        total = 0
        for ch in text[start:start + 3]:
            total = total + value[ch]
        result = result + str(total)
    return result

print("rwxr-xr-- ->", to_octal("rwxr-xr--"))
print("rw-r----- ->", to_octal("rw-r-----"))
