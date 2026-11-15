# 1.3 Digital forensics: collecting and reading evidence
# Example "file_carve" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# File carving: find files inside raw bytes by their magic numbers (start and end patterns)
SIGNATURES = {
    "jpeg": (bytes.fromhex("FFD8FF"), bytes.fromhex("FFD9")),
    "pdf": (b"%PDF", b"%%EOF"),
    "png": (bytes.fromhex("89504E470D0A1A0A"), b"IEND"),
}

raw = (bytes.fromhex("0013 7A00 41") + bytes.fromhex("FFD8FFE0104A46FFD9") + bytes.fromhex("0000 2E91 0005 0077")
       + b"%PDF-1\n%%EOF" + bytes.fromhex("003C 0000 1100") + bytes.fromhex("89504E470D0A1A0A"))
print(f"{len(raw)} raw bytes from unallocated space\n")

for kind, (head, foot) in SIGNATURES.items():
    start = raw.find(head)
    while start != -1:
        end = raw.find(foot, start + len(head))
        if end == -1:
            print(f"{kind:4}: header at offset {start}, no footer, partial file of {len(raw) - start} bytes")
        else:
            end += len(foot)                          # include the footer
            print(f"{kind:4}: header at offset {start}, footer ends at {end - 1}, carved {end - start} bytes")
        start = raw.find(head, start + 1)
