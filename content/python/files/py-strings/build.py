# 3.1 Strings: text, slicing, methods and Unicode
# Example "build" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Building text: join a list instead of adding in a loop
words = []
for i in range(1, 6):
    words.append(str(i * i))
print(", ".join(words))

# Counting letters with a simple loop
text = "banana"
count_a = 0
for ch in text:
    if ch == "a":
        count_a += 1
print(count_a, text.count("a"))

# Caesar cipher: move each letter 3 places
secret = ""
for ch in "attack at dawn":
    if ch.isalpha():
        secret += chr((ord(ch) - ord("a") + 3) % 26 + ord("a"))
    else:
        secret += ch
print(secret)
