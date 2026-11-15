# 2.1 Memory safety: overflows, ASLR, use after free and Rust
# Example "integer_overflow" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Integer overflow: in C a 32 bit unsigned number wraps around, so a size check can be fooled.
# Python integers never overflow, so the wrap is modelled with "& 0xFFFFFFFF".
MASK = 0xFFFFFFFF

def alloc_size_buggy(count, item_size):
    return (count * item_size) & MASK             # what uint32_t size = count * item_size gives in C

def alloc_size_safe(count, item_size):
    if item_size and count > MASK // item_size:   # check before multiplying
        raise OverflowError("count * item_size does not fit in 32 bits")
    return count * item_size

for count in (1000, 0x40000001):
    size = alloc_size_buggy(count, 4)
    print(f"count {count:>11}: buffer of {size:>10} bytes, loop writes {count * 4:>11} bytes"
          + ("  <- heap overflow" if size < count * 4 else ""))
try:
    alloc_size_safe(0x40000001, 4)
except OverflowError as e:
    print("safe version:", e)

# Signed wrap: a length that looks negative passes a "too big?" check
def to_int32(x):
    x &= MASK
    return x - 2 ** 32 if x >= 2 ** 31 else x

length = to_int32(0xFFFFFFF0)                      # attacker sends 4294967280
print("as signed 32 bit:", length, "| check 'length > 1024' passes:", not length > 1024)
print("as unsigned size for memcpy:", length & MASK, "bytes")
