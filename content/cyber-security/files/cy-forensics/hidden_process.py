# 1.3 Digital forensics: collecting and reading evidence
# Example "hidden_process" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Memory forensics in miniature: list walking versus scanning.
# Windows keeps running processes in a linked list. Rootkits unlink themselves (DKOM) so the list skips them.
# Scanning all of memory for the process structure's signature still finds them, as Volatility's psscan does.
memory = {
    0x1000: {"tag": "Proc", "pid": 4, "name": "System", "next": 0x2000},
    0x2000: {"tag": "Proc", "pid": 612, "name": "lsass.exe", "next": 0x3000},
    0x3000: {"tag": "Proc", "pid": 1880, "name": "explorer.exe", "next": 0x5000},
    0x4000: {"tag": "Proc", "pid": 6666, "name": "svch0st.exe", "next": 0x5000},   # unlinked: nobody points here
    0x5000: {"tag": "Proc", "pid": 2210, "name": "chrome.exe", "next": None},
    0x6000: {"tag": "Data", "text": "random heap bytes"},
}

def walk_list(head):
    found, addr = [], head
    while addr is not None:
        proc = memory[addr]
        found.append((proc["pid"], proc["name"]))
        addr = proc["next"]
    return found

def scan_memory():
    return [(m["pid"], m["name"]) for addr, m in sorted(memory.items()) if m["tag"] == "Proc"]

listed = walk_list(0x1000)
scanned = scan_memory()
print("pslist (walk the list):", [n for _, n in listed])
print("psscan (scan memory):  ", [n for _, n in scanned])
hidden = set(scanned) - set(listed)
print("\nIn the scan but not in the list:", hidden)
print("A process named svch0st.exe (zero, not o) hiding from the list is a strong sign of a rootkit.")
