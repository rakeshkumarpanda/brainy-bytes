# 1.1 Network attacks and defences: spoofing, floods, scans and poisoning
# Example "syn_cookies" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# SYN floods and SYN cookies (Bernstein, 1996), with toy numbers
import hashlib
import hmac

# 1. Why a SYN flood fills the queue: half open connections = attack rate x timeout
backlog = 1024                           # slots for half open connections
timeout = 30                             # seconds a server waits for the final ACK
for rate in (10, 30, 50, 100):           # forged SYN packets per second
    half_open = rate * timeout
    state = "FULL: new users refused" if half_open >= backlog else "ok"
    print(f"{rate:4} SYN/s -> {half_open:5} half open of {backlog}  {state}")

# 2. SYN cookies: keep no state, hide it in the server's sequence number instead
SECRET = b"server secret, rotated often"
MSS_TABLE = [536, 1300, 1440, 1460]      # the server can encode one of 4 MSS values in 2 bits

def cookie(src, dst, sport, dport, t, mss_index):
    msg = f"{src},{dst},{sport},{dport},{t}".encode()
    mac = int.from_bytes(hmac.new(SECRET, msg, hashlib.sha256).digest()[:3], "big")   # 24 bits
    return ((t % 32) << 27) | (mss_index << 24) | mac       # 5 + 3 + 24 = 32 bits (we use 2 of the 3)

def check(src, dst, sport, dport, now, ack):
    isn = (ack - 1) % 2 ** 32            # the client acknowledges our sequence number + 1
    t_low, mss_index = isn >> 27, (isn >> 24) & 7
    for t in (now, now - 1):             # accept cookies from this or the previous minute
        if t % 32 == t_low and mss_index < len(MSS_TABLE) and cookie(src, dst, sport, dport, t, mss_index) == isn:
            return MSS_TABLE[mss_index]
    return None

minute = 29_000_000                      # minutes since 1970, a toy clock
isn = cookie("198.51.100.4", "203.0.113.10", 51000, 443, minute, 3)
print("cookie sent as sequence number:", isn)
print("real client ACK accepted, MSS =", check("198.51.100.4", "203.0.113.10", 51000, 443, minute, isn + 1))
print("forged ACK from a guess:       ", check("198.51.100.4", "203.0.113.10", 51000, 443, minute, 123456789))
print("same ACK three minutes later:  ", check("198.51.100.4", "203.0.113.10", 51000, 443, minute + 3, isn + 1))
