# 1.3 Digital forensics: collecting and reading evidence
# Example "deleted_file" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Why deleted files can come back: a tiny FAT style file system.
# Deleting only marks the directory entry (first byte becomes 0xE5) and frees the clusters. The data stays.
CLUSTER = 8                      # bytes per cluster, tiny so we can print it
disk = bytearray(b"." * 64)      # 8 clusters of free space

directory = []                   # each entry: [name, first cluster, size]

def save(name, data, first):
    disk[first * CLUSTER: first * CLUSTER + len(data)] = data
    directory.append([name, first, len(data)])

def delete(name):
    for entry in directory:
        if entry[0] == name:
            entry[0] = "\xe5" + name[1:]           # FAT marks a deleted entry with 0xE5
    print(f"deleted {name}: the directory now shows {[e[0] for e in directory]!r}")

save("PLAN.TXT", b"Meet at gate 4 at 9pm", 1)
save("LIST.TXT", b"milk eggs", 5)
delete("PLAN.TXT")

print("\nThe disk bytes are untouched:")
print(disk.decode())

for name, first, size in directory:
    if name.startswith("\xe5"):
        data = disk[first * CLUSTER: first * CLUSTER + size]
        print(f"\nrecovered ?{name[1:]} from cluster {first}: {data.decode()!r}")
print("\nThe first letter of the name is lost, so tools show it as ? or _. On SSDs, TRIM often wipes the data soon after.")
