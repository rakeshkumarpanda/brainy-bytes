# 4.1 Social engineering and phishing: tricks, email authentication and defences
# Example "lookalike" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Lookalike domains: swap confusable characters, then measure edit distance to known brands
CONFUSABLE = {"0": "o", "1": "l", "3": "e", "5": "s", "а": "a", "е": "e", "о": "o", "р": "p", "с": "c"}
BRANDS = ["google", "paypal", "amazon", "apple", "sbi", "hdfcbank", "icicibank", "flipkart", "paytm"]

def normalise(name):
    name = name.replace("rn", "m").replace("vv", "w")
    return "".join(CONFUSABLE.get(ch, ch) for ch in name)

def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def check(domain):
    name = domain.split(".")[0]
    norm = normalise(name)
    best = min(BRANDS, key=lambda b: edit_distance(norm, b))
    d = edit_distance(norm, best)
    if name == best:
        verdict = "genuine name"
    elif d <= 1:
        verdict = f"LOOKALIKE of {best}"
    elif d == 2:
        verdict = f"suspicious, close to {best}"
    else:
        verdict = "not near a known brand"
    return name, norm, best, d, verdict

for dom in ["paypa1.com", "arnazon.in", "hdfcbank.com", "flipkrt.com", "gooogle.com", "sunrise-tea.in", "аpple.com"]:
    name, norm, best, d, verdict = check(dom)
    print(f"{dom:15s} reads as {norm:10s} nearest {best:9s} distance {d}  -> {verdict}")
