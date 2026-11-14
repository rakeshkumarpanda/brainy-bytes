# 1.1 Set up your computer for machine learning
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


# ================================================================== task 1: Read one line of requirements.txt
# Write parse_requirement(line) that returns [name, operator, version] for lines such as
# numpy==2.4.6 or joblib>=1.4 (operators == and >=), and None for blank lines and comments. Ignore
# spaces and anything after a #.
# Why it works: Real requirement lines can also have extras, markers and other operators. The
# packaging library parses all of them, and this task covers the two you see most.

def parse_requirement(line):
    line = line.split('#')[0].strip()
    if not line:
        return None
    for op in ('==', '>='):
        if op in line:
            name, version = line.split(op)
            return [name.strip(), op, version.strip()]
    return None


# ================================================================== task 2: Does the installed version satisfy the requirement?
# Write version_ok(installed, op, wanted) that compares dotted versions such as 2.4.6 number by
# number (so 1.10 is newer than 1.9). For == return whether they are equal, for >= whether installed
# is at least wanted.
# Why it works: Comparing versions as text gets 1.10 against 1.9 wrong, because the character 1
# sorts before 9. Comparing numbers fixes it.

def version_ok(installed, op, wanted):
    a = [int(p) for p in installed.split('.')]
    b = [int(p) for p in wanted.split('.')]
    n = max(len(a), len(b))
    a, b = a + [0] * (n - len(a)), b + [0] * (n - len(b))
    return a == b if op == '==' else a >= b


# ================================================================== task 3: Find a command on PATH
# Write find_on_path(path, contents, command). path is a list of folder names in search order and
# contents is a dictionary from folder name to the list of programs in it. Return the first folder
# that contains the command, or 'not found'.
# Why it works: The last test shows why order matters: with .venv/bin second, the system python3
# wins. Activating an environment puts its folder first.

def find_on_path(path, contents, command):
    for folder in path:
        if command in contents.get(folder, []):
            return folder
    return 'not found'


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Read one line of requirements.txt", [("parse_requirement('numpy==2.4.6')", ['numpy', '==', '2.4.6']), ("parse_requirement('joblib >= 1.4  # any newer one')", ['joblib', '>=', '1.4']), ("parse_requirement('# comment')", None), ("parse_requirement('')", None)]))
    results.append(check("Task 2: Does the installed version satisfy the requirement?", [("version_ok('2.4.6', '==', '2.4.6')", True), ("version_ok('1.10.0', '>=', '1.9')", True), ("version_ok('2.3.5', '>=', '2.4')", False), ("version_ok('2.4.6', '==', '2.3.5')", False)]))
    results.append(check("Task 3: Find a command on PATH", [("find_on_path(['/usr/bin', '/bin'], {'/usr/bin': ['python3'], '/bin': ['ls']}, 'python')", 'not found'), ("find_on_path(['.venv/bin', '/usr/bin'], {'.venv/bin': ['python', 'pip'], '/usr/bin': ['python3']}, 'python')", '.venv/bin'), ("find_on_path(['/usr/bin', '.venv/bin'], {'.venv/bin': ['python3'], '/usr/bin': ['python3']}, 'python3')", '/usr/bin')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
