# 3.3 Tuples and sets: fixed records and unique items
# Example "set" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

langs = {"python", "java", "python", "go"}
print(langs, len(langs))        # the repeat is gone, order is not fixed

empty = set()                   # {} would make an empty dict
print(type(empty), type({}))

nums = set([3, 1, 3, 2, 1])
print(nums)
print(set("banana"))

langs.add("rust")
langs.discard("cobol")          # no error if missing
langs.remove("java")            # KeyError if missing
print(sorted(langs))
print("go" in langs)
