# 2.1 Iterators and generators
# Example "protocol" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

nums = [10, 20, 30]
it = iter(nums)                                # ask the list for an iterator
print(type(it).__name__)
print(next(it), next(it), next(it))
try:
    next(it)                                   # nothing is left
except StopIteration:
    print("StopIteration: the iterator is used up")

# what a for loop really does with "hi"
it = iter("hi")
while True:
    try:
        ch = next(it)
    except StopIteration:
        break
    print("got", ch)

print(iter(nums) is iter(nums), iter(it) is it)
print(next(iter([]), "empty"))                 # a default instead of StopIteration
