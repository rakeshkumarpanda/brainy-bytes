# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "safe_input" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Two classic mistakes with user input: path traversal and command injection
import posixpath
import shlex

BASE = "/srv/files"

def safe_join(base, name):
    full = posixpath.normpath(posixpath.join(base, name))   # turns a/../b into b
    if full == base or full.startswith(base + "/"):
        return full
    return None                                                # outside the folder: refuse

for name in ["report.pdf", "2026/nov.csv", "../../etc/passwd", "/etc/shadow", "a/../../files2/x"]:
    print(repr(name), "->", safe_join(BASE, name))

user_input = "report.pdf && rm -rf ~"
unsafe = "ls -l " + user_input           # a shell would run TWO commands
safer = ["ls", "-l", user_input]         # subprocess.run(safer) passes ONE argument, no shell
print("unsafe string:", unsafe)
print("safe list    :", safer)
print("quoted       :", "ls -l " + shlex.quote(user_input))
