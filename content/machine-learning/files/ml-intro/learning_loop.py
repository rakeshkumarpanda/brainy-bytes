# 1.1 What machine learning is: learning from examples
# Example "learning_loop" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Learn the rule "marks = w x hours" from examples, by guess, check, adjust, repeat
hours = [1, 2, 3, 4, 5]
marks = [12, 19, 31, 38, 52]

w = 2.0                  # a bad first guess
learning_rate = 0.02

for round_number in range(6):
    # 1. check: how wrong is the guess? (mean squared error)
    error = 0
    for h, m in zip(hours, marks):
        error = error + (w * h - m) ** 2
    error = error / len(hours)

    # 2. which way to move: the slope of the error
    slope = 0
    for h, m in zip(hours, marks):
        slope = slope + 2 * (w * h - m) * h
    slope = slope / len(hours)

    print("round", round_number, "w =", round(w, 2), "error =", round(error, 1))
    # 3. adjust the guess a little, against the slope
    w = w - learning_rate * slope

print("learned rule: marks =", round(w, 2), "x hours")
print("6 hours of study gives about", round(w * 6), "marks")
