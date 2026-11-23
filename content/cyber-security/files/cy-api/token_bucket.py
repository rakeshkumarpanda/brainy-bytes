# 4.4 API security: BOLA, rate limits, mass assignment and the OWASP API Top 10
# Example "token_bucket" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Token bucket rate limiting, the same numbers as the animation: a bot sends 10 login tries a second from 10 IPs
class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity, self.rate, self.tokens = capacity, refill_per_sec, float(capacity)

    def refill(self, seconds):
        self.tokens = min(self.capacity, self.tokens + self.rate * seconds)

    def allow(self):
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False          # the API answers 429 Too Many Requests

def attack(mode, target=40, seconds=12, ips=10):
    if mode == "per IP":
        buckets = [TokenBucket(2, 0.5) for _ in range(ips)]
    elif mode == "per account":
        buckets = [TokenBucket(5, 0.2)]
    else:
        buckets = None
    tested = refused = 0
    for t in range(1, seconds + 1):
        if buckets and t > 1:
            for b in buckets:
                b.refill(1)
        for ip in range(ips):
            b = None if buckets is None else buckets[ip if mode == "per IP" else 0]
            if b is None or b.allow():
                tested += 1
                if tested == target:
                    return f"{mode:12s} broken in at second {t}, {refused} tries refused"
            else:
                refused += 1
    return f"{mode:12s} still out after {seconds} s: {tested} tested, {refused} refused"

for mode in ("no limit", "per IP", "per account"):
    print(attack(mode))
