# 3.2 Lists: storing, changing, sorting and copying
# Example "sort" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

nums = [5, 2, 9, 1, 7]
nums.sort()                      # changes the list, returns None
print(nums)
nums.sort(reverse=True)
print(nums)

words = ["banana", "Apple", "cherry", "fig"]
print(sorted(words))                    # new list, upper case first
print(sorted(words, key=str.lower))     # ignore case
print(sorted(words, key=len))           # shortest first, ties keep their order
print(words)                            # sorted() did not change words

result = nums.sort()
print(result)                           # a common mistake: sort() gives None
nums.reverse()
print(nums)
