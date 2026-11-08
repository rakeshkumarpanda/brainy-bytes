# 6.1 API security: passwords, JWT, OAuth 2.0, CORS and OWASP
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


# ================================================================== 2325. Decode the Message (Easy)
# https://leetcode.com/problems/decode-the-message/
# Pattern: Build a substitution table from first appearances
# Idea: This is a simple substitution cipher. The first time each letter appears in the key it
# stands for the next letter of the alphabet. A dict holds the table, and spaces stay as they are.
# Ciphers like this are easy to break, which is why real systems use keys and HMAC instead.

def decode_message(key, message):
    table = {" ": " "}
    for ch in key:
        if ch != " " and ch not in table:
            table[ch] = chr(ord("a") + len(table) - 1)
    return "".join(table[ch] for ch in message)


# ================================================================== 1844. Replace All Digits with Characters (Easy)
# https://leetcode.com/problems/replace-all-digits-with-characters/
# Pattern: Shift a letter by a digit
# Idea: Every digit says how far to move the letter before it, the same idea as a Caesar shift.
# chr(ord(letter) + digit) does the move.

def replace_digits(s):
    out = list(s)
    for i in range(1, len(s), 2):
        out[i] = chr(ord(s[i - 1]) + int(s[i]))
    return "".join(out)


# ================================================================== 1528. Shuffle String (Easy)
# https://leetcode.com/problems/shuffle-string/
# Pattern: Put each character at its target index
# Idea: A transposition: indices[i] says where s[i] belongs. Fill a list of the right length, then
# join it.

def restore_string(s, indices):
    out = [""] * len(s)
    for ch, place in zip(s, indices):
        out[place] = ch
    return "".join(out)


# ================================================================== 1461. Check If a String Contains All Binary Codes of Size K (Medium)
# https://leetcode.com/problems/check-if-a-string-contains-all-binary-codes-of-size-k/
# Pattern: A set of every window of length k
# Idea: There are 2k codes of length k, the same count an attacker must try to guess a k bit token.
# Put every window of the string in a set and compare its size with 2k.

def has_all_codes(s, k):
    seen = {s[i:i + k] for i in range(len(s) - k + 1)}
    return len(seen) == 2 ** k


# ================================================================== 187. Repeated DNA Sequences (Medium)
# https://leetcode.com/problems/repeated-dna-sequences/
# Pattern: Two sets: seen once and seen again
# Idea: Slide a window of 10 letters and remember each one in a set. A window that is already there
# is a repeat, like a replayed request id that a server must refuse. The answer is sorted here so
# the tests can compare it.

def find_repeated_dna_sequences(s):
    seen, repeated = set(), set()
    for i in range(len(s) - 9):
        part = s[i:i + 10]
        if part in seen:
            repeated.add(part)
        seen.add(part)
    return sorted(repeated)


# ================================================================== 1980. Find Unique Binary String (Medium)
# https://leetcode.com/problems/find-unique-binary-string/
# Pattern: Cantor diagonal: differ from string i at place i
# Idea: Take bit i of string i and flip it. The new string differs from every given string in at
# least one place, so it cannot be any of them. The same trick proves that some sets cannot be
# listed.

def find_different_binary_string(nums):
    return "".join("1" if nums[i][i] == "0" else "0" for i in range(len(nums)))


# ================================================================== 721. Accounts Merge (Medium)
# https://leetcode.com/problems/accounts-merge/
# Pattern: Union find over e-mail addresses
# Idea: Two accounts are one person when they share an e-mail, like linking identities in a login
# system. Union find joins every e-mail with the first e-mail of its account, then each group
# becomes one sorted account. The list is sorted at the end so the tests can compare it.

def accounts_merge(accounts):
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner = {}
    for name, *emails in accounts:
        for email in emails:
            parent.setdefault(email, email)
            owner[email] = name
            parent[find(email)] = find(emails[0])
    groups = {}
    for email in parent:
        groups.setdefault(find(email), []).append(email)
    return sorted([owner[root]] + sorted(emails) for root, emails in groups.items())


# ================================================================== 420. Strong Password Checker (Hard)
# https://leetcode.com/problems/strong-password-checker/
# Pattern: Count runs, then spend deletions where they save a replacement
# Idea: A strong password has 6 to 20 characters, a lower case letter, an upper case letter and a
# digit, and never three equal characters in a row. Short passwords only need inserts. Long ones
# need deletes, and a delete in a run whose length is a multiple of 3 saves one replacement, so
# spend deletes on those runs first, then on runs with remainder 1 (two deletes) and then three at a
# time.

def strong_password_checker(password):
    n = len(password)
    missing = 3 - (any(c.islower() for c in password) + any(c.isupper() for c in password)
                   + any(c.isdigit() for c in password))
    if n < 6:
        return max(missing, 6 - n)
    replace = one = two = 0
    i = 2
    while i < n:
        if password[i] == password[i - 1] == password[i - 2]:
            length = 2
            while i < n and password[i] == password[i - 1]:
                length += 1
                i += 1
            replace += length // 3
            if length % 3 == 0:
                one += 1
            elif length % 3 == 1:
                two += 1
        else:
            i += 1
    if n <= 20:
        return max(missing, replace)
    delete = n - 20
    replace -= min(delete, one)
    replace -= min(max(delete - one, 0), two * 2) // 2
    replace -= max(delete - one - 2 * two, 0) // 3
    return delete + max(missing, replace)


# ================================================================== 2156. Find Substring With Given Hash Value (Hard)
# https://leetcode.com/problems/find-substring-with-given-hash-value/
# Pattern: Rolling hash, walking from the right
# Idea: The hash gives the first letter the power p0, so it is easy to add a letter on the LEFT:
# multiply by p and add the new value. Walk from the end of the string, drop the letter that falls
# out of the window, and remember the leftmost window that matches. Rolling hashes also power rsync
# and duplicate file checks.

def sub_str_hash(s, power, modulo, k, hash_value):
    n = len(s)
    top = pow(power, k - 1, modulo)
    h = 0
    best = 0
    for i in range(n - 1, -1, -1):
        h = (h * power + ord(s[i]) - 96) % modulo
        if i + k < n:
            h = (h - (ord(s[i + k]) - 96) * top * power) % modulo
        if i + k <= n and h == hash_value:
            best = i
    return s[best:best + k]


# ================================================================== 1392. Longest Happy Prefix (Hard)
# https://leetcode.com/problems/longest-happy-prefix/
# Pattern: The KMP failure table
# Idea: A happy prefix is also a suffix. The prefix function of KMP stores, for each position, the
# longest proper prefix that ends there, and its last value is the answer. It runs in O(n), with no
# hash collisions to worry about.

def longest_prefix(s):
    fail = [0] * len(s)
    j = 0
    for i in range(1, len(s)):
        while j and s[i] != s[j]:
            j = fail[j - 1]
        if s[i] == s[j]:
            j += 1
        fail[i] = j
    return s[:fail[-1]]


if __name__ == "__main__":
    results = []
    results.append(check("2325. Decode the Message", [('decode_message("the quick brown fox jumps over the lazy dog", "vkbs bs t suepuv")', 'this is a secret'), ('decode_message("eljuxhpwnyrdgtqkviszcfmabo", "zwx hnfx lqantp mnoeius ycgk vcnjrdb")', 'the five boxing wizards jump quickly')]))
    results.append(check("1844. Replace All Digits with Characters", [('replace_digits("a1c1e1")', 'abcdef'), ('replace_digits("a1b2c3d4e")', 'abbdcfdhe')]))
    results.append(check("1528. Shuffle String", [('restore_string("codeleet", [4, 5, 6, 7, 0, 2, 1, 3])', 'leetcode'), ('restore_string("abc", [0, 1, 2])', 'abc')]))
    results.append(check("1461. Check If a String Contains All Binary Codes of Size K", [('has_all_codes("00110110", 2)', True), ('has_all_codes("0110", 1)', True), ('has_all_codes("0110", 2)', False)]))
    results.append(check("187. Repeated DNA Sequences", [('find_repeated_dna_sequences("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT")', ['AAAAACCCCC', 'CCCCCAAAAA']), ('find_repeated_dna_sequences("AAAAAAAAAAAAA")', ['AAAAAAAAAA'])]))
    results.append(check("1980. Find Unique Binary String", [('find_different_binary_string(["01", "10"])', '11'), ('find_different_binary_string(["00", "01"]) not in ["00", "01"]', True), ('find_different_binary_string(["111", "011", "001"])', '000')]))
    results.append(check("721. Accounts Merge", [('accounts_merge([["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"], ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]])', [['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com'], ['John', 'johnnybravo@mail.com'], ['Mary', 'mary@mail.com']]), ('accounts_merge([["Gabe", "Gabe0@m.co", "Gabe3@m.co", "Gabe1@m.co"], ["Kevin", "Kevin3@m.co", "Kevin5@m.co", "Kevin0@m.co"], ["Ethan", "Ethan5@m.co", "Ethan4@m.co", "Ethan0@m.co"], ["Hanzo", "Hanzo3@m.co", "Hanzo1@m.co", "Hanzo0@m.co"], ["Fern", "Fern5@m.co", "Fern1@m.co", "Fern0@m.co"]])', [['Ethan', 'Ethan0@m.co', 'Ethan4@m.co', 'Ethan5@m.co'], ['Fern', 'Fern0@m.co', 'Fern1@m.co', 'Fern5@m.co'], ['Gabe', 'Gabe0@m.co', 'Gabe1@m.co', 'Gabe3@m.co'], ['Hanzo', 'Hanzo0@m.co', 'Hanzo1@m.co', 'Hanzo3@m.co'], ['Kevin', 'Kevin0@m.co', 'Kevin3@m.co', 'Kevin5@m.co']])]))
    results.append(check("420. Strong Password Checker", [('strong_password_checker("a")', 5), ('strong_password_checker("aA1")', 3), ('strong_password_checker("1337C0d3")', 0), ('strong_password_checker("aaa111")', 2), ('strong_password_checker("aaaaaaaaaaaaaaaaaaaaa")', 7), ('strong_password_checker("bbaaaaaaaaaaaaaaacccccc")', 8)]))
    results.append(check("2156. Find Substring With Given Hash Value", [('sub_str_hash("leetcode", 7, 20, 2, 0)', 'ee'), ('sub_str_hash("fbxzaad", 31, 100, 3, 32)', 'fbx')]))
    results.append(check("1392. Longest Happy Prefix", [('longest_prefix("level")', 'l'), ('longest_prefix("ababab")', 'abab'), ('longest_prefix("abc")', '')]))
    if all(results):
        print("Every solution passes its tests.")
