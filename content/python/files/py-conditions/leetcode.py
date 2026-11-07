# 2.1 Making decisions: if, elif, else and match
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


# ================================================================== 1455. Check If a Word Occurs As a Prefix of Any Word in a Sentence (Easy)
# https://leetcode.com/problems/check-if-a-word-occurs-as-a-prefix-of-any-word-in-a-sentence/
# Pattern: Condition inside a loop
# Idea: Split the sentence. Return the 1 based position of the first word that starts with
# searchWord, else -1.

def is_prefix_of_word(sentence, search_word):
    words = sentence.split()
    for i in range(len(words)):
        if words[i].startswith(search_word):
            return i + 1
    return -1


# ================================================================== 2129. Capitalize the Title (Easy)
# https://leetcode.com/problems/capitalize-the-title/
# Pattern: if else on length
# Idea: Words of length 1 or 2 become all lower case. Longer words get a capital first letter and
# the rest lower.

def capitalize_title(title):
    result = []
    for word in title.split():
        if len(word) <= 2:
            result.append(word.lower())
        else:
            result.append(word[0].upper() + word[1:].lower())
    return " ".join(result)


# ================================================================== 1672. Richest Customer Wealth (Easy)
# https://leetcode.com/problems/richest-customer-wealth/
# Pattern: Keep the biggest with if
# Idea: Add up each row. Keep the biggest sum seen so far with an if.

def maximum_wealth(accounts):
    best = 0
    for customer in accounts:
        total = 0
        for money in customer:
            total = total + money
        if total > best:
            best = total
    return best


# ================================================================== 2678. Number of Senior Citizens (Easy)
# https://leetcode.com/problems/number-of-senior-citizens/
# Pattern: Condition on a slice
# Idea: Characters 11 and 12 of each passenger text are the age. Count ages above 60.

def count_seniors(details):
    count = 0
    for d in details:
        age = int(d[11:13])
        if age > 60:
            count = count + 1
    return count


# ================================================================== 1344. Angle Between Hands of a Clock (Medium)
# https://leetcode.com/problems/angle-between-hands-of-a-clock/
# Pattern: Formula and min
# Idea: Minute hand at 6 × minutes degrees, hour hand at 30 × (hour % 12) + 0.5 × minutes. Return
# the smaller of the gap and 360 minus the gap.

def angle_clock(hour, minutes):
    minute_angle = 6 * minutes
    hour_angle = 30 * (hour % 12) + 0.5 * minutes
    gap = abs(hour_angle - minute_angle)
    if gap > 180:
        gap = 360 - gap
    return gap


if __name__ == "__main__":
    results = []
    results.append(check("1455. Check If a Word Occurs As a Prefix of Any Word in a Sentence", [('is_prefix_of_word("i love eating burger", "burg")', 4), ('is_prefix_of_word("i am tired", "you")', -1)]))
    results.append(check("2129. Capitalize the Title", [('capitalize_title("capiTalIze tHe titLe")', 'Capitalize The Title'), ('capitalize_title("i lOve leetcode")', 'i Love Leetcode')]))
    results.append(check("1672. Richest Customer Wealth", [('maximum_wealth([[1, 2, 3], [3, 2, 1]])', 6), ('maximum_wealth([[1, 5], [7, 3], [3, 5]])', 10)]))
    results.append(check("2678. Number of Senior Citizens", [('count_seniors(["7868190130M7522", "5303914400F9211", "9273338290F4010"])', 2), ('count_seniors(["1313579440F2036", "2921522980M5644"])', 0)]))
    results.append(check("1344. Angle Between Hands of a Clock", [('angle_clock(12, 30)', 165.0), ('angle_clock(3, 30)', 75.0), ('angle_clock(3, 15)', 7.5)]))
    if all(results):
        print("Every solution passes its tests.")
