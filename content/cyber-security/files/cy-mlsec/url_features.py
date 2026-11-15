# 1.1 Machine learning for security
# Example "url_features" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Phishing URL detector: hand made features plus logistic regression trained by gradient descent
import math

def entropy(s):
    """Shannon entropy in bits per character: random looking strings score high."""
    n = len(s)
    return -sum(s.count(ch) / n * math.log2(s.count(ch) / n) for ch in set(s))

def features(url):
    host = url.split("//")[-1].split("/")[0]
    return [
        len(url) / 50,                                # long URLs hide the real domain
        host.count(".") / 3,                          # many subdomains: paypal.com.secure-login.xyz
        1.0 if "@" in url or "-" in host else 0.0,    # tricks that confuse readers
        0.0 if url.startswith("https") else 1.0,      # no TLS
        sum(ch.isdigit() for ch in host) / 5,         # digits in the host name
        entropy(host) / 4,                            # random looking host
    ]

data = [
    ("https://www.google.com", 0), ("https://github.com/login", 0), ("https://mail.yahoo.com", 0),
    ("https://www.irctc.co.in", 0), ("https://en.wikipedia.org/wiki/Cat", 0), ("https://www.sbi.co.in", 0),
    ("http://paypal.com.secure-login.xq7z.top/verify", 1), ("http://192.168.10.5/bank/login", 1),
    ("http://sbi-kyc-update.in-pay.net/form", 1), ("http://amaz0n-prize.win@evil.io/claim", 1),
    ("http://login.micr0soft.verify-acc.ru", 1), ("http://x9k2q7.top/apple-id", 1),
]

w, b, lr = [0.0] * 6, 0.0, 0.5
for epoch in range(300):
    for url, y in data:
        x = features(url)
        z = sum(wi * xi for wi, xi in zip(w, x)) + b
        p = 1 / (1 + math.exp(-z))
        for i in range(6):
            w[i] -= lr * (p - y) * x[i]                # gradient of the log loss
        b -= lr * (p - y)

names = ["length", "dots", "@ or -", "no https", "digits", "entropy"]
print("learned weights:", ", ".join(f"{n} {wi:+.2f}" for n, wi in zip(names, w)))
for url in ["https://www.amazon.in/orders", "https://paypa1.com-secure-verify.xyz/login",
            "http://hdfc-netbanking.secure-update.co/login", "http://45.33.12.9/paytm"]:
    z = sum(wi * xi for wi, xi in zip(w, features(url))) + b
    print(f"{url:48} P(phish) = {1 / (1 + math.exp(-z)):.3f}")
print("\nThe https phishing URL slips through: every phish in training used http, so the model leaned on 'no https'.")
