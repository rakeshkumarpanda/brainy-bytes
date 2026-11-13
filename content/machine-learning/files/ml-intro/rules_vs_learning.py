# 1.1 What machine learning is: learning from examples
# Example "rules_vs_learning" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Way 1: a person writes the rule by hand
def spam_by_rule(message):
    words = message.lower().split()
    if "free" in words and "win" in words:
        return "spam"
    return "not spam"

# Way 2: the machine counts words in examples and learns the rule itself
examples = [
    ("win a free phone now", "spam"),
    ("free tickets win big", "spam"),
    ("claim your free prize", "spam"),
    ("lunch at one tomorrow", "not spam"),
    ("see you at the meeting", "not spam"),
    ("your free time this week", "not spam"),
]

spam_count = {}
ham_count = {}
for text, label in examples:
    for word in text.split():
        if label == "spam":
            spam_count[word] = spam_count.get(word, 0) + 1
        else:
            ham_count[word] = ham_count.get(word, 0) + 1

def spam_by_learning(message):
    score = 0
    for word in message.lower().split():
        score = score + spam_count.get(word, 0) - ham_count.get(word, 0)
    if score > 0:
        return "spam"
    return "not spam"

for msg in ["claim a free prize", "win free cash", "free lunch tomorrow"]:
    print(msg, "| rule:", spam_by_rule(msg), "| learned:", spam_by_learning(msg))
