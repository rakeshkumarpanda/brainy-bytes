# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "text_bytes" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Text and bytes: what a security tool really reads
import base64

word = "café"
data = word.encode("utf-8")            # text (str) to bytes
print("text      :", word, "has", len(word), "characters")
print("bytes     :", data, "has", len(data), "bytes")
print("hex       :", data.hex())
print("numbers   :", list(data))      # every byte is a number from 0 to 255

bits = ""
for b in data:
    bits = bits + format(b, "08b") + " "
print("bits      :", bits)

encoded = base64.b64encode(data)
print("base64    :", encoded.decode("ascii"))
print("back again:", base64.b64decode(encoded).decode("utf-8"))

# bytes.fromhex reads a hex dump back into bytes
packet = bytes.fromhex("48 54 54 50")
print("from hex  :", packet, "is the text", packet.decode("ascii"))
