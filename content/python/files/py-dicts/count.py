# 3.4 Dictionaries: keys, values and hash tables
# Example "count" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

text = "the cat and the hat and the bat"

counts = {}                     # 1. with if
for word in text.split():
    if word in counts:
        counts[word] += 1
    else:
        counts[word] = 1
print(counts)

counts = {}                     # 2. with get
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)

from collections import Counter # 3. with Counter
c = Counter(text.split())
print(c.most_common(2))
print(Counter("banana"))
