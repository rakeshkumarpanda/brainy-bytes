# 2.1 Operating systems: users, permissions, processes and logs
# Example "passwd_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Audit a copy of /etc/passwd: every account with user id 0 has full root power
passwd = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
riya:x:1000:1000:Riya:/home/riya:/bin/bash
backup:x:0:0:old backup job:/var/backups:/bin/bash
www-data:x:33:33:web server:/var/www:/usr/sbin/nologin"""

for line in passwd.split("\n"):
    name, password, uid, gid, comment, home, shell = line.split(":")
    if uid == "0":
        warning = "  <-- root power" if name != "root" else ""
        print("uid 0:", name + warning)
    if not shell.endswith("nologin") and int(uid) >= 1000:
        print("person who can log in:", name)
