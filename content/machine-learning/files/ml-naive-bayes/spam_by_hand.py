# 2.3 Naive Bayes: classify by counting clues
# Example "spam_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

spam = ["win money now", "win a free prize", "free money offer", "claim your prize now"]
ham = ["meeting at noon", "lunch money for friday", "project meeting now", "see you at lunch"]

def count_words(messages):
    counts = {}
    total = 0
    for m in messages:
        for w in m.split():
            counts[w] = counts.get(w, 0) + 1
            total = total + 1
    return counts, total

spam_counts, spam_total = count_words(spam)
ham_counts, ham_total = count_words(ham)
vocab = set(spam_counts) | set(ham_counts)
v = len(vocab)
print("vocabulary size:", v, " words in spam:", spam_total, " words in ham:", ham_total)

def word_prob(word, counts, total):
    return (counts.get(word, 0) + 1) / (total + v)      # Laplace smoothing

new = "free money now"
p_spam = len(spam) / (len(spam) + len(ham))
p_ham = 1 - p_spam
for w in new.split():
    ps = word_prob(w, spam_counts, spam_total)
    ph = word_prob(w, ham_counts, ham_total)
    print("word", w.ljust(6), " P(w|spam)", round(ps, 4), " P(w|ham)", round(ph, 4))
    p_spam = p_spam * ps
    p_ham = p_ham * ph
print("P(spam | message) =", round(p_spam / (p_spam + p_ham), 4))
