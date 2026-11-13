# 1.1 What machine learning is: learning from examples
# Example "measure_a_model" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# How good is a model? Compare its answers with the true answers.
true_marks = [12, 19, 31, 38, 52]
predicted = [9.6, 19.6, 29.6, 39.6, 49.6]

total = 0
for t, p in zip(true_marks, predicted):
    total = total + (t - p) ** 2
mse = total / len(true_marks)
print("mean squared error:", round(mse, 2))

true_labels = ["spam", "ham", "spam", "ham", "ham"]
guesses = ["spam", "ham", "ham", "ham", "spam"]
right = 0
for t, g in zip(true_labels, guesses):
    if t == g:
        right = right + 1
print("accuracy:", right, "of", len(true_labels), "=", right / len(true_labels))
