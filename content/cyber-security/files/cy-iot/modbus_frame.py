# 4.3 IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet
# Example "modbus_frame" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Reading a Modbus TCP frame byte by byte (a parser, as monitoring tools use, on a made up frame)
import struct

FUNCTIONS = {1: "read coils", 3: "read holding registers", 5: "write single coil",
             6: "write single register", 15: "write multiple coils", 16: "write multiple registers"}

def parse(frame):
    tid, proto, length, unit, func = struct.unpack(">HHHBB", frame[:8])
    body = frame[8:]
    out = {"transaction": tid, "protocol": proto, "length": length, "unit": unit,
           "function": f"{func:02d} {FUNCTIONS.get(func, 'unknown')}"}
    if func in (5, 6):
        addr, value = struct.unpack(">HH", body[:4])
        out["address"] = hex(addr)
        out["value"] = hex(value)
    return out

frame = bytes.fromhex("002A 0000 0006 01 05 0010 FF00".replace(" ", ""))
for k, v in parse(frame).items():
    print(f"{k:12s} {v}")

print("\nNo field holds a user name, password or signature. Any device that can reach port 502")
print("can send this. That is why plants allow writes only from known operator stations.")
