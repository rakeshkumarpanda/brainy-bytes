# 2.1 Memory safety: overflows, ASLR, use after free and Rust
# Example "use_after_free" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Use after free on a toy heap: a freed block is reused, and an old pointer now sees someone else's data
class Heap:
    def __init__(self, blocks):
        self.mem = [None] * blocks
        self.free_list = list(range(blocks))
        self.gen = [0] * blocks                   # generation counter for the safe handle version

    def malloc(self, value):
        addr = self.free_list.pop()               # the most recently freed block is reused first (LIFO)
        self.mem[addr] = value
        return addr

    def free(self, addr):
        self.mem[addr] = None
        self.gen[addr] += 1
        self.free_list.append(addr)

heap = Heap(4)
session = heap.malloc({"user": "alice", "is_admin": False})
heap.free(session)                                # alice logs out, but the code keeps the pointer "session"
attacker = heap.malloc({"user": "mallory", "is_admin": True})
print("same block reused:", session == attacker)
print("old pointer now reads:", heap.mem[session], " <- dangling pointer sees mallory's object")

# Fix idea 1: set pointers to None after free. Fix idea 2: handles that remember the generation.
def deref(heap, handle):
    addr, gen = handle
    if heap.gen[addr] != gen:
        raise RuntimeError("use after free detected: block was freed and reused")
    return heap.mem[addr]

addr = heap.malloc({"user": "bob"})
h = (addr, heap.gen[addr])                        # a handle is the address plus its generation
heap.free(addr)
heap.malloc({"user": "eve"})
try:
    deref(heap, h)
except RuntimeError as e:
    print("generation check:", e)
print("Rust prevents this at compile time: a value cannot be used after it has been moved or dropped.")
