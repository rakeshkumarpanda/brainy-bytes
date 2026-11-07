# 3.1 Clean code: PEP 8, docstrings and type hints
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


# ================================================================== 520. Detect Capital (Easy)
# https://leetcode.com/problems/detect-capital/
# Pattern: Three allowed shapes
# Idea: Like a naming rule: all capitals, all small, or only the first letter capital.

def detect_capital_use(word: str) -> bool:
    """Return True if word is all caps, all lower case, or Capitalised."""
    return word.isupper() or word.islower() or word.istitle()


# ================================================================== 482. License Key Formatting (Easy)
# https://leetcode.com/problems/license-key-formatting/
# Pattern: Clean, then group from the right
# Idea: Remove dashes, make it upper case, then cut groups of k from the end so only the first group
# may be shorter.

def license_key_formatting(s: str, k: int) -> str:
    """Return the key in upper case groups of k, joined by dashes."""
    clean = s.replace("-", "").upper()
    first = len(clean) % k or k
    groups = [clean[:first]]
    for start in range(first, len(clean), k):
        groups.append(clean[start:start + k])
    return "-".join(group for group in groups if group)


# ================================================================== 68. Text Justification (Hard)
# https://leetcode.com/problems/text-justification/
# Pattern: Fill each line, then share out the spaces
# Idea: Take as many words as fit. Spread the extra spaces from the left. The last line and one word
# lines are left justified.

def full_justify(words: list[str], max_width: int) -> list[str]:
    """Return the lines of words justified to max_width characters."""
    lines = []
    start = 0
    while start < len(words):
        end = start
        width = 0
        while end < len(words) and width + len(words[end]) + (end - start) <= max_width:
            width += len(words[end])
            end += 1
        gaps = end - start - 1
        if end == len(words) or gaps == 0:
            line = " ".join(words[start:end])
            lines.append(line + " " * (max_width - len(line)))
        else:
            spaces = max_width - width
            line = ""
            for i in range(start, end - 1):
                extra = 1 if i - start < spaces % gaps else 0
                line += words[i] + " " * (spaces // gaps + extra)
            lines.append(line + words[end - 1])
        start = end
    return lines


# ================================================================== 824. Goat Latin (Easy)
# https://leetcode.com/problems/goat-latin/
# Pattern: Follow the rules word by word
# Idea: Vowel start: add "ma". Otherwise move the first letter to the end and add "ma". Then add one
# "a" per word position.

def to_goat_latin(sentence: str) -> str:
    """Return sentence translated into Goat Latin."""
    result = []
    for position, word in enumerate(sentence.split(), start=1):
        if word[0].lower() in "aeiou":
            goat = word + "ma"
        else:
            goat = word[1:] + word[0] + "ma"
        result.append(goat + "a" * position)
    return " ".join(result)


# ================================================================== 1859. Sorting the Sentence (Easy)
# https://leetcode.com/problems/sorting-the-sentence/
# Pattern: Sort by the last character
# Idea: Each word ends with its position. Sort by that digit and remove it.

def sort_sentence(s: str) -> str:
    """Return the sentence with words put back in order."""
    words = sorted(s.split(), key=lambda word: word[-1])
    return " ".join(word[:-1] for word in words)


# ================================================================== 2047. Number of Valid Words in a Sentence (Easy)
# https://leetcode.com/problems/number-of-valid-words-in-a-sentence/
# Pattern: Check each rule, like a linter
# Idea: No digits, at most one hyphen with letters on both sides, at most one punctuation mark and
# only at the end.

def is_valid_token(token: str) -> bool:
    """Return True if token follows every rule of the problem."""
    if any(ch.isdigit() for ch in token):
        return False
    if token.count("-") > 1:
        return False
    if "-" in token:
        i = token.index("-")
        if i == 0 or i == len(token) - 1 or not token[i - 1].isalpha() or not token[i + 1].isalpha():
            return False
    marks = [i for i, ch in enumerate(token) if ch in "!.,"]
    return not marks or (len(marks) == 1 and marks[0] == len(token) - 1)


def count_valid_words(sentence: str) -> int:
    """Return how many tokens of sentence are valid words."""
    return sum(1 for token in sentence.split() if is_valid_token(token))


# ================================================================== 929. Unique Email Addresses (Easy)
# https://leetcode.com/problems/unique-email-addresses/
# Pattern: Normalise, then count with a set
# Idea: In the local part drop everything after "+" and remove dots. Keep the domain as it is.

def num_unique_emails(emails: list[str]) -> int:
    """Return how many different addresses actually receive mail."""
    seen = set()
    for email in emails:
        local, domain = email.split("@")
        local = local.split("+")[0].replace(".", "")
        seen.add(local + "@" + domain)
    return len(seen)


# ================================================================== 1556. Thousand Separator (Easy)
# https://leetcode.com/problems/thousand-separator/
# Pattern: Format with a separator
# Idea: Python can group digits with format(n, ","). LeetCode wants dots, so swap the commas.

def thousand_separator(n: int) -> str:
    """Return n with a dot between every group of three digits."""
    return format(n, ",").replace(",", ".")


# ================================================================== 1694. Reformat Phone Number (Easy)
# https://leetcode.com/problems/reformat-phone-number/
# Pattern: Blocks of 3, end with 2 and 2 if 4 are left
# Idea: Keep only digits. Take blocks of 3 while more than 4 remain. Then 4 digits become 2 and 2,
# otherwise one last block.

def reformat_number(number: str) -> str:
    """Return the digits of number in blocks of three, never ending with one digit."""
    digits = "".join(ch for ch in number if ch.isdigit())
    blocks = []
    while len(digits) > 4:
        blocks.append(digits[:3])
        digits = digits[3:]
    if len(digits) == 4:
        blocks += [digits[:2], digits[2:]]
    else:
        blocks.append(digits)
    return "-".join(blocks)


# ================================================================== 2299. Strong Password Checker II (Easy)
# https://leetcode.com/problems/strong-password-checker-ii/
# Pattern: One check per rule
# Idea: At least 8 characters, a lower case letter, an upper case letter, a digit, a special
# character, and no two equal characters side by side.

SPECIAL = "!@#$%^&*()-+"


def strong_password_checker_ii(password: str) -> bool:
    """Return True if password passes every rule."""
    if len(password) < 8:
        return False
    if any(a == b for a, b in zip(password, password[1:])):
        return False
    return (any(ch.islower() for ch in password)
            and any(ch.isupper() for ch in password)
            and any(ch.isdigit() for ch in password)
            and any(ch in SPECIAL for ch in password))


if __name__ == "__main__":
    results = []
    results.append(check("520. Detect Capital", [('detect_capital_use("USA")', True), ('detect_capital_use("FlaG")', False), ('detect_capital_use("leetcode")', True), ('detect_capital_use("Google")', True)]))
    results.append(check("482. License Key Formatting", [('license_key_formatting("5F3Z-2e-9-w", 4)', '5F3Z-2E9W'), ('license_key_formatting("2-5g-3-J", 2)', '2-5G-3J'), ('license_key_formatting("---", 3)', '')]))
    results.append(check("68. Text Justification", [('full_justify(["This", "is", "an", "example", "of", "text", "justification."], 16)', ['This    is    an', 'example  of text', 'justification.  ']), ('full_justify(["What", "must", "be", "acknowledgment", "shall", "be"], 16)', ['What   must   be', 'acknowledgment  ', 'shall be        '])]))
    results.append(check("824. Goat Latin", [('to_goat_latin("I speak Goat Latin")', 'Imaa peaksmaaa oatGmaaaa atinLmaaaaa')]))
    results.append(check("1859. Sorting the Sentence", [('sort_sentence("is2 sentence4 This1 a3")', 'This is a sentence'), ('sort_sentence("Myself2 Me1 I4 and3")', 'Me Myself and I')]))
    results.append(check("2047. Number of Valid Words in a Sentence", [('count_valid_words("cat and  dog")', 3), ('count_valid_words("!this  1-s b8d!")', 0), ('count_valid_words("alice and  bob are playing stone-game10")', 5)]))
    results.append(check("929. Unique Email Addresses", [('num_unique_emails(["test.email+alex@leetcode.com", "test.e.mail+bob.cathy@leetcode.com", "testemail+david@lee.tcode.com"])', 2)]))
    results.append(check("1556. Thousand Separator", [('thousand_separator(987)', '987'), ('thousand_separator(1234)', '1.234'), ('thousand_separator(0)', '0')]))
    results.append(check("1694. Reformat Phone Number", [('reformat_number("1-23-45 6")', '123-456'), ('reformat_number("123 4-567")', '123-45-67'), ('reformat_number("123 4-5678")', '123-456-78')]))
    results.append(check("2299. Strong Password Checker II", [('strong_password_checker_ii("IloveLe3tcode!")', True), ('strong_password_checker_ii("Me+You--IsMyDream")', False), ('strong_password_checker_ii("1aB!")', False)]))
    if all(results):
        print("Every solution passes its tests.")
