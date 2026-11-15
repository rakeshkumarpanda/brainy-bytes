# 2.1 Memory safety: overflows, ASLR, use after free and Rust
# Example "stack_overflow" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A stack buffer overflow, modelled with a bytearray: what C's strcpy does when the input is too long.
# Layout of one stack frame (simplified, low to high addresses): buf[16] | canary[8] | saved return address[8]
import struct

def make_frame(canary):
    frame = bytearray(32)
    frame[16:24] = struct.pack("<Q", canary)
    frame[24:32] = struct.pack("<Q", 0x401136)            # where the function should return to
    return frame

def strcpy_unchecked(frame, data):
    frame[0:len(data)] = data                              # copies every byte, however many there are

def strcpy_checked(frame, data):
    if len(data) > 16:
        raise ValueError("input longer than the 16 byte buffer")
    frame[0:len(data)] = data

def function_return(frame, canary, check_canary):
    if check_canary and struct.unpack("<Q", frame[16:24])[0] != canary:
        return "*** stack smashing detected ***: program aborted"
    ret = struct.unpack("<Q", frame[24:32])[0]
    return f"returns to 0x{ret:x}" + ("  <- attacker chose this address" if ret != 0x401136 else "")

CANARY = 0x8a1f3c5e7b2d9400                                  # random per run, low byte 0 to stop string copies
good = b"alice"
evil = b"A" * 16 + b"B" * 8 + struct.pack("<Q", 0xdeadbeef)  # fill buf, smash canary, set return address

for label, data in [("normal input", good), ("long input", evil)]:
    for check in (False, True):
        f = make_frame(CANARY)
        strcpy_unchecked(f, data)
        print(f"{label:12} canary check {'on ' if check else 'off'}: {function_return(f, CANARY, check)}")
f = make_frame(CANARY)
try:
    strcpy_checked(f, evil)
except ValueError as e:
    print("bounds checked copy:        refused,", e)
