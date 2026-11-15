# 1.2 Incident response: from the first alert to lessons learned
# Model solutions. Try practice.py first.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Priority from impact and urgency
# Write priority_level(impact, urgency) where each is 1, 2 or 3. Multiply them. Return "P1" for 9,
# "P2" for 6, "P3" for 3 or 4, and "P4" for 1 or 2.
# Why it works: Real teams add more inputs, such as whether personal data is involved, but the idea
# of a small fixed table stays the same, so everyone sorts alerts the same way.

def priority_level(impact, urgency):
    score = impact * urgency
    if score >= 9:
        return "P1"
    if score >= 6:
        return "P2"
    if score >= 3:
        return "P3"
    return "P4"


# ================================================================== task 2: Data lost for a backup schedule
# Backups run at hour 0, every, 2 × every and so on. Write work_lost(every, incident) that returns
# the hours between the last backup at or before the incident hour and the incident, rounded to 2
# decimals.
# Why it works: The same answer comes from incident % every, the remainder after dividing. The loop
# shows the idea more plainly.

def work_lost(every, incident):
    last = 0
    while last + every <= incident:
        last += every
    return round(float(incident - last), 2)


# ================================================================== task 3: Machines hit before containment
# A grid has rows by cols machines. Infection starts at row 0, column 0 and each minute reaches the
# 4 neighbours of infected machines. If wall is a number w, machines in columns w and w + 1 cannot
# infect each other. Write machines_hit(rows, cols, minutes, wall=None) that returns how many
# machines are infected after the given minutes.
# Why it works: Real networks are graphs, not grids, but the same search shows which machines an
# attacker can reach and how a segment wall changes that.

from collections import deque

def machines_hit(rows, cols, minutes, wall=None):
    dist = {(0, 0): 0}
    queue = deque([(0, 0)])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r2, c2 = r + dr, c + dc
            if not (0 <= r2 < rows and 0 <= c2 < cols):
                continue
            if wall is not None and {c, c2} == {wall, wall + 1}:
                continue
            if (r2, c2) not in dist:
                dist[(r2, c2)] = dist[(r, c)] + 1
                queue.append((r2, c2))
    count = 0
    for d in dist.values():
        if d <= minutes:
            count += 1
    return count


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Priority from impact and urgency", [('priority_level(3, 3)', 'P1'), ('priority_level(3, 2)', 'P2'), ('priority_level(2, 2)', 'P3'), ('priority_level(1, 3)', 'P3'), ('priority_level(1, 2)', 'P4')]))
    results.append(check("Task 2: Data lost for a backup schedule", [('work_lost(4, 15.5)', 3.5), ('work_lost(24, 15.5)', 15.5), ('work_lost(1, 15.5)', 0.5), ('work_lost(12, 12)', 0.0), ('work_lost(5, 23)', 3.0)]))
    results.append(check("Task 3: Machines hit before containment", [('machines_hit(4, 6, 3)', 10), ('machines_hit(4, 6, 9)', 24), ('machines_hit(4, 6, 9, wall=2)', 12), ('machines_hit(1, 1, 5)', 1), ('machines_hit(3, 3, 0)', 1)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
