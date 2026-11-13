# 1.1 What machine learning is: learning from examples
# Example "memorise_or_learn" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Training data: hours studied -> passed (1) or failed (0)
train = [(1, 0), (2, 0), (3, 0), (5, 1), (6, 1), (8, 1)]
test = [(4, 1), (7, 1), (2.5, 0), (9, 1)]   # new students the model never saw

# Model A memorises: it stores the answers in a table
table_of_answers = {}
for h, passed in train:
    table_of_answers[h] = passed

def memoriser(h):
    return table_of_answers.get(h, "no idea")

# Model B learns a rule: pass when hours are at least a cut off
best_cut = None
best_correct = -1
for cut in [1, 2, 3, 4, 5, 6, 7, 8]:
    correct = 0
    for h, passed in train:
        guess = 1 if h >= cut else 0
        if guess == passed:
            correct = correct + 1
    if correct > best_correct:
        best_correct = correct
        best_cut = cut

def rule_learner(h):
    return 1 if h >= best_cut else 0

print("learned cut off:", best_cut, "hours")
for h, passed in test:
    print("hours", h, "true", passed, "| memoriser:", memoriser(h), "| rule:", rule_learner(h))
