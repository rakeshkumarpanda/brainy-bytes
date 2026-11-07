# 3.2 Lists: storing, changing, sorting and copying
# Example "remove" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

nums = [10, 20, 30, 20, 40]
nums.remove(20)          # removes the first 20 only
print(nums)
last = nums.pop()        # removes and returns the last item
print(last, nums)
first = nums.pop(0)      # removes and returns the item at index 0
print(first, nums)
del nums[0]              # del removes by index and returns nothing
print(nums)
nums.clear()
print(nums)
try:
    nums.remove(99)
except ValueError as err:
    print("ValueError:", err)
