# 3.2 Lists: storing, changing, sorting and copying
# Example "growth" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import sys
items = []
last_size = sys.getsizeof(items)
print("empty list:", last_size, "bytes")
for i in range(20):
    items.append(i)
    size = sys.getsizeof(items)
    if size != last_size:
        print("after", len(items), "items the list grew to", size, "bytes")
        last_size = size
