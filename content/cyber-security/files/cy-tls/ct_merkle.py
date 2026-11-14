# 1.1 Certificates, PKI and TLS 1.3
# Example "ct_merkle" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Certificate Transparency: a public append only log built as a Merkle tree (RFC 6962 hashing)
import hashlib

def leaf_hash(entry):
    return hashlib.sha256(b"\x00" + entry).digest()      # 0x00 marks a leaf

def node_hash(left, right):
    return hashlib.sha256(b"\x01" + left + right).digest()   # 0x01 marks an inner node

def root(hashes):
    if len(hashes) == 1:
        return hashes[0]
    k = 1
    while k * 2 < len(hashes):                          # largest power of two below the size
        k = k * 2
    return node_hash(root(hashes[:k]), root(hashes[k:]))

def proof(hashes, index):                               # the sibling hashes from the leaf up to the root
    if len(hashes) == 1:
        return []
    k = 1
    while k * 2 < len(hashes):
        k = k * 2
    if index < k:
        return proof(hashes[:k], index) + [("R", root(hashes[k:]))]
    return proof(hashes[k:], index - k) + [("L", root(hashes[:k]))]

def verify(entry, path, expected_root):
    h = leaf_hash(entry)
    for side, sibling in path:
        h = node_hash(h, sibling) if side == "R" else node_hash(sibling, h)
    return h == expected_root

certs = [f"certificate {i} for site{i}.example".encode() for i in range(7)]
hashes = [leaf_hash(c) for c in certs]
signed_root = root(hashes)                              # the log signs this and publishes it
print("log of", len(certs), "certificates, root", signed_root.hex()[:16], "...")

path = proof(hashes, 5)
print("inclusion proof for certificate 5 has", len(path), "hashes (about log2 of the log size)")
print("certificate 5 is in the log:", verify(certs[5], path, signed_root))
print("a forged certificate passes:", verify(b"certificate 5 for evil.example", path, signed_root))
print("a log of 1 billion entries needs about", (10 ** 9).bit_length(), "hashes per proof")
