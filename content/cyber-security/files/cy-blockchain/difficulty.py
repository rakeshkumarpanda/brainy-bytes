# 3.1 Blockchain security: hash chains, mining, consensus and wallets
# Example "difficulty" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How Bitcoin keeps one block about every 10 minutes: the difficulty retarget every 2016 blocks
TARGET_SECONDS = 2016 * 600              # two weeks

def retarget(old_difficulty, actual_seconds):
    # Bitcoin limits one adjustment to a factor of 4 in either direction
    actual = min(max(actual_seconds, TARGET_SECONDS / 4), TARGET_SECONDS * 4)
    return old_difficulty * TARGET_SECONDS / actual

d = 100.0
for days, why in [(14, "on time"), (10, "new machines joined, blocks came fast"),
                  (20, "miners left after a price fall"), (2, "a huge jump, capped at 4 times")]:
    new = retarget(d, days * 86400)
    print(f"2016 blocks took {days:2d} days ({why}): difficulty {d:7.2f} -> {new:7.2f}")
    d = new

# expected hashes for a given number of leading zero bits
for bits in (20, 40, 78):
    print(f"{bits} zero bits: about 2^{bits} = {2 ** bits:.3e} hashes per block")
