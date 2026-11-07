# 2.2 Real API work: pages, retries, limits and validation
# Example "token_bucket" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class TokenBucket:
    """Allows `rate` requests per second on average, with bursts of up to `capacity`."""

    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity          # start full
        self.last = 0.0

    def allow(self, now):
        passed = now - self.last
        self.tokens = min(self.capacity, self.tokens + passed * self.rate)    # refill
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


bucket = TokenBucket(rate=2, capacity=3)      # 2 requests a second, bursts of 3
for t in [0.0, 0.1, 0.2, 0.3, 0.4, 1.0, 1.1, 1.2, 3.0, 3.0, 3.0, 3.0]:
    answer = "200 allowed" if bucket.allow(t) else "429 Too Many Requests"
    print(f"t = {t:.1f} s  {answer:22}  tokens left {bucket.tokens:.1f}")


def wait_needed(tokens, rate):
    """How long a client should wait before the next token is ready."""
    return 0.0 if tokens >= 1 else (1 - tokens) / rate


print("wait for the next token:", wait_needed(bucket.tokens, bucket.rate), "s")
