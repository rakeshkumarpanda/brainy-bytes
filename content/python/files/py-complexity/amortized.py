# 4.1 Complexity, timing and profiling
# Example "amortized" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class DynamicArray:
    """A list that doubles its space when it is full, like Python's list does (Python grows by less)."""

    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None]
        self.copies = 0

    def append(self, value):
        if self.size == self.capacity:         # full: get twice the space and copy everything
            self.capacity = self.capacity * 2
            new_slots = [None] * self.capacity
            for i in range(self.size):
                new_slots[i] = self.slots[i]
                self.copies += 1
            self.slots = new_slots
        self.slots[self.size] = value
        self.size += 1


array = DynamicArray()
for n in range(1, 1025):
    array.append(n)
    if n in (1, 2, 4, 8, 64, 1024):
        print(f"{n:>5} items  capacity {array.capacity:>5}  copies {array.copies:>5}  per append {array.copies / n:.2f}")
