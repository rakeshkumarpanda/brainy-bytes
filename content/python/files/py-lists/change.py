# 3.2 Lists: storing, changing, sorting and copying
# Example "change" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

fruits = ["apple", "mango"]
fruits.append("banana")          # add one item at the end
print(fruits)
fruits.insert(1, "kiwi")         # add at position 1, the rest move right
print(fruits)
fruits.extend(["fig", "plum"])   # add every item of another list
print(fruits)
fruits[0] = "grape"              # replace one item
print(fruits)
fruits[1:3] = ["lime"]           # replace a slice, the list can shrink
print(fruits)
