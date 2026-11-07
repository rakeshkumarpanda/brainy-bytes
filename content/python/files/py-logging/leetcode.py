# 3.3 Logging and debugging
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


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


# ================================================================== 937. Reorder Data in Log Files (Medium)
# https://leetcode.com/problems/reorder-data-in-log-files/
# Pattern: A sort key that splits two kinds of logs
# Idea: Letter logs come first, sorted by content then identifier. Digit logs keep their order:
# sorted is stable, so give them all the same key.

def reorder_log_files(logs):
    def key(log):
        ident, rest = log.split(" ", 1)
        if rest[0].isalpha():
            return (0, rest, ident)
        return (1,)
    return sorted(logs, key=key)


# ================================================================== 1598. Crawler Log Folder (Easy)
# https://leetcode.com/problems/crawler-log-folder/
# Pattern: Track the depth
# Idea: "../" goes up one level (never above the top), "./" stays, anything else goes one level
# down.

def min_operations(logs):
    depth = 0
    for entry in logs:
        if entry == "../":
            depth = max(0, depth - 1)
        elif entry != "./":
            depth += 1
    return depth


# ================================================================== 2933. High-Access Employees (Medium)
# https://leetcode.com/problems/high-access-employees/
# Pattern: Group times per person, then a window of 3
# Idea: Turn "hhmm" into minutes, sort each person's times, and check whether any 3 in a row fit
# within 59 minutes.

def find_high_access_employees(access_times):
    times = {}
    for name, hhmm in access_times:
        minutes = int(hhmm[:2]) * 60 + int(hhmm[2:])
        times.setdefault(name, []).append(minutes)
    result = []
    for name, moments in times.items():
        moments.sort()
        for i in range(2, len(moments)):
            if moments[i] - moments[i - 2] < 60:
                result.append(name)
                break
    return sorted(result)


# ================================================================== 1604. Alert Using Same Key-Card Three or More Times in a One Hour Period (Medium)
# https://leetcode.com/problems/alert-using-same-key-card-three-or-more-times-in-a-one-hour-period/
# Pattern: The same window idea on access logs
# Idea: Group by name, sort the minutes, and alert if times[i] − times[i − 2] is at most 60.

def alert_names(keyName, keyTime):
    times = {}
    for name, clock in zip(keyName, keyTime):
        hours, minutes = clock.split(":")
        times.setdefault(name, []).append(int(hours) * 60 + int(minutes))
    alerts = []
    for name, moments in times.items():
        moments.sort()
        if any(moments[i] - moments[i - 2] <= 60 for i in range(2, len(moments))):
            alerts.append(name)
    return sorted(alerts)


# ================================================================== 1817. Finding the Users Active Minutes (Medium)
# https://leetcode.com/problems/finding-the-users-active-minutes/
# Pattern: A set of minutes per user
# Idea: Collect each user's different minutes in a set. The size of the set is that user's active
# minutes. Count users per size.

def finding_users_active_minutes(logs, k):
    minutes = {}
    for user, minute in logs:
        minutes.setdefault(user, set()).add(minute)
    answer = [0] * k
    for active in minutes.values():
        answer[len(active) - 1] += 1
    return answer


# ================================================================== 2747. Count Zero Request Servers (Medium)
# https://leetcode.com/problems/count-zero-request-servers/
# Pattern: Sort logs and queries, slide a window
# Idea: Sort logs by time. Answer queries in time order with two pointers that keep only logs inside
# [q − x, q] and a count per server.

def count_servers(n, logs, x, queries):
    logs = sorted(logs, key=lambda log: log[1])
    order = sorted(range(len(queries)), key=lambda i: queries[i])
    count = {}
    answer = [0] * len(queries)
    left = right = 0
    for i in order:
        q = queries[i]
        while right < len(logs) and logs[right][1] <= q:
            server = logs[right][0]
            count[server] = count.get(server, 0) + 1
            right += 1
        while left < right and logs[left][1] < q - x:
            server = logs[left][0]
            count[server] -= 1
            if count[server] == 0:
                del count[server]
            left += 1
        answer[i] = n - len(count)
    return answer


# ================================================================== 1169. Invalid Transactions (Medium)
# https://leetcode.com/problems/invalid-transactions/
# Pattern: Parse, then compare every pair
# Idea: A transaction is invalid above 1000, or when the same name has another one in a different
# city within 60 minutes.

def invalid_transactions(transactions):
    parsed = []
    for t in transactions:
        name, time, amount, city = t.split(",")
        parsed.append((name, int(time), int(amount), city))
    result = []
    for i, (name, time, amount, city) in enumerate(parsed):
        bad = amount > 1000
        for other_name, other_time, other_amount, other_city in parsed:
            if other_name == name and other_city != city and abs(other_time - time) <= 60:
                bad = True
        if bad:
            result.append(transactions[i])
    return result


# ================================================================== 609. Find Duplicate File in System (Medium)
# https://leetcode.com/problems/find-duplicate-file-in-system/
# Pattern: Parse lines into a dict by content
# Idea: Each line is a folder then files like name(content). Group full paths by content and keep
# groups with more than one file.

def find_duplicate(paths):
    by_content = {}
    for line in paths:
        folder, *files = line.split(" ")
        for entry in files:
            name, content = entry[:-1].split("(")
            by_content.setdefault(content, []).append(folder + "/" + name)
    return [group for group in by_content.values() if len(group) > 1]


# ================================================================== 388. Longest Absolute File Path (Medium)
# https://leetcode.com/problems/longest-absolute-file-path/
# Pattern: A stack of path lengths by depth
# Idea: The number of tabs is the depth. Keep the total length of the path at each depth. A name
# with a dot is a file.

def length_longest_path(text):
    length_at = {0: 0}
    best = 0
    for line in text.split("\n"):
        name = line.lstrip("\t")
        depth = len(line) - len(name)
        if "." in name:
            best = max(best, length_at[depth] + len(name))
        else:
            length_at[depth + 1] = length_at[depth] + len(name) + 1
    return best


# ================================================================== 165. Compare Version Numbers (Medium)
# https://leetcode.com/problems/compare-version-numbers/
# Pattern: Compare number by number
# Idea: Split on dots, turn each part into an int (so 01 equals 1) and treat missing parts as 0.

from itertools import zip_longest


def compare_version(version1, version2):
    parts1 = [int(p) for p in version1.split(".")]
    parts2 = [int(p) for p in version2.split(".")]
    for a, b in zip_longest(parts1, parts2, fillvalue=0):
        if a != b:
            return 1 if a > b else -1
    return 0


if __name__ == "__main__":
    results = []
    results.append(check("937. Reorder Data in Log Files", [('reorder_log_files(["dig1 8 1 5 1", "let1 art can", "dig2 3 6", "let2 own kit dig", "let3 art zero"])', ['let1 art can', 'let3 art zero', 'let2 own kit dig', 'dig1 8 1 5 1', 'dig2 3 6'])]))
    results.append(check("1598. Crawler Log Folder", [('min_operations(["d1/", "d2/", "../", "d21/", "./"])', 2), ('min_operations(["d1/", "../", "../", "../"])', 0)]))
    results.append(check("2933. High-Access Employees", [('find_high_access_employees([["a", "0549"], ["b", "0457"], ["a", "0532"], ["a", "0621"], ["b", "0540"]])', ['a']), ('find_high_access_employees([["cd", "1025"], ["ab", "1025"], ["cd", "1046"], ["cd", "1055"], ["ab", "1124"], ["ab", "1120"]])', ['ab', 'cd'])]))
    results.append(check("1604. Alert Using Same Key-Card Three or More Times in a One Hour Period", [('alert_names(["daniel", "daniel", "daniel", "luis", "luis", "luis", "luis"], ["10:00", "10:40", "11:00", "09:00", "11:00", "13:00", "15:00"])', ['daniel']), ('alert_names(["alice", "alice", "alice", "bob", "bob", "bob", "bob"], ["12:01", "12:00", "18:00", "21:00", "21:20", "21:30", "23:00"])', ['bob'])]))
    results.append(check("1817. Finding the Users Active Minutes", [('finding_users_active_minutes([[0, 5], [1, 2], [0, 2], [0, 5], [1, 3]], 5)', [0, 2, 0, 0, 0]), ('finding_users_active_minutes([[1, 1], [2, 2], [2, 3]], 4)', [1, 1, 0, 0])]))
    results.append(check("2747. Count Zero Request Servers", [('count_servers(3, [[1, 3], [2, 6], [1, 5]], 5, [10, 11])', [1, 2]), ('count_servers(3, [[2, 4], [2, 1], [1, 2], [3, 1]], 2, [3, 4])', [0, 1])]))
    results.append(check("1169. Invalid Transactions", [('invalid_transactions(["alice,20,800,mtv", "alice,50,100,beijing"])', ['alice,20,800,mtv', 'alice,50,100,beijing']), ('invalid_transactions(["alice,20,800,mtv", "alice,50,1200,mtv"])', ['alice,50,1200,mtv'])]))
    results.append(check("609. Find Duplicate File in System", [('sorted(sorted(g) for g in find_duplicate(["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)", "root 4.txt(efgh)"]))', [['root/4.txt', 'root/a/2.txt', 'root/c/d/4.txt'], ['root/a/1.txt', 'root/c/3.txt']])]))
    results.append(check("388. Longest Absolute File Path", [('length_longest_path("dir\\n\\tsubdir1\\n\\tsubdir2\\n\\t\\tfile.ext")', 20), ('length_longest_path("a")', 0)]))
    results.append(check("165. Compare Version Numbers", [('compare_version("1.2", "1.10")', -1), ('compare_version("1.01", "1.001")', 0), ('compare_version("1.0", "1.0.0.0")', 0), ('compare_version("7.5.2.4", "7.5.3")', -1)]))
    if all(results):
        print("Every solution passes its tests.")
