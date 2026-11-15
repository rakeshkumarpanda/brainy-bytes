# 1.3 Digital forensics: collecting and reading evidence
# Example "image_hash" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Proving a disk image never changed: hash it when it is made, and again every time it is used
import hashlib

# a pretend 4 KB disk image made of repeating text (a real one is a file of many gigabytes)
image = (b"Quarterly report draft. " * 200)[:4096]

def fingerprint(data):
    return hashlib.sha256(data).hexdigest()

at_seizure = fingerprint(image)
print("hash recorded at seizure:", at_seizure[:16], "...")

at_lab = fingerprint(image)
print("hash at the lab:         ", at_lab[:16], "...", "MATCH" if at_lab == at_seizure else "DIFFERENT")

# someone mounts the original without a write blocker and one byte changes
changed = bytearray(image)
changed[100] ^= 1                      # flip a single bit
after_mistake = fingerprint(bytes(changed))
print("hash after one bit flip: ", after_mistake[:16], "...", "MATCH" if after_mistake == at_seizure else "DIFFERENT")

same = sum(1 for a, b in zip(at_seizure, after_mistake) if a == b)
print(f"\nOnly 1 bit of 32768 changed, yet only {same} of 64 hex digits of the hash stayed the same.")
print("This is the avalanche effect, and it is why one hash can stand for a whole disk.")
