# 2.1 Memory safety: overflows, ASLR, use after free and Rust
# Example "aslr_entropy" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How much does address space layout randomisation (ASLR) help? It depends on the bits of randomness
# and on whether a crash gives the attacker a fresh random layout or the same one again.
def expected_tries(bits, rerandomised):
    n = 2 ** bits
    return n if rerandomised else (n + 1) / 2          # with replacement versus without replacement

def p_success(bits, tries, rerandomised):
    n = 2 ** bits
    return 1 - (1 - 1 / n) ** tries if rerandomised else min(1.0, tries / n)

for name, bits in [("32 bit Linux mmap (about 8 bits)", 8), ("Shacham et al. 2004 target (16 bits)", 16),
                   ("64 bit Linux mmap (28 bits)", 28)]:
    e = expected_tries(bits, False)
    print(f"{name:38} expected guesses {e:>16,.1f}   P(win in 1000 tries) = {p_success(bits, 1000, False):.6f}")

print("\nA forking server keeps the same layout in every child, so each guess rules one address out.")
print("Re-randomising on every restart turns guessing into a fresh lottery each time:")
for bits in (8, 16):
    print(f"   {bits} bits: same layout {expected_tries(bits, False):>8,.1f} tries, fresh layout {expected_tries(bits, True):>8,} tries")
print("\nAn information leak of one pointer reveals the whole offset and makes ASLR worthless for that run.")
