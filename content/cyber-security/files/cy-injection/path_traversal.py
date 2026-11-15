# 1.2 Injection: SQL, blind SQL, commands, SSRF and paths
# Example "path_traversal" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Path traversal: "../" in a file name escapes the folder the app meant to serve
import posixpath

BASE = "/srv/app/uploads"

def open_buggy(name):
    return posixpath.join(BASE, name)                   # just glues the strings together

def open_safe(name):
    full = posixpath.normpath(posixpath.join(BASE, name))
    if posixpath.commonpath([full, BASE]) != BASE:      # must still be inside BASE after resolving ".."
        return None
    return full

for name in ["report.pdf", "../../../etc/passwd", "photos/../report.pdf", "/etc/shadow", "photos/../../../app/secret.key"]:
    print(f"{name:32} buggy -> {posixpath.normpath(open_buggy(name)):28} safe -> {open_safe(name)}")
