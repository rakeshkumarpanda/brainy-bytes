# 1.2 Sockets, TCP and UDP: under HTTP
# Example "bytes_text" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import struct

text = "héllo"
data = text.encode("utf-8")          # sockets send bytes, not str
print(data, len(text), "letters,", len(data), "bytes")
print(data.decode("utf-8"))

number = 258
print(number.to_bytes(4, "big"), number.to_bytes(4, "little"))
print(int.from_bytes(b"\x00\x00\x01\x02", "big"))

packed = struct.pack("!HI", 8080, 1_000_000)     # ! = network order (big endian), H = 2 bytes, I = 4 bytes
print(packed.hex(" "), "is", len(packed), "bytes")
print(struct.unpack("!HI", packed))
print(struct.calcsize("!HI"), struct.calcsize("HI"))    # without ! the computer may add padding bytes
