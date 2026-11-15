# 1.2 Incident response: from the first alert to lessons learned
# Example "contain_spread" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Ransomware on a grid of 4 x 6 machines. Each minute it reaches the machines next to an infected one.
# How many machines are hit if the SOC isolates them at minute m, with and without a firewall between the halves?
from collections import deque

ROWS, COLS = 4, 6

def minutes_to_reach(firewall):
    """Breadth first search from the first laptop at row 0, column 0."""
    dist = {(0, 0): 0}
    queue = deque([(0, 0)])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r2, c2 = r + dr, c + dc
            if not (0 <= r2 < ROWS and 0 <= c2 < COLS):
                continue
            if firewall and {c, c2} == {2, 3}:        # the firewall sits between column 2 and column 3
                continue
            if (r2, c2) not in dist:
                dist[(r2, c2)] = dist[(r, c)] + 1
                queue.append((r2, c2))
    return dist

flat = minutes_to_reach(False)
split = minutes_to_reach(True)
print("isolate at minute   flat network   with firewall")
for m in range(1, 10):
    hit_flat = sum(1 for d in flat.values() if d <= m)
    hit_split = sum(1 for d in split.values() if d <= m)
    print(f"{m:17}   {hit_flat:12}   {hit_split:13}")
print("\nFast isolation limits the damage. Segments put a ceiling on it even when the team is slow.")
