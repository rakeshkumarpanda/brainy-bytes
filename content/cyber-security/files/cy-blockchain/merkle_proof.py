# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "merkle_proof" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A Merkle tree and a proof that one payment is inside the block (Bitcoin pairs an odd last hash with itself)
import hashlib

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def levels(payments):
    L = [[h(p) for p in payments]]
    while len(L[-1]) > 1:
        cur, nxt = L[-1], []
        for i in range(0, len(cur), 2):
            right = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(h(cur[i] + right))
        L.append(nxt)
    return L

def proof(L, index):
    path = []
    for level in L[:-1]:
        sib = index ^ 1
        if sib >= len(level):
            sib = index
        path.append((level[sib], "right" if sib >= index else "left"))
        index //= 2
    return path

def verify(payment, path, root):
    cur = h(payment)
    for sib, side in path:
        cur = h(cur + sib) if side == "right" else h(sib + cur)
    return cur == root

pays = ["Asha pays Ravi 5", "Ravi pays Meena 2", "Meena pays Arjun 1", "Arjun pays Zoya 3", "Zoya pays Asha 4"]
L = levels(pays)
root = L[-1][0]
print("Merkle root:", root[:24], "...")
p = proof(L, 2)
print("proof for payment 3 uses", len(p), "hashes:", [s[:8] for s, _ in p])
print("verify real payment :", verify("Meena pays Arjun 1", p, root))
print("verify fake payment :", verify("Meena pays Arjun 100", p, root))
for n in (4, 4000, 1_000_000):
    print(f"{n:>9} payments need about {max(1, (n - 1).bit_length())} hashes in a proof")
