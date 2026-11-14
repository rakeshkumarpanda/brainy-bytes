# 2.1 Operating systems: users, permissions, processes and logs
# Example "access_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How the Linux kernel decides: owner first, then group, then other. Only the FIRST class that matches is used.
def can_access(user, user_groups, owner, group, mode, want):
    bit = {"read": 4, "write": 2, "execute": 1}[want]
    if user == "root":
        if want == "execute":
            return (mode & 0o111) != 0      # root still needs some execute bit to run a file
        return True                         # root skips read and write checks
    if user == owner:
        digit = (mode >> 6) & 7
    elif group in user_groups:
        digit = (mode >> 3) & 7
    else:
        digit = mode & 7
    return (digit & bit) != 0

print(can_access("riya", ["staff"], "riya", "staff", 0o754, "write"))   # owner digit 7: True
print(can_access("amit", ["staff"], "riya", "staff", 0o754, "write"))   # group digit 5: False
print(can_access("amit", ["staff"], "riya", "staff", 0o604, "read"))    # group digit 0: False, even though other may read
print(can_access("root", [], "riya", "staff", 0o600, "read"))           # root: True
