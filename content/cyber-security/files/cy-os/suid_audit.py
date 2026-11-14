# 2.1 Operating systems: users, permissions, processes and logs
# Example "suid_audit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Find files with the setuid bit (octal 4000). A setuid program runs with its OWNER's rights.
files_found = [
    ("/usr/bin/passwd", "root", 0o4755),
    ("/usr/bin/sudo", "root", 0o4755),
    ("/home/riya/tool", "riya", 0o0755),
    ("/opt/backup/run.sh", "root", 0o4777),
    ("/usr/bin/ls", "root", 0o0755),
]

expected = ["/usr/bin/passwd", "/usr/bin/sudo"]
for path, owner, mode in files_found:
    if mode & 0o4000:
        risky = ""
        if mode & 0o002:
            risky = " and ANYONE can change it: a user could put their own code here and run it as root"
        elif path not in expected:
            risky = " (unexpected, check why)"
        print("setuid", format(mode, "04o"), owner, path + risky)
