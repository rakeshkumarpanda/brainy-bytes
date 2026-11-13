# 1.2 The machine learning project: from a question to a working model
# Example "leakage_demo" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.tree import DecisionTreeClassifier

# Predict if a loan will be repaid (1) or not (0).
# Columns: income_k, debt_k, late_fee_paid. The last one is filled in AFTER the loan ends!
X_train = [[30, 10, 0], [50, 5, 0], [20, 15, 1], [60, 2, 0], [25, 12, 1], [40, 8, 0], [35, 6, 1], [28, 9, 0]]
y_train = [1, 1, 0, 1, 0, 1, 0, 1]
X_test = [[45, 7, 0], [22, 14, 1], [33, 11, 1], [52, 3, 0]]     # old loans, so the column is filled in
y_test = [1, 0, 0, 1]

leaky = DecisionTreeClassifier(random_state=0).fit(X_train, y_train)
print("test accuracy with the leaky column:", leaky.score(X_test, y_test))

# Real use: a NEW applicant. Nobody has paid a late fee yet, so the column is always 0.
X_real = [[row[0], row[1], 0] for row in X_test]
print("accuracy on the same people at decision time:", leaky.score(X_real, y_test))

fair = DecisionTreeClassifier(random_state=0).fit([r[:2] for r in X_train], y_train)
print("fair model (income and debt only):", fair.score([r[:2] for r in X_test], y_test))
