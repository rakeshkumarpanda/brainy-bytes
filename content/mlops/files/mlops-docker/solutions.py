# 2.3 Docker and CI/CD for models
# Model solutions. Try practice.py first.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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


# ================================================================== task 1: Bump a model version
# Model images are tagged with versions like 1.4.2 (major.minor.patch). Write next_version(version,
# change) where change is 'major', 'minor' or 'patch'. A bump sets the parts to its right to 0.
# Why it works: Compare the parts as numbers, not text: 0.9.10 comes after 0.9.9.

def next_version(version, change):
    major, minor, patch = (int(p) for p in version.split('.'))
    if change == 'major':
        return f'{major + 1}.0.0'
    if change == 'minor':
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'


# ================================================================== task 2: A quality gate
# Write passes_gate(y_true, y_pred, gate=0.9) that returns True when the share of matching labels is
# at least gate.
# Why it works: In CI this is one assert, and a failing assert blocks the merge.

def passes_gate(y_true, y_pred, gate=0.9):
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true) >= gate


# ================================================================== task 3: Which Docker layers rebuild?
# Each Dockerfile step is given as the list of files it copies (empty for steps that copy nothing).
# Write rebuilt_steps(steps, changed) that returns the indices of the steps that run again. A step
# runs again if it copies a changed file or any earlier step ran again.
# Why it works: This is why the slow, rarely changing steps belong near the top of the Dockerfile.

def rebuilt_steps(steps, changed):
    out, again = [], False
    for i, files in enumerate(steps):
        if any(f in changed for f in files):
            again = True
        if again:
            out.append(i)
    return out


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Bump a model version", [("next_version('1.4.2', 'patch')", '1.4.3'), ("next_version('1.4.2', 'minor')", '1.5.0'), ("next_version('1.4.2', 'major')", '2.0.0'), ("next_version('0.9.9', 'patch')", '0.9.10')]))
    results.append(check("Task 2: A quality gate", [('passes_gate([0, 1, 2, 2], [0, 1, 2, 1], 0.75)', True), ('passes_gate([0, 1, 2, 2], [0, 1, 2, 1], 0.8)', False), ('passes_gate([1] * 10, [1] * 9 + [0])', True), ('passes_gate([0, 0], [1, 1])', False)]))
    results.append(check("Task 3: Which Docker layers rebuild?", [("rebuilt_steps([[], [], ['requirements.txt'], [], ['app.py'], []], ['app.py'])", [4, 5]), ("rebuilt_steps([[], [], ['requirements.txt'], [], ['app.py'], []], ['requirements.txt'])", [2, 3, 4, 5]), ("rebuilt_steps([[], ['.'], []], [])", []), ("rebuilt_steps([['a', 'b'], []], ['b'])", [0, 1])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
