# 3.4 Dictionaries: keys, values and hash tables
# Example "make" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

phone = {"Asha": "98450 11111", "Ravi": "99001 22222"}
ages = dict(asha=21, ravi=23)              # keyword style, keys become strings
pairs = dict([("x", 1), ("y", 2)])         # from a list of pairs
empty = {}
print(phone)
print(ages, pairs, empty)
print(phone["Asha"])                       # look up by key
print(len(phone), "Ravi" in phone, "98450 11111" in phone)
