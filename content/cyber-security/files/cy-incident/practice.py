# 1.2 Incident response: from the first alert to lessons learned
# Practice tasks. Fill in each function, then run this file.
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
# Hint: Compute the score, then check from the highest level down.

def priority_level(impact, urgency):
    # your code here
    pass


# ================================================================== task 2: Data lost for a backup schedule
# Backups run at hour 0, every, 2 × every and so on. Write work_lost(every, incident) that returns
# the hours between the last backup at or before the incident hour and the incident, rounded to 2
# decimals.
# Hint: Step forward through backup times while the next one is still at or before the incident.

def work_lost(every, incident):
    # your code here
    pass


# ================================================================== task 3: Machines hit before containment
# A grid has rows by cols machines. Infection starts at row 0, column 0 and each minute reaches the
# 4 neighbours of infected machines. If wall is a number w, machines in columns w and w + 1 cannot
# infect each other. Write machines_hit(rows, cols, minutes, wall=None) that returns how many
# machines are infected after the given minutes.
# Hint: Breadth first search gives each machine the minute it is reached. Count those reached by the
# given minute.

from collections import deque

def machines_hit(rows, cols, minutes, wall=None):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Priority from impact and urgency", [('priority_level(3, 3)', 'P1'), ('priority_level(3, 2)', 'P2'), ('priority_level(2, 2)', 'P3'), ('priority_level(1, 3)', 'P3'), ('priority_level(1, 2)', 'P4')]))
    results.append(check("Task 2: Data lost for a backup schedule", [('work_lost(4, 15.5)', 3.5), ('work_lost(24, 15.5)', 15.5), ('work_lost(1, 15.5)', 0.5), ('work_lost(12, 12)', 0.0), ('work_lost(5, 23)', 3.0)]))
    results.append(check("Task 3: Machines hit before containment", [('machines_hit(4, 6, 3)', 10), ('machines_hit(4, 6, 9)', 24), ('machines_hit(4, 6, 9, wall=2)', 12), ('machines_hit(1, 1, 5)', 1), ('machines_hit(3, 3, 0)', 1)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
