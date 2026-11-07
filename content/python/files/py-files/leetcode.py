# 5.3 Files: reading, writing, modes, paths and streams
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


# ================================================================== 1816. Truncate Sentence (Easy)
# https://leetcode.com/problems/truncate-sentence/
# Pattern: split and join
# Idea: Split on spaces, keep the first k words, join them again.

def truncate_sentence(s, k):
    return " ".join(s.split()[:k])


# ================================================================== 819. Most Common Word (Easy)
# https://leetcode.com/problems/most-common-word/
# Pattern: Clean text, count words
# Idea: Turn every non letter into a space, lower case everything, count the words that are not
# banned and take the most common.

def most_common_word(paragraph, banned):
    clean = ""
    for ch in paragraph:
        if ch.isalpha():
            clean = clean + ch.lower()
        else:
            clean = clean + " "
    banned_set = set(banned)
    counts = {}
    for word in clean.split():
        if word not in banned_set:
            counts[word] = counts.get(word, 0) + 1
    return max(counts, key=counts.get)


# ================================================================== 884. Uncommon Words from Two Sentences (Easy)
# https://leetcode.com/problems/uncommon-words-from-two-sentences/
# Pattern: Count words of both texts
# Idea: A word is uncommon if it appears exactly once in the two sentences together.

def uncommon_from_sentences(s1, s2):
    counts = {}
    for word in (s1 + " " + s2).split():
        counts[word] = counts.get(word, 0) + 1
    return [w for w in counts if counts[w] == 1]


# ================================================================== 1592. Rearrange Spaces Between Words (Easy)
# https://leetcode.com/problems/rearrange-spaces-between-words/
# Pattern: Count spaces, divide
# Idea: Count the spaces and words. Put spaces // (words − 1) between words and the rest at the end.

def reorder_spaces(text):
    spaces = text.count(" ")
    words = text.split()
    if len(words) == 1:
        return words[0] + " " * spaces
    gap = spaces // (len(words) - 1)
    extra = spaces % (len(words) - 1)
    return (" " * gap).join(words) + " " * extra


# ================================================================== 2042. Check if Numbers Are Ascending in a Sentence (Easy)
# https://leetcode.com/problems/check-if-numbers-are-ascending-in-a-sentence/
# Pattern: Parse tokens
# Idea: Split into tokens. Every token made of digits must be bigger than the previous number.

def are_numbers_ascending(s):
    last = -1
    for token in s.split():
        if token.isdigit():
            if int(token) <= last:
                return False
            last = int(token)
    return True


# ================================================================== 609. Find Duplicate File in System (Medium)
# https://leetcode.com/problems/find-duplicate-file-in-system/
# Pattern: Group paths by content
# Idea: Each entry is "folder name(content) ...". Group full paths by content in a dict and keep
# groups with more than one path.

def find_duplicate(paths):
    groups = {}
    for entry in paths:
        parts = entry.split()
        folder = parts[0]
        for item in parts[1:]:
            name, rest = item.split("(")
            content = rest[:-1]
            if content not in groups:
                groups[content] = []
            groups[content].append(folder + "/" + name)
    return [g for g in groups.values() if len(g) > 1]


# ================================================================== 388. Longest Absolute File Path (Medium)
# https://leetcode.com/problems/longest-absolute-file-path/
# Pattern: Depth by tabs, a stack of lengths
# Idea: Split into lines. The number of tabs is the depth. Keep the path length at each depth. A
# name with a dot is a file.

def length_longest_path(text):
    best = 0
    length_at = {0: 0}
    for line in text.split("\n"):
        name = line.lstrip("\t")
        depth = len(line) - len(name)
        if "." in name:
            best = max(best, length_at[depth] + len(name))
        else:
            length_at[depth + 1] = length_at[depth] + len(name) + 1
    return best


# ================================================================== 1233. Remove Sub-Folders from the Filesystem (Medium)
# https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/
# Pattern: Sort, then compare with the last kept folder
# Idea: After sorting, a sub folder comes right after its parent. Keep a folder unless it starts
# with the last kept folder plus "/".

def remove_subfolders(folder):
    result = []
    for f in sorted(folder):
        if not result or not f.startswith(result[-1] + "/"):
            result.append(f)
    return result


# ================================================================== 1047. Remove All Adjacent Duplicates In String (Easy)
# https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string/
# Pattern: Stack
# Idea: Push each character. If it equals the top of the stack, pop instead.

def remove_duplicates_text(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


# ================================================================== 68. Text Justification (Hard)
# https://leetcode.com/problems/text-justification/
# Pattern: Greedy lines, spread spaces
# Idea: Fill each line with as many words as fit. Spread the spaces, giving the left gaps one extra
# when they do not divide evenly. The last line is left aligned.

def full_justify(words, max_width):
    lines = []
    i = 0
    while i < len(words):
        j = i
        width = 0
        while j < len(words) and width + len(words[j]) + (j - i) <= max_width:
            width = width + len(words[j])
            j = j + 1
        gaps = j - i - 1
        if j == len(words) or gaps == 0:
            line = " ".join(words[i:j])
            line = line + " " * (max_width - len(line))
        else:
            spaces = max_width - width
            line = ""
            for k in range(i, j - 1):
                extra = 1 if (k - i) < spaces % gaps else 0
                line = line + words[k] + " " * (spaces // gaps + extra)
            line = line + words[j - 1]
        lines.append(line)
        i = j
    return lines


if __name__ == "__main__":
    results = []
    results.append(check("1816. Truncate Sentence", [('truncate_sentence("Hello how are you Contestant", 4)', 'Hello how are you'), ('truncate_sentence("chopper is not a tanuki", 5)', 'chopper is not a tanuki')]))
    results.append(check("819. Most Common Word", [('most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", ["hit"])', 'ball'), ('most_common_word("a.", [])', 'a')]))
    results.append(check("884. Uncommon Words from Two Sentences", [('sorted(uncommon_from_sentences("this apple is sweet", "this apple is sour"))', ['sour', 'sweet']), ('uncommon_from_sentences("apple apple", "banana")', ['banana'])]))
    results.append(check("1592. Rearrange Spaces Between Words", [('reorder_spaces("  this   is  a sentence ")', 'this   is   a   sentence'), ('reorder_spaces(" practice   makes   perfect")', 'practice   makes   perfect '), ('reorder_spaces("  hello")', 'hello  ')]))
    results.append(check("2042. Check if Numbers Are Ascending in a Sentence", [('are_numbers_ascending("1 box has 3 blue 4 red 6 green and 12 yellow marbles")', True), ('are_numbers_ascending("hello world 5 x 5")', False)]))
    results.append(check("609. Find Duplicate File in System", [('sorted(sorted(g) for g in find_duplicate(["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)", "root 4.txt(efgh)"]))', [['root/4.txt', 'root/a/2.txt', 'root/c/d/4.txt'], ['root/a/1.txt', 'root/c/3.txt']])]))
    results.append(check("388. Longest Absolute File Path", [('length_longest_path("dir\\n\\tsubdir1\\n\\tsubdir2\\n\\t\\tfile.ext")', 20), ('length_longest_path("a")', 0), ('length_longest_path("file1.txt\\nfile2.txt\\nlongfile.txt")', 12)]))
    results.append(check("1233. Remove Sub-Folders from the Filesystem", [('remove_subfolders(["/a", "/a/b", "/c/d", "/c/d/e", "/c/f"])', ['/a', '/c/d', '/c/f']), ('remove_subfolders(["/a/b/c", "/a/b/ca", "/a/b/d"])', ['/a/b/c', '/a/b/ca', '/a/b/d'])]))
    results.append(check("1047. Remove All Adjacent Duplicates In String", [('remove_duplicates_text("abbaca")', 'ca'), ('remove_duplicates_text("azxxzy")', 'ay')]))
    results.append(check("68. Text Justification", [('full_justify(["This", "is", "an", "example", "of", "text", "justification."], 16)', ['This    is    an', 'example  of text', 'justification.  ']), ('full_justify(["What", "must", "be", "acknowledgment", "shall", "be"], 16)', ['What   must   be', 'acknowledgment  ', 'shall be        '])]))
    if all(results):
        print("Every solution passes its tests.")
