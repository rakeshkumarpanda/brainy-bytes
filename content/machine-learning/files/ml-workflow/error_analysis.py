# 1.2 The machine learning project: from a question to a working model
# Example "error_analysis" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# After training, look at WHERE the model is wrong, not only how much
orders = [
    # distance, raining, true minutes, predicted minutes
    (2.0, 0, 16, 15),
    (5.0, 0, 27, 28),
    (3.0, 1, 30, 20),
    (6.0, 1, 45, 32),
    (1.0, 0, 11, 12),
    (4.0, 1, 36, 24),
]
dry_errors = []
rain_errors = []
for distance, raining, true_minutes, predicted in orders:
    error = abs(true_minutes - predicted)
    if raining:
        rain_errors.append(error)
    else:
        dry_errors.append(error)

print("average error when dry: ", round(sum(dry_errors) / len(dry_errors), 1), "minutes")
print("average error when rain:", round(sum(rain_errors) / len(rain_errors), 1), "minutes")
print("idea: add a 'raining' feature, the model does not know about rain yet")
