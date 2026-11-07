# 1.2 Sockets, TCP and UDP: under HTTP
# Example "stream_framing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import struct


def frame(text):
    data = text.encode("utf-8")
    return struct.pack("!I", len(data)) + data      # 4 bytes of length, then the message


stream = frame("hi") + frame("how are you?") + frame("bye")
print(len(stream), "bytes on the wire")

# TCP may cut the stream anywhere. Here it arrives in pieces of 5 bytes.
pieces = [stream[i:i + 5] for i in range(0, len(stream), 5)]
print(len(pieces), "pieces, the first is", pieces[0])

buffer = b""
for piece in pieces:
    buffer += piece
    while len(buffer) >= 4:
        size = struct.unpack("!I", buffer[:4])[0]
        if len(buffer) < 4 + size:
            break                                    # not complete yet, wait for more bytes
        message = buffer[4:4 + size].decode("utf-8")
        buffer = buffer[4 + size:]
        print("message:", message)
print("bytes left over:", len(buffer))
