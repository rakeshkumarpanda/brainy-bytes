# 1.1 Machine learning for security
# Example "spam_bayes" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Naive Bayes phishing filter, the idea behind Paul Graham's "A Plan for Spam" (2002)
import math

train = [
    ("verify your account password now", "phish"),
    ("urgent your account is suspended click here", "phish"),
    ("click here to claim your prize now", "phish"),
    ("update payment details urgent", "phish"),
    ("meeting moved to friday afternoon", "ham"),
    ("lunch tomorrow with the team", "ham"),
    ("here are the notes from the meeting", "ham"),
    ("your payment receipt for the course", "ham"),
]

counts = {"phish": {}, "ham": {}}
docs = {"phish": 0, "ham": 0}
for text, label in train:
    docs[label] += 1
    for w in text.split():
        counts[label][w] = counts[label].get(w, 0) + 1
vocab = set(counts["phish"]) | set(counts["ham"])
total = {c: sum(counts[c].values()) for c in counts}

def word_prob(w, c):
    # Laplace smoothing: add 1 so an unseen word never gives probability 0
    return (counts[c].get(w, 0) + 1) / (total[c] + len(vocab))

def log_odds(text):
    score = math.log(docs["phish"] / docs["ham"])
    for w in text.split():
        if w in vocab:
            score += math.log(word_prob(w, "phish") / word_prob(w, "ham"))
    return score

for msg in ["urgent verify your password", "notes from friday meeting", "your course payment receipt"]:
    s = log_odds(msg)
    p = 1 / (1 + math.exp(-s))
    print(f"{msg:30} log odds {s:6.2f}  P(phish) = {p:.3f}  {'PHISH' if p > 0.5 else 'ok'}")
print("\nvocabulary size:", len(vocab), " words in phish:", total["phish"], " words in ham:", total["ham"])
