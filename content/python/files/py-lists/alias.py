# 3.2 Lists: storing, changing, sorting and copying
# Example "alias" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

a = [1, 2, 3]
b = a            # b is another name for the same list
b.append(4)
print(a, b, a is b)

c = a[:]         # a copy (also a.copy() or list(a))
c.append(5)
print(a, c, a is c, a == c)

def add_item(items):
    items.append("new")      # changes the caller's list

shop = ["milk"]
add_item(shop)
print(shop)
